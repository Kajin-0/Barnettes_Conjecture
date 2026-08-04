#!/usr/bin/env python3
"""Mine low-width Hamiltonian boundary clauses on large faces.

A counterexample must contain a face of size at least ten.  This scanner uses
the independent dual face-cut encoding to classify every partial inclusion
assignment of width one, two, and three on each sufficiently large face of a
Barnette graph.  It extracts prime forbidden patterns and proof-escalates the
most compact nontrivial ternary clauses.

The incremental SAT oracle is exact: every disconnected spanning 2-factor adds
a globally valid cut clause, and a positive is accepted only with an explicit
connected Hamiltonian cycle.  Solver-negative scan records are deliberately
labelled unproved until separately reproduced by CaDiCaL and checked by
``drat-trim``.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import time
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
from pysat.solvers import Solver

from dual_face_cut_obstruction import (
    build_dual,
    dual_validation,
    enumerate_faces,
    solve_case,
    validate_dual_witness,
    xor_equivalence,
)
from sat_verify_face_constraints import at_least_two, ce, exactly_k_small, graph_validation

Edge = tuple[int, int]


def cyclic_gap_signature(positions: tuple[int, ...], cycle_length: int) -> tuple[int, ...]:
    ordered = sorted(positions)
    gaps = [
        (ordered[(index + 1) % len(ordered)] - ordered[index]) % cycle_length
        for index in range(len(ordered))
    ]
    return tuple(sorted(gaps))


def cyclic_span(positions: tuple[int, ...], cycle_length: int) -> int:
    if len(positions) <= 1:
        return 0
    ordered = sorted(positions)
    gaps = [
        (ordered[(index + 1) % len(ordered)] - ordered[index]) % cycle_length
        for index in range(len(ordered))
    ]
    return cycle_length - max(gaps)


def pattern_key(positions: tuple[int, ...], bits: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(zip(positions, bits, strict=True)))


def is_prime_negative(
    key: tuple[tuple[int, int], ...],
    negative_keys: set[tuple[tuple[int, int], ...]],
) -> bool:
    if len(key) == 1:
        return True
    for size in range(1, len(key)):
        for subset in itertools.combinations(key, size):
            if tuple(sorted(subset)) in negative_keys:
                return False
    return True


class DualHamiltonianOracle:
    def __init__(
        self,
        primal: nx.Graph,
        dual: nx.Graph,
        edge_to_dual: dict[Edge, Edge],
        solver_name: str,
    ) -> None:
        self.primal = primal
        self.dual = dual
        self.edge_to_dual = edge_to_dual
        self.primal_edges = sorted(ce(int(left), int(right)) for left, right in primal.edges())
        next_variable = 1
        self.color_var: dict[int, int] = {}
        for face in sorted(dual):
            self.color_var[face] = next_variable
            next_variable += 1
        self.edge_var: dict[Edge, int] = {}
        for edge in self.primal_edges:
            self.edge_var[edge] = next_variable
            next_variable += 1

        self.clauses: list[list[int]] = [[-self.color_var[min(dual.nodes())]]]
        for primal_edge in self.primal_edges:
            left_face, right_face = edge_to_dual[primal_edge]
            self.clauses.extend(
                xor_equivalence(
                    self.edge_var[primal_edge],
                    self.color_var[left_face],
                    self.color_var[right_face],
                )
            )
        for vertex in primal:
            incident = [
                self.edge_var[ce(int(vertex), int(neighbor))]
                for neighbor in primal.neighbors(vertex)
            ]
            self.clauses.extend(exactly_k_small(incident, 2))

        self.solver = Solver(name=solver_name, bootstrap_with=self.clauses)
        self.known_crossing_sets: set[tuple[int, ...]] = set()
        self.added_subtour_constraints = 0
        self.solve_calls = 0
        self.sat_models = 0
        self.unsat_calls = 0
        self.cache: dict[tuple[tuple[Edge, int], ...], dict[str, Any]] = {}

    def close(self) -> None:
        self.solver.delete()

    def solve_pattern(
        self,
        assignments: tuple[tuple[Edge, int], ...],
        max_rounds: int,
    ) -> dict[str, Any]:
        canonical = tuple(sorted((ce(*edge), int(bit)) for edge, bit in assignments))
        if canonical in self.cache:
            return dict(self.cache[canonical])
        assumptions = [
            self.edge_var[edge] if bit else -self.edge_var[edge]
            for edge, bit in canonical
        ]
        include_edges = {edge for edge, bit in canonical if bit}
        exclude_edges = {edge for edge, bit in canonical if not bit}
        rounds = 0
        started = time.time()
        while rounds < max_rounds:
            rounds += 1
            self.solve_calls += 1
            if not self.solver.solve(assumptions=assumptions):
                self.unsat_calls += 1
                result = {
                    "classification": "solver_negative_unproved",
                    "rounds": rounds,
                    "elapsed_s": time.time() - started,
                }
                self.cache[canonical] = result
                return dict(result)

            self.sat_models += 1
            positive_model = {literal for literal in self.solver.get_model() if literal > 0}
            colors = {
                face: int(variable in positive_model)
                for face, variable in self.color_var.items()
            }
            selected = [
                edge for edge, variable in self.edge_var.items() if variable in positive_model
            ]
            validation = validate_dual_witness(
                self.primal,
                self.dual,
                self.edge_to_dual,
                colors,
                selected,
                include_edges,
                exclude_edges,
            )
            if validation["valid"]:
                result = {
                    "classification": "verified_positive",
                    "rounds": rounds,
                    "elapsed_s": time.time() - started,
                    "witness_cycle_sha256": hashlib.sha256(
                        json.dumps(sorted(selected)).encode("utf-8")
                    ).hexdigest(),
                }
                self.cache[canonical] = result
                return dict(result)

            selected_graph = nx.Graph()
            selected_graph.add_nodes_from(self.primal)
            selected_graph.add_edges_from(selected)
            new_clauses: list[list[int]] = []
            for component in nx.connected_components(selected_graph):
                if len(component) == self.primal.number_of_nodes():
                    continue
                crossing_vars = tuple(
                    sorted(
                        self.edge_var[ce(int(left), int(right))]
                        for left in component
                        for right in self.primal.neighbors(left)
                        if right not in component
                    )
                )
                if crossing_vars in self.known_crossing_sets:
                    continue
                self.known_crossing_sets.add(crossing_vars)
                new_clauses.extend(at_least_two(crossing_vars))
                self.added_subtour_constraints += 1
            if not new_clauses:
                result = {
                    "classification": "unknown",
                    "reason": "disconnected model produced no new valid cut",
                    "rounds": rounds,
                    "elapsed_s": time.time() - started,
                }
                self.cache[canonical] = result
                return dict(result)
            for clause in new_clauses:
                self.clauses.append(clause)
                self.solver.add_clause(clause)

        result = {
            "classification": "unknown",
            "reason": "maximum lazy-connectivity rounds reached",
            "rounds": rounds,
            "elapsed_s": time.time() - started,
        }
        self.cache[canonical] = result
        return dict(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--min-face-size", type=int, default=10)
    parser.add_argument("--max-width", type=int, default=3)
    parser.add_argument("--max-rounds", type=int, default=10000)
    parser.add_argument("--proof-limit", type=int, default=32)
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--proof-timeout", type=float, default=1800.0)
    args = parser.parse_args()

    if args.max_width < 1 or args.max_width > 3:
        raise SystemExit("max-width must be between one and three")

    source = json.loads(args.input.read_text(encoding="utf-8"))
    primal = nx.from_graph6_bytes(source["source"]["graph6"].encode("ascii"))
    primal_checks = graph_validation(primal)
    if not primal_checks["barnette_predicates"]:
        raise SystemExit(f"source failed Barnette predicates: {primal_checks}")
    _, faces, dart_face = enumerate_faces(primal)
    dual, edge_to_dual, vertex_faces = build_dual(primal, faces, dart_face)
    dual_checks = dual_validation(primal, dual, faces, vertex_faces)
    if not dual_checks["even_plane_triangulation"]:
        raise SystemExit(f"dual validation failed: {dual_checks}")

    target_faces = [
        (face_index, face)
        for face_index, face in enumerate(faces)
        if len(face) >= args.min_face_size
    ]
    if not target_faces:
        raise SystemExit("no face meets the requested minimum size")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    oracle = DualHamiltonianOracle(primal, dual, edge_to_dual, args.solver)
    started = time.time()
    face_reports: list[dict[str, Any]] = []
    all_prime_candidates: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []

    try:
        for face_index, face in target_faces:
            boundary_edges = [
                ce(int(face[position]), int(face[(position + 1) % len(face)]))
                for position in range(len(face))
            ]
            negative_keys: set[tuple[tuple[int, int], ...]] = set()
            records: list[dict[str, Any]] = []
            width_counts: dict[str, dict[str, int]] = {}
            for width in range(1, args.max_width + 1):
                counts: dict[str, int] = {}
                for positions in itertools.combinations(range(len(face)), width):
                    for bits in itertools.product((0, 1), repeat=width):
                        assignments = tuple(
                            (boundary_edges[position], bit)
                            for position, bit in zip(positions, bits, strict=True)
                        )
                        result = oracle.solve_pattern(assignments, args.max_rounds)
                        classification = str(result["classification"])
                        counts[classification] = counts.get(classification, 0) + 1
                        key = pattern_key(positions, bits)
                        if classification == "solver_negative_unproved":
                            negative_keys.add(key)
                        elif classification == "unknown":
                            incomplete.append(
                                {
                                    "face_index": face_index,
                                    "positions": list(positions),
                                    "bits": list(bits),
                                    "result": result,
                                }
                            )
                        records.append(
                            {
                                "width": width,
                                "positions": list(positions),
                                "bits": list(bits),
                                "classification": classification,
                                "rounds": result.get("rounds"),
                                "witness_cycle_sha256": result.get("witness_cycle_sha256"),
                            }
                        )
                width_counts[str(width)] = counts
                print(
                    json.dumps(
                        {
                            "face_index": face_index,
                            "face_size": len(face),
                            "width": width,
                            "counts": counts,
                            "global_cuts": oracle.added_subtour_constraints,
                        }
                    ),
                    flush=True,
                )

            prime_records: list[dict[str, Any]] = []
            for key in sorted(negative_keys, key=lambda value: (len(value), value)):
                if not is_prime_negative(key, negative_keys):
                    continue
                positions = tuple(position for position, _ in key)
                bits = tuple(bit for _, bit in key)
                record = {
                    "face_index": face_index,
                    "face_size": len(face),
                    "face_vertices_cyclic_order": list(face),
                    "positions": list(positions),
                    "bits": list(bits),
                    "edges": [list(boundary_edges[position]) for position in positions],
                    "width": len(key),
                    "cyclic_span": cyclic_span(positions, len(face)),
                    "cyclic_gap_signature": list(cyclic_gap_signature(positions, len(face))),
                    "nontrivial_ternary": len(key) == 3,
                }
                prime_records.append(record)
                all_prime_candidates.append(record)

            face_report = {
                "face_index": face_index,
                "face_size": len(face),
                "vertices_cyclic_order": list(face),
                "boundary_edges_cyclic_order": [list(edge) for edge in boundary_edges],
                "width_classification_counts": width_counts,
                "prime_negative_count": len(prime_records),
                "prime_negative_patterns": prime_records,
                "all_pattern_records": records,
            }
            face_reports.append(face_report)
            (args.output_dir / f"face_{face_index}_scan.json").write_text(
                json.dumps(face_report, indent=2), encoding="utf-8"
            )
    finally:
        oracle.close()

    proof_candidates = sorted(
        (
            candidate
            for candidate in all_prime_candidates
            if candidate["width"] == 3
        ),
        key=lambda candidate: (
            candidate["cyclic_span"],
            candidate["face_size"],
            candidate["cyclic_gap_signature"],
            candidate["face_index"],
            candidate["positions"],
            candidate["bits"],
        ),
    )[: args.proof_limit]

    certified_results: list[dict[str, Any]] = []
    face_edges = {
        face_index: [
            ce(int(face[position]), int(face[(position + 1) % len(face)]))
            for position in range(len(face))
        ]
        for face_index, face in target_faces
    }
    for rank, candidate in enumerate(proof_candidates, 1):
        edges = face_edges[candidate["face_index"]]
        include_edges = [
            edges[position]
            for position, bit in zip(candidate["positions"], candidate["bits"], strict=True)
            if bit
        ]
        exclude_edges = [
            edges[position]
            for position, bit in zip(candidate["positions"], candidate["bits"], strict=True)
            if not bit
        ]
        case = {
            "case_id": (
                f"face{candidate['face_index']}-prime3-r{rank}-"
                + "-".join(
                    f"{position}{bit}"
                    for position, bit in zip(candidate["positions"], candidate["bits"], strict=True)
                )
            ),
            "include_edges": [list(edge) for edge in include_edges],
            "exclude_edges": [list(edge) for edge in exclude_edges],
        }
        result = solve_case(
            primal,
            dual,
            edge_to_dual,
            case,
            args.output_dir / "proofs",
            args.solver,
            args.proof_solver,
            args.drat_trim,
            args.max_rounds,
            args.proof_timeout,
        )
        certified_results.append({"candidate": candidate, "proof_result": result})
        print(
            json.dumps(
                {
                    "proof_rank": rank,
                    "case_id": case["case_id"],
                    "classification": result["classification"],
                }
            ),
            flush=True,
        )

    summary = {
        "date_utc": "2026-08-04",
        "campaign": "dual-large-face-prime-implicate-scan",
        "primal_validation": primal_checks,
        "dual_validation": dual_checks,
        "minimum_face_size": args.min_face_size,
        "maximum_width": args.max_width,
        "faces_scanned": len(face_reports),
        "face_sizes_scanned": sorted(len(face) for _, face in target_faces),
        "prime_negative_patterns": len(all_prime_candidates),
        "prime_ternary_patterns": sum(
            candidate["width"] == 3 for candidate in all_prime_candidates
        ),
        "proof_candidates_attempted": len(certified_results),
        "proof_candidates_certified": sum(
            item["proof_result"]["classification"] == "certified_negative"
            for item in certified_results
        ),
        "remaining_unknown": len(incomplete),
        "incremental_oracle": {
            "solve_calls": oracle.solve_calls,
            "sat_models": oracle.sat_models,
            "unsat_calls": oracle.unsat_calls,
            "globally_valid_subtour_constraints": oracle.added_subtour_constraints,
            "cached_patterns": len(oracle.cache),
        },
        "counterexample_found": False,
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
    }
    output = {
        "summary": summary,
        "faces": face_reports,
        "proof_results": certified_results,
        "incomplete": incomplete,
    }
    (args.output_dir / "dual_face_implicate_summary.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
