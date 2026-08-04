#!/usr/bin/env python3
"""Independent dual face-cut encoding for Barnette Hamiltonicity.

For a fixed plane embedding of a cubic graph G, a Hamiltonian cycle separates
faces into two classes.  A primal edge is selected exactly when its two incident
faces receive different colors.  Conversely, a face 2-coloring whose
bichromatic primal edges form a connected spanning 2-factor is a Hamiltonian
cycle.

This program constructs the planar dual of canonical candidate 489, encodes
Hamiltonicity with face-color variables plus edge-XOR variables, and verifies:

* all eight inclusion patterns on the principal facial triple;
* every previously certified H^{+--} obstruction in the source JSON;
* the induced-tree dual certificate for every positive witness.

Connectivity is imposed by valid lazy cut clauses.  A negative is called
certified only when an external CaDiCaL run emits a textual DRAT proof and
``drat-trim`` accepts it.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
from pysat.solvers import Solver

from sat_verify_face_constraints import (
    at_least_two,
    ce,
    exactly_k_small,
    graph_validation,
    run_process,
    sha256_file,
    write_dimacs,
)

Edge = tuple[int, int]


def cyclic_equal(left: list[int], right: list[int]) -> bool:
    if len(left) != len(right):
        return False
    n = len(left)
    for sequence in (left, list(reversed(left))):
        for offset in range(n):
            if sequence[offset:] + sequence[:offset] == right:
                return True
    return False


def enumerate_faces(graph: nx.Graph) -> tuple[nx.PlanarEmbedding, list[list[int]], dict[tuple[int, int], int]]:
    planar, embedding = nx.check_planarity(graph)
    if not planar:
        raise ValueError("input graph is not planar")
    seen: set[tuple[int, int]] = set()
    faces: list[list[int]] = []
    dart_face: dict[tuple[int, int], int] = {}
    for vertex in embedding:
        for neighbor in embedding.neighbors_cw_order(vertex):
            if (vertex, neighbor) in seen:
                continue
            face = embedding.traverse_face(vertex, neighbor, seen)
            face_index = len(faces)
            faces.append([int(value) for value in face])
            for index, left in enumerate(face):
                right = face[(index + 1) % len(face)]
                dart_face[(int(left), int(right))] = face_index
    if len(dart_face) != 2 * graph.number_of_edges():
        raise ValueError("directed-edge to face map is incomplete")
    return embedding, faces, dart_face


def build_dual(
    graph: nx.Graph,
    faces: list[list[int]],
    dart_face: dict[tuple[int, int], int],
) -> tuple[nx.Graph, dict[Edge, Edge], dict[int, tuple[int, int, int]]]:
    dual = nx.Graph()
    dual.add_nodes_from(range(len(faces)))
    edge_to_dual: dict[Edge, Edge] = {}
    for left, right in graph.edges():
        primal_edge = ce(int(left), int(right))
        face_left = dart_face[(int(left), int(right))]
        face_right = dart_face[(int(right), int(left))]
        if face_left == face_right:
            raise ValueError(f"bridge or one-sided edge encountered: {primal_edge}")
        dual_edge = ce(face_left, face_right)
        if dual.has_edge(*dual_edge):
            raise ValueError(f"parallel dual edge encountered: {dual_edge}")
        dual.add_edge(*dual_edge, primal_edge=primal_edge)
        edge_to_dual[primal_edge] = dual_edge

    vertex_faces: dict[int, tuple[int, int, int]] = {}
    for vertex in graph:
        incident_faces = {
            dart_face[(int(vertex), int(neighbor))]
            for neighbor in graph.neighbors(vertex)
        }
        if len(incident_faces) != 3:
            raise ValueError(
                f"primal vertex {vertex} is not incident with three distinct faces: {incident_faces}"
            )
        vertex_faces[int(vertex)] = tuple(sorted(incident_faces))
    return dual, edge_to_dual, vertex_faces


def dual_validation(
    primal: nx.Graph,
    dual: nx.Graph,
    faces: list[list[int]],
    vertex_faces: dict[int, tuple[int, int, int]],
) -> dict[str, Any]:
    planar, _ = nx.check_planarity(dual)
    triangles_valid = all(
        dual.has_edge(face_tuple[index], face_tuple[(index + 1) % 3])
        for face_tuple in vertex_faces.values()
        for index in range(3)
    )
    checks: dict[str, Any] = {
        "primal_vertices": primal.number_of_nodes(),
        "primal_edges": primal.number_of_edges(),
        "dual_vertices": dual.number_of_nodes(),
        "dual_edges": dual.number_of_edges(),
        "euler_face_count": primal.number_of_edges() - primal.number_of_nodes() + 2,
        "simple": not dual.is_multigraph() and nx.number_of_selfloops(dual) == 0,
        "connected": nx.is_connected(dual),
        "planar": planar,
        "all_degrees_even": all(degree % 2 == 0 for _, degree in dual.degree()),
        "every_primal_vertex_dual_triangle": triangles_valid,
        "node_connectivity": nx.node_connectivity(dual) if nx.is_connected(dual) else 0,
        "face_size_multiset": sorted(len(face) for face in faces),
        "dual_degree_multiset": sorted(degree for _, degree in dual.degree()),
    }
    checks["even_plane_triangulation"] = all(
        (
            checks["dual_vertices"] == checks["euler_face_count"],
            checks["simple"],
            checks["connected"],
            checks["planar"],
            checks["all_degrees_even"],
            checks["every_primal_vertex_dual_triangle"],
        )
    )
    return checks


def xor_equivalence(output: int, left: int, right: int) -> list[list[int]]:
    """CNF for output <-> (left XOR right)."""
    return [
        [left, right, -output],
        [-left, -right, -output],
        [left, -right, output],
        [-left, right, output],
    ]


def validate_dual_witness(
    primal: nx.Graph,
    dual: nx.Graph,
    edge_to_dual: dict[Edge, Edge],
    colors: dict[int, int],
    selected_edges: list[Edge],
    include_edges: set[Edge],
    exclude_edges: set[Edge],
) -> dict[str, Any]:
    selected_set = {ce(*edge) for edge in selected_edges}
    expected_selected = {
        primal_edge
        for primal_edge, (left_face, right_face) in edge_to_dual.items()
        if colors[left_face] != colors[right_face]
    }
    cycle = nx.Graph()
    cycle.add_nodes_from(primal)
    cycle.add_edges_from(selected_set)

    color_tree_checks: dict[str, Any] = {}
    trees_valid = True
    for color in (0, 1):
        vertices = [vertex for vertex, value in colors.items() if value == color]
        induced = dual.subgraph(vertices)
        connected = bool(vertices) and nx.is_connected(induced)
        edge_count = induced.number_of_edges()
        expected_edges = len(vertices) - 1
        tree = connected and edge_count == expected_edges
        trees_valid = trees_valid and tree
        color_tree_checks[str(color)] = {
            "vertices": len(vertices),
            "edges": edge_count,
            "connected": connected,
            "expected_tree_edges": expected_edges,
            "tree": tree,
        }

    checks: dict[str, Any] = {
        "selected_equals_dual_cut": selected_set == expected_selected,
        "selected_edge_count": len(selected_set),
        "expected_edge_count": primal.number_of_nodes(),
        "degree_two": all(cycle.degree(vertex) == 2 for vertex in primal),
        "connected": nx.is_connected(cycle),
        "includes_required": include_edges <= selected_set,
        "avoids_excluded": selected_set.isdisjoint(exclude_edges),
        "dual_color_classes": color_tree_checks,
        "dual_induced_trees": trees_valid,
    }
    checks["valid"] = all(
        (
            checks["selected_equals_dual_cut"],
            checks["selected_edge_count"] == checks["expected_edge_count"],
            checks["degree_two"],
            checks["connected"],
            checks["includes_required"],
            checks["avoids_excluded"],
            checks["dual_induced_trees"],
        )
    )
    return checks


def solve_case(
    primal: nx.Graph,
    dual: nx.Graph,
    edge_to_dual: dict[Edge, Edge],
    case: dict[str, Any],
    output_dir: Path,
    solver_name: str,
    proof_solver: str | None,
    drat_trim: str | None,
    max_rounds: int,
    proof_timeout: float,
) -> dict[str, Any]:
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(case["case_id"]))
    case_dir = output_dir / safe_id
    case_dir.mkdir(parents=True, exist_ok=True)

    include_edges = {ce(int(edge[0]), int(edge[1])) for edge in case.get("include_edges", [])}
    exclude_edges = {ce(int(edge[0]), int(edge[1])) for edge in case.get("exclude_edges", [])}
    primal_edges = sorted(ce(int(left), int(right)) for left, right in primal.edges())
    primal_edge_set = set(primal_edges)
    malformed: list[str] = []
    if not include_edges <= primal_edge_set:
        malformed.append("required edge absent from graph")
    if not exclude_edges <= primal_edge_set:
        malformed.append("excluded edge absent from graph")
    if include_edges & exclude_edges:
        malformed.append("same edge both included and excluded")
    if malformed:
        return {
            "case_id": case["case_id"],
            "classification": "malformed",
            "reasons": malformed,
        }

    next_variable = 1
    color_var: dict[int, int] = {}
    for face in sorted(dual):
        color_var[face] = next_variable
        next_variable += 1
    edge_var: dict[Edge, int] = {}
    for edge in primal_edges:
        edge_var[edge] = next_variable
        next_variable += 1

    clauses: list[list[int]] = []
    clauses.append([-color_var[min(dual.nodes())]])
    for primal_edge in primal_edges:
        left_face, right_face = edge_to_dual[primal_edge]
        clauses.extend(
            xor_equivalence(
                edge_var[primal_edge],
                color_var[left_face],
                color_var[right_face],
            )
        )
    for vertex in primal:
        incident = [edge_var[ce(int(vertex), int(neighbor))] for neighbor in primal.neighbors(vertex)]
        clauses.extend(exactly_k_small(incident, 2))
    clauses.extend([[edge_var[edge]] for edge in sorted(include_edges)])
    clauses.extend([[-edge_var[edge]] for edge in sorted(exclude_edges)])

    started = time.time()
    rounds = 0
    added_subtour_constraints = 0
    known_crossing_sets: set[tuple[int, ...]] = set()
    outcome: dict[str, Any]

    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        while rounds < max_rounds:
            rounds += 1
            if not solver.solve():
                cnf_path = case_dir / "final.cnf"
                proof_path = case_dir / "final.drat"
                dimacs = write_dimacs(cnf_path, clauses)
                if proof_path.exists():
                    proof_path.unlink()

                proof_generation: dict[str, Any] = {
                    "attempted": bool(proof_solver),
                    "unsat_exit_code": False,
                    "proof_bytes": 0,
                }
                if proof_solver:
                    proof_generation.update(
                        run_process(
                            [proof_solver, "--no-binary", str(cnf_path), str(proof_path)],
                            proof_timeout,
                        )
                    )
                    proof_generation["unsat_exit_code"] = proof_generation.get("returncode") == 20
                    proof_generation["proof_bytes"] = proof_path.stat().st_size if proof_path.exists() else 0

                proof_verification: dict[str, Any] = {
                    "attempted": bool(drat_trim),
                    "verified": False,
                }
                if (
                    drat_trim
                    and proof_path.exists()
                    and proof_path.stat().st_size > 0
                    and proof_generation.get("unsat_exit_code")
                ):
                    proof_verification.update(
                        run_process([drat_trim, str(cnf_path), str(proof_path)], proof_timeout)
                    )
                    proof_verification["verified"] = proof_verification.get("returncode") == 0

                classification = (
                    "certified_negative" if proof_verification["verified"] else "provisional_negative"
                )
                outcome = {
                    "case_id": case["case_id"],
                    "classification": classification,
                    "include_edges": [list(edge) for edge in sorted(include_edges)],
                    "exclude_edges": [list(edge) for edge in sorted(exclude_edges)],
                    "rounds": rounds,
                    "added_subtour_constraints": added_subtour_constraints,
                    "dimacs": dimacs,
                    "cnf_path": str(cnf_path),
                    "cnf_sha256": sha256_file(cnf_path),
                    "proof_path": str(proof_path),
                    "proof_sha256": sha256_file(proof_path) if proof_path.exists() else None,
                    "proof_generation": proof_generation,
                    "proof_verification": proof_verification,
                }
                break

            positive_model = {literal for literal in solver.get_model() if literal > 0}
            colors = {
                face: int(variable in positive_model)
                for face, variable in color_var.items()
            }
            selected = [
                edge for edge, variable in edge_var.items() if variable in positive_model
            ]
            validation = validate_dual_witness(
                primal,
                dual,
                edge_to_dual,
                colors,
                selected,
                include_edges,
                exclude_edges,
            )
            if validation["valid"]:
                witness_path = case_dir / "dual_tree_coloring_and_hamiltonian_cycle.json"
                witness = {
                    "case_id": case["case_id"],
                    "face_colors": {str(face): color for face, color in sorted(colors.items())},
                    "selected_edges": [list(edge) for edge in selected],
                    "validation": validation,
                }
                witness_path.write_text(json.dumps(witness, indent=2), encoding="utf-8")
                outcome = {
                    "case_id": case["case_id"],
                    "classification": "verified_positive",
                    "include_edges": [list(edge) for edge in sorted(include_edges)],
                    "exclude_edges": [list(edge) for edge in sorted(exclude_edges)],
                    "rounds": rounds,
                    "added_subtour_constraints": added_subtour_constraints,
                    "witness_path": str(witness_path),
                    "witness_sha256": sha256_file(witness_path),
                    "witness_validation": validation,
                }
                break

            selected_graph = nx.Graph()
            selected_graph.add_nodes_from(primal)
            selected_graph.add_edges_from(selected)
            components = list(nx.connected_components(selected_graph))
            new_clauses: list[list[int]] = []
            for component in components:
                if len(component) == primal.number_of_nodes():
                    continue
                crossing_vars = tuple(
                    sorted(
                        edge_var[ce(int(left), int(right))]
                        for left in component
                        for right in primal.neighbors(left)
                        if right not in component
                    )
                )
                if crossing_vars in known_crossing_sets:
                    continue
                known_crossing_sets.add(crossing_vars)
                new_clauses.extend(at_least_two(crossing_vars))
                added_subtour_constraints += 1
            if not new_clauses:
                outcome = {
                    "case_id": case["case_id"],
                    "classification": "unknown",
                    "reason": "disconnected model produced no new valid cut",
                    "rounds": rounds,
                    "witness_validation": validation,
                }
                break
            for clause in new_clauses:
                clauses.append(clause)
                solver.add_clause(clause)
        else:
            outcome = {
                "case_id": case["case_id"],
                "classification": "unknown",
                "reason": "maximum lazy-connectivity rounds reached",
                "rounds": rounds,
                "added_subtour_constraints": added_subtour_constraints,
            }

    outcome["elapsed_s"] = time.time() - started
    (case_dir / "result.json").write_text(json.dumps(outcome, indent=2), encoding="utf-8")
    return outcome


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-rounds", type=int, default=10000)
    parser.add_argument("--proof-timeout", type=float, default=900.0)
    args = parser.parse_args()

    source = json.loads(args.input.read_text(encoding="utf-8"))
    primal = nx.from_graph6_bytes(source["source"]["graph6"].encode("ascii"))
    primal_checks = graph_validation(primal)
    if not primal_checks["barnette_predicates"]:
        raise SystemExit(f"source graph failed Barnette predicates: {primal_checks}")

    _, faces, dart_face = enumerate_faces(primal)
    dual, edge_to_dual, vertex_faces = build_dual(primal, faces, dart_face)
    dual_checks = dual_validation(primal, dual, faces, vertex_faces)
    if not dual_checks["even_plane_triangulation"]:
        raise SystemExit(f"dual validation failed: {dual_checks}")

    requested_face = [int(value) for value in source["face"]["vertices_cyclic_order"]]
    matching_faces = [index for index, face in enumerate(faces) if cyclic_equal(face, requested_face)]
    if len(matching_faces) != 1:
        raise SystemExit(f"expected one matching source face, found {matching_faces}")
    source_face_index = matching_faces[0]

    boundary_map: list[dict[str, Any]] = []
    for face_edge in source["face"]["edges_cyclic_order"]:
        edge = ce(int(face_edge[0]), int(face_edge[1]))
        dual_edge = edge_to_dual[edge]
        if source_face_index not in dual_edge:
            raise SystemExit(f"source face is not incident with boundary edge {edge}: {dual_edge}")
        neighbor = dual_edge[1] if dual_edge[0] == source_face_index else dual_edge[0]
        boundary_map.append(
            {
                "primal_edge": list(edge),
                "dual_face_vertex": source_face_index,
                "dual_neighbor": neighbor,
            }
        )

    principal_edges = [ce(14, 18), ce(10, 17), ce(5, 11)]
    principal_cases: list[dict[str, Any]] = []
    for bits in itertools.product((0, 1), repeat=3):
        include = [principal_edges[index] for index, bit in enumerate(bits) if bit]
        exclude = [principal_edges[index] for index, bit in enumerate(bits) if not bit]
        principal_cases.append(
            {
                "case_id": "principal-pattern-" + "".join(str(bit) for bit in bits),
                "pattern": list(bits),
                "include_edges": [list(edge) for edge in include],
                "exclude_edges": [list(edge) for edge in exclude],
            }
        )

    source_cases = [
        {
            "case_id": "source-certified-" + str(case["case_id"]),
            "source_case_id": case["case_id"],
            "include_edges": case.get("include_edges", []),
            "exclude_edges": case.get("exclude_edges", []),
        }
        for case in source.get("cases", [])
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    principal_results: list[dict[str, Any]] = []
    source_results: list[dict[str, Any]] = []
    for group_name, cases, destination in (
        ("principal", principal_cases, principal_results),
        ("source", source_cases, source_results),
    ):
        for index, case in enumerate(cases, 1):
            print(json.dumps({"group": group_name, "case": index, "id": case["case_id"]}), flush=True)
            result = solve_case(
                primal,
                dual,
                edge_to_dual,
                case,
                args.output_dir / group_name,
                args.solver,
                args.proof_solver,
                args.drat_trim,
                args.max_rounds,
                args.proof_timeout,
            )
            if "pattern" in case:
                result["pattern"] = case["pattern"]
            if "source_case_id" in case:
                result["source_case_id"] = case["source_case_id"]
            destination.append(result)
            print(
                json.dumps(
                    {
                        "id": case["case_id"],
                        "classification": result["classification"],
                        "rounds": result.get("rounds"),
                    }
                ),
                flush=True,
            )

    def counts(results: Iterable[dict[str, Any]]) -> dict[str, int]:
        output: dict[str, int] = {}
        for result in results:
            key = str(result["classification"])
            output[key] = output.get(key, 0) + 1
        return output

    principal_counts = counts(principal_results)
    source_counts = counts(source_results)
    summary = {
        "date_utc": "2026-08-04",
        "campaign": "dual-face-cut-obstruction",
        "primal_validation": primal_checks,
        "dual_validation": dual_checks,
        "source_face": {
            "input_face_index": source["face"].get("face_index"),
            "embedding_face_index": source_face_index,
            "vertices_cyclic_order": requested_face,
            "boundary_map": boundary_map,
            "dual_degree": dual.degree(source_face_index),
        },
        "principal_edges": [list(edge) for edge in principal_edges],
        "principal_patterns_attempted": len(principal_results),
        "principal_classification_counts": principal_counts,
        "principal_certified_negative_patterns": [
            result["pattern"]
            for result in principal_results
            if result["classification"] == "certified_negative"
        ],
        "source_cases_attempted": len(source_results),
        "source_classification_counts": source_counts,
        "source_cases_all_independently_certified": (
            len(source_results) == len(source_cases)
            and all(result["classification"] == "certified_negative" for result in source_results)
        ),
        "remaining_unknown_or_provisional": sum(
            1
            for result in principal_results + source_results
            if result["classification"] not in ("verified_positive", "certified_negative")
        ),
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
        "principal_results": principal_results,
        "source_results": source_results,
    }
    summary_path = args.output_dir / "dual_face_cut_summary.json"
    summary_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
