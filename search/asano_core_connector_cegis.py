#!/usr/bin/env python3
"""Relation-first connector synthesis for the three-module Asano core.

Deleting the two separator hubs from the 26-vertex Asano graph leaves three
edge-deleted cubes and six degree-two ports.  Its exact six-terminal path-cover
language contains one state: all six terminals active, paired within the three
cube modules.  This script synthesizes a planar bipartite cubic connector whose
language avoids every pairing compatible with that state while the assembled
graph is simple, planar, bipartite, cubic, and 3-connected.

Topology, planarity, and connectivity are handled by counterexample-guided SAT.
Each compatible path-cover witness becomes a permanent edge-hitting clause.  A
zero-language assembly is sent directly to whole-graph CaDiCaL/DRAT proof.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

from exact_six_port_closure_search import (
    all_pairings,
    ce,
    exact_language,
    exact_path_cover_state,
    states_compatible,
)
from sat_verify_face_constraints import graph_validation, solve_case

Edge = tuple[int, int]


def build_asano_core() -> tuple[nx.Graph, list[int], dict[str, Any]]:
    """Return the hub-deleted three-module core and ordered ports L0,R0,... ."""
    graph = nx.Graph()
    ports: list[int] = []
    modules: list[dict[str, Any]] = []
    next_vertex = 0
    for module_index in range(3):
        left, right, a, b, c, d, e, f = range(next_vertex, next_vertex + 8)
        next_vertex += 8
        edges = [
            ce(left, a), ce(left, e), ce(right, b), ce(right, f),
            ce(a, b), ce(a, c), ce(e, f), ce(e, c),
            ce(c, d), ce(d, b), ce(d, f),
        ]
        graph.add_edges_from(edges)
        ports.extend([left, right])
        modules.append(
            {
                "module_index": module_index,
                "vertices": [left, right, a, b, c, d, e, f],
                "ports": [left, right],
                "edges": [list(edge) for edge in edges],
            }
        )
    return graph, ports, {
        "construction": "three disjoint edge-deleted cubes",
        "modules": modules,
        "ordered_ports": ports,
    }


def state_specs() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for active_size in (2, 4, 6):
        for active in itertools.combinations(range(6), active_size):
            for pairing in all_pairings(active):
                result.append(
                    {"active": list(active), "pairing": [list(pair) for pair in pairing]}
                )
    if len(result) != 75:
        raise ValueError(f"state-space mismatch: {len(result)}")
    return result


def fixed_color_map(source_colors: list[int], patch_colors: list[int]) -> tuple[int, ...]:
    mapping: list[int | None] = [None] * 6
    for color in (0, 1):
        source_indices = [index for index, value in enumerate(source_colors) if value == color]
        patch_indices = [index for index, value in enumerate(patch_colors) if value == 1 - color]
        if len(source_indices) != len(patch_indices):
            raise ValueError((source_colors, patch_colors))
        for source_index, patch_index in zip(source_indices, patch_indices, strict=True):
            mapping[source_index] = patch_index
    return tuple(int(value) for value in mapping)


def graph6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def edge_nogood(edges: Iterable[Edge], edge_var: dict[Edge, int]) -> list[int]:
    return [-edge_var[ce(*edge)] for edge in edges]


def obstruction_clause(
    obstruction: nx.Graph,
    edge_var: dict[Edge, int],
    patch_offset: int,
) -> list[int]:
    literals: set[int] = set()
    for left, right in obstruction.edges():
        patch_edge = ce(int(left) - patch_offset, int(right) - patch_offset)
        if patch_edge in edge_var:
            literals.add(-edge_var[patch_edge])
    return sorted(literals)


def separator_crossing_clause(
    side: set[int],
    separator: set[int],
    edge_var: dict[Edge, int],
    patch_offset: int,
) -> list[int]:
    literals: list[int] = []
    for edge, variable in edge_var.items():
        left, right = patch_offset + edge[0], patch_offset + edge[1]
        if left in separator or right in separator:
            continue
        if (left in side) != (right in side):
            literals.append(variable)
    return sorted(set(literals))


def add_lex_leq(
    clauses: list[list[int]],
    pool: IDPool,
    first: list[int],
    second: list[int],
    tag: str,
) -> None:
    previous: int | None = None
    for position, (left, right) in enumerate(zip(first, second, strict=True)):
        clauses.append([-left, right] if previous is None else [-previous, -left, right])
        equal = pool.id(f"lex:{tag}:{position}")
        if previous is None:
            clauses.extend(
                [[-equal, -left, right], [-equal, left, -right], [-left, -right, equal], [left, right, equal]]
            )
        else:
            clauses.extend(
                [
                    [-equal, previous],
                    [-equal, -left, right],
                    [-equal, left, -right],
                    [-previous, -left, -right, equal],
                    [-previous, left, right, equal],
                ]
            )
        previous = equal


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--patch-order", type=int, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--call-budget", type=int, default=10_000_000)
    parser.add_argument("--max-iterations", type=int, default=100_000)
    parser.add_argument("--wall-time", type=float, default=20_000.0)
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-rounds", type=int, default=100_000)
    parser.add_argument("--proof-timeout", type=float, default=3600.0)
    args = parser.parse_args()

    if args.patch_order < 6 or args.patch_order % 2:
        raise SystemExit("patch order must be even and at least six")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.output_dir / "checkpoint.json"
    started = time.time()
    counts: Counter[str] = Counter()
    incomplete: list[dict[str, Any]] = []
    final_candidate: dict[str, Any] | None = None
    best_record: dict[str, Any] | None = None
    best_compatibility: int | None = None
    learned_witnesses: set[tuple[int, ...]] = set()

    source_core, source_ports, construction = build_asano_core()
    if (
        source_core.number_of_nodes() != 24
        or source_core.number_of_edges() != 33
        or nx.number_connected_components(source_core) != 3
        or not nx.is_bipartite(source_core)
        or not nx.check_planarity(source_core)[0]
        or sorted(source_core.degree(vertex) for vertex in source_ports) != [2] * 6
        or any(source_core.degree(vertex) != 3 for vertex in source_core if vertex not in source_ports)
    ):
        raise SystemExit("Asano-core construction regression")

    source_language = exact_language(source_core, source_ports, args.call_budget)
    source_positive = [
        state for state in source_language if state["classification"] == "verified_positive"
    ]
    source_unknown = [state for state in source_language if state["classification"] == "unknown"]
    expected_state = {
        "active": [0, 1, 2, 3, 4, 5],
        "pairing": [[0, 1], [2, 3], [4, 5]],
    }
    if source_unknown or len(source_positive) != 1:
        raise SystemExit(
            f"Asano-core language regression: positive={len(source_positive)} unknown={len(source_unknown)}"
        )
    observed = {
        "active": source_positive[0]["active"],
        "pairing": source_positive[0]["pairing"],
    }
    if observed != expected_state:
        raise SystemExit(f"unexpected Asano-core state: {observed}")

    source_coloring = nx.bipartite.color(source_core)
    source_colors = [int(source_coloring[vertex]) for vertex in source_ports]
    half = args.patch_order // 2
    left = list(range(half))
    right = list(range(half, 2 * half))
    patch_ports = left[:3] + right[:3]
    patch_colors = [0, 0, 0, 1, 1, 1]
    mapping = fixed_color_map(source_colors, patch_colors)
    relevant_specs = [
        spec
        for spec in state_specs()
        if states_compatible(source_positive[0], spec, mapping)
    ]
    relevant_specs.sort(key=lambda spec: (spec["active"], spec["pairing"]))
    if len(relevant_specs) != 8 or any(len(spec["active"]) != 6 for spec in relevant_specs):
        raise SystemExit(f"compatible-state kernel regression: {len(relevant_specs)}")

    pool = IDPool()
    edge_var = {
        ce(left_vertex, right_vertex): pool.id(f"e:{left_vertex}:{right_vertex}")
        for left_vertex in left
        for right_vertex in right
    }
    clauses: list[list[int]] = []
    port_set = set(patch_ports)
    for vertex in left + right:
        incident = [variable for edge, variable in edge_var.items() if vertex in edge]
        target_degree = 2 if vertex in port_set else 3
        clauses.extend(
            CardEnc.equals(
                incident,
                target_degree,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    # Internal vertices of the same color are interchangeable.
    for first, second in zip(left[3:], left[4:]):
        add_lex_leq(
            clauses,
            pool,
            [edge_var[ce(first, vertex)] for vertex in reversed(right)],
            [edge_var[ce(second, vertex)] for vertex in reversed(right)],
            f"left:{first}:{second}",
        )
    for first, second in zip(right[3:], right[4:]):
        add_lex_leq(
            clauses,
            pool,
            [edge_var[ce(vertex, first)] for vertex in reversed(left)],
            [edge_var[ce(vertex, second)] for vertex in reversed(left)],
            f"right:{first}:{second}",
        )

    patch_offset = max(source_core.nodes()) + 1

    def checkpoint(iteration: int, status: str) -> None:
        save_json(
            checkpoint_path,
            {
                "campaign": "asano-core-connector-cegis",
                "status": status,
                "iteration": iteration,
                "patch_order": args.patch_order,
                "seed": args.seed,
                "mapping": list(mapping),
                "source_state": expected_state,
                "relevant_patch_states": relevant_specs,
                "counts": dict(counts),
                "learned_witnesses": len(learned_witnesses),
                "best_compatibility": best_compatibility,
                "best_record": best_record,
                "final_candidate": final_candidate,
                "incomplete": incomplete,
                "elapsed_s": time.time() - started,
            },
        )

    with Solver(name=args.solver, bootstrap_with=clauses) as solver:
        try:
            solver.set_phases(
                [
                    variable
                    if ((variable * 0x9E3779B1 + args.seed) & 1)
                    else -variable
                    for variable in edge_var.values()
                ]
            )
        except Exception:
            pass

        for iteration in range(1, args.max_iterations + 1):
            if time.time() - started > args.wall_time:
                counts["wall_time"] += 1
                checkpoint(iteration, "wall_time_exhausted")
                break
            if not solver.solve():
                counts["synthesis_unsat"] += 1
                checkpoint(iteration, "synthesis_unsat")
                break

            positive_model = {literal for literal in solver.get_model() if literal > 0}
            patch_edges = sorted(
                edge for edge, variable in edge_var.items() if variable in positive_model
            )
            patch = nx.Graph()
            patch.add_nodes_from(left + right)
            patch.add_edges_from(patch_edges)
            counts["sat_candidates"] += 1

            relabel = {vertex: patch_offset + vertex for vertex in patch}
            assembled = source_core.copy()
            assembled.add_edges_from(
                (relabel[first], relabel[second]) for first, second in patch.edges()
            )
            glue_edges: list[Edge] = []
            for source_index, patch_index in enumerate(mapping):
                edge = ce(source_ports[source_index], relabel[patch_ports[patch_index]])
                assembled.add_edge(*edge)
                glue_edges.append(edge)

            planar, obstruction = nx.check_planarity(assembled, counterexample=True)
            if not planar:
                clause = obstruction_clause(obstruction, edge_var, patch_offset)
                if not clause:
                    clause = edge_nogood(patch_edges, edge_var)
                solver.add_clause(clause)
                counts["assembled_nonplanar"] += 1
                continue

            connectivity = nx.node_connectivity(assembled)
            if connectivity < 3:
                separator = set(nx.minimum_node_cut(assembled))
                reduced = assembled.copy()
                reduced.remove_nodes_from(separator)
                added = 0
                for component in nx.connected_components(reduced):
                    clause = separator_crossing_clause(
                        set(component), separator, edge_var, patch_offset
                    )
                    if clause:
                        solver.add_clause(clause)
                        added += 1
                if not added:
                    solver.add_clause(edge_nogood(patch_edges, edge_var))
                    counts["separator_nogoods"] += 1
                counts[f"connectivity_{connectivity}"] += 1
                counts["separator_clauses"] += added
                continue

            checks = graph_validation(assembled)
            if not checks["barnette_predicates"]:
                incomplete.append(
                    {
                        "iteration": iteration,
                        "reason": "validation regression",
                        "checks": checks,
                    }
                )
                solver.add_clause(edge_nogood(patch_edges, edge_var))
                counts["validation_regression"] += 1
                checkpoint(iteration, "validation_regression")
                continue

            counts["structurally_valid"] += 1
            positive_states: list[dict[str, Any]] = []
            unknown_states: list[dict[str, Any]] = []
            new_witness_clauses: list[list[int]] = []
            for spec in relevant_specs:
                active = tuple(int(value) for value in spec["active"])
                pairing = tuple(
                    tuple(int(value) for value in pair) for pair in spec["pairing"]
                )
                result = exact_path_cover_state(
                    patch,
                    patch_ports,
                    active,
                    pairing,
                    args.call_budget,
                )
                if result["classification"] == "unknown":
                    unknown_states.append(result)
                    continue
                if result["classification"] != "verified_positive":
                    continue
                positive_states.append(result)
                clause = tuple(
                    sorted(
                        -edge_var[ce(int(edge[0]), int(edge[1]))]
                        for edge in result["witness"]
                    )
                )
                if clause not in learned_witnesses:
                    learned_witnesses.add(clause)
                    new_witness_clauses.append(list(clause))

            if unknown_states:
                incomplete.append(
                    {
                        "iteration": iteration,
                        "patch_graph6": graph6(patch),
                        "unknown_states": unknown_states,
                    }
                )
                solver.add_clause(edge_nogood(patch_edges, edge_var))
                counts["language_unknown"] += 1
                checkpoint(iteration, "language_unknown")
                continue

            compatibility = len(positive_states)
            if best_compatibility is None or compatibility < best_compatibility:
                best_compatibility = compatibility
                best_record = {
                    "iteration": iteration,
                    "patch_graph6": graph6(patch),
                    "patch_edges": [list(edge) for edge in patch_edges],
                    "compatible_states": compatibility,
                    "positive_state_records": positive_states,
                    "assembled_graph6": graph6(assembled),
                }
                checkpoint(iteration, "new_best")
                print(
                    json.dumps(
                        {
                            "iteration": iteration,
                            "patch_order": args.patch_order,
                            "seed": args.seed,
                            "new_best": compatibility,
                            "learned_witnesses": len(learned_witnesses),
                        }
                    ),
                    flush=True,
                )

            if compatibility:
                if new_witness_clauses:
                    for clause in new_witness_clauses:
                        solver.add_clause(clause)
                    counts["witness_clauses"] += len(new_witness_clauses)
                else:
                    solver.add_clause(edge_nogood(patch_edges, edge_var))
                    counts["duplicate_witness_nogoods"] += 1
                if iteration % 25 == 0:
                    checkpoint(iteration, "searching")
                continue

            candidate_graph6 = graph6(assembled)
            candidate_id = (
                f"asano-core-n{args.patch_order}-s{args.seed}-"
                f"{hashlib.sha256(candidate_graph6.encode('ascii')).hexdigest()[:12]}"
            )
            candidate_dir = args.output_dir / candidate_id
            candidate_dir.mkdir(parents=True, exist_ok=True)
            (candidate_dir / "candidate.g6").write_text(candidate_graph6 + "\n")
            (candidate_dir / "candidate_edges.json").write_text(
                json.dumps([list(ce(*edge)) for edge in sorted(assembled.edges())], indent=2)
            )
            proof_result = solve_case(
                assembled,
                {
                    "case_id": candidate_id + "-hamiltonicity",
                    "constraint_type": "whole_graph_hamiltonicity",
                    "include_edges": [],
                    "exclude_edges": [],
                },
                candidate_dir,
                args.solver,
                args.proof_solver,
                args.drat_trim,
                args.max_rounds,
                args.proof_timeout,
            )
            final_candidate = {
                "candidate_id": candidate_id,
                "patch_graph6": graph6(patch),
                "patch_edges": [list(edge) for edge in patch_edges],
                "mapping": list(mapping),
                "glue_edges": [list(edge) for edge in sorted(glue_edges)],
                "source_state": expected_state,
                "all_eight_compatible_patch_states_exact_negative": True,
                "candidate_graph6": candidate_graph6,
                "candidate_graph6_sha256": hashlib.sha256(
                    candidate_graph6.encode("ascii")
                ).hexdigest(),
                "graph_validation": checks,
                "whole_graph_result": proof_result,
            }
            if (
                proof_result["classification"] == "certified_negative"
                and proof_result.get("proof_verification", {}).get("verified", False)
            ):
                counts["certified_counterexample_candidates"] += 1
                checkpoint(iteration, "certified_counterexample_candidate")
                break
            if proof_result["classification"] == "verified_positive":
                checkpoint(iteration, "language_composition_contradiction")
                raise SystemExit("zero exact composition contradicted by Hamiltonian witness")
            incomplete.append(final_candidate)
            counts["whole_graph_unknown"] += 1
            checkpoint(iteration, "whole_graph_unknown")
            break
        else:
            counts["max_iterations"] += 1
            checkpoint(args.max_iterations, "max_iterations_exhausted")

    checkpoint_data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    status = checkpoint_data["status"]
    counterexample_found = bool(
        final_candidate
        and final_candidate.get("whole_graph_result", {}).get("classification")
        == "certified_negative"
        and final_candidate.get("whole_graph_result", {})
        .get("proof_verification", {})
        .get("verified", False)
    )
    summary = {
        "date_utc": "2026-08-03",
        "campaign": "asano-core-connector-cegis",
        "status": status,
        "patch_order": args.patch_order,
        "seed": args.seed,
        "source": {
            "construction": construction,
            "ports": source_ports,
            "port_colors": source_colors,
            "exact_positive_states": source_positive,
            "positive_state_count": 1,
            "unknown_state_count": 0,
        },
        "mapping": list(mapping),
        "relevant_patch_states": relevant_specs,
        "relevant_patch_state_count": len(relevant_specs),
        "candidate_edge_variables": len(edge_var),
        "target_patch_edges": (3 * args.patch_order - 6) // 2,
        "counts": dict(counts),
        "learned_witness_count": len(learned_witnesses),
        "best_compatibility": best_compatibility,
        "best_record": best_record,
        "final_candidate": final_candidate,
        "counterexample_found": counterexample_found,
        "incomplete": incomplete,
        "complete_classification": not incomplete
        and status in {"synthesis_unsat", "certified_counterexample_candidate"},
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
    }
    save_json(args.output_dir / "campaign_summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
