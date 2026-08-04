#!/usr/bin/env python3
"""Search embedded even-triangulated disk substitutions for candidate 489.

The distinguished 12-face of candidate 489 corresponds to a degree-12 vertex
in its simple even plane-triangulation dual.  Removing that dual vertex leaves
a 12-cycle boundary.  This program reads canonical plantri triangulations of a
12-disk, glues each disk into that hole under every dihedral boundary map, and
retains only closures that are simple even 4-connected triangulations.

Each retained dual is converted back to its cubic bipartite planar primal.
Hamiltonicity is screened exactly by a primal spanning-2-factor SAT oracle with
valid lazy connectivity cuts.  Every provisional negative is immediately
escalated through two independent proof-producing formulations:

1. primal selected-edge Hamiltonicity;
2. dual face-color cut / two induced trees.

A candidate is reported only when both CaDiCaL proofs are accepted by
``drat-trim`` and every Barnette predicate is independently checked.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import re
import time
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
from pysat.solvers import Solver

from dual_face_cut_obstruction import (
    build_dual,
    cyclic_equal,
    dual_validation,
    enumerate_faces,
    solve_case as solve_dual_case,
)
from sat_verify_face_constraints import (
    at_least_two,
    ce,
    exactly_k_small,
    graph_validation,
    solve_case as solve_primal_case,
)

Edge = tuple[int, int]


def parse_plantri_ascii(line: str) -> tuple[nx.Graph, dict[int, list[int]]]:
    raw = line.strip()
    if not raw:
        raise ValueError("empty plantri record")
    fields = raw.split(maxsplit=1)
    if len(fields) != 2:
        raise ValueError(f"malformed plantri ascii record: {raw[:120]}")
    order = int(fields[0])
    sections = fields[1].split(",")
    if len(sections) != order:
        raise ValueError(f"adjacency-section count {len(sections)} != order {order}")
    if order > 26:
        raise ValueError("this parser currently supports plantri ascii orders at most 26")

    rotations: dict[int, list[int]] = {}
    graph = nx.Graph()
    graph.add_nodes_from(range(order))
    for vertex, section in enumerate(sections):
        neighbors = [ord(character) - ord("a") for character in section]
        if any(neighbor < 0 or neighbor >= order for neighbor in neighbors):
            raise ValueError(f"neighbor outside range at vertex {vertex}: {neighbors}")
        if len(neighbors) != len(set(neighbors)):
            raise ValueError(f"duplicate neighbor at vertex {vertex}: {neighbors}")
        rotations[vertex] = neighbors
        for neighbor in neighbors:
            graph.add_edge(vertex, neighbor)

    for left, right in graph.edges():
        if left not in rotations[right] or right not in rotations[left]:
            raise ValueError(f"asymmetric adjacency for edge {(left, right)}")
    return graph, rotations


def rotation_faces(rotations: dict[int, list[int]]) -> list[list[int]]:
    """Enumerate faces from clockwise rotations using predecessor traversal."""
    seen: set[tuple[int, int]] = set()
    faces: list[list[int]] = []
    for left in sorted(rotations):
        for right in rotations[left]:
            if (left, right) in seen:
                continue
            start = (left, right)
            dart = start
            face: list[int] = []
            while True:
                u, v = dart
                if dart in seen and dart != start:
                    raise ValueError("face traversal entered a previously used dart")
                seen.add(dart)
                face.append(u)
                neighbors = rotations[v]
                position = neighbors.index(u)
                w = neighbors[(position - 1) % len(neighbors)]
                dart = (v, w)
                if dart == start:
                    break
                if len(face) > 4 * len(rotations):
                    raise ValueError("face traversal failed to close")
            faces.append(face)
    expected_darts = sum(len(neighbors) for neighbors in rotations.values())
    if len(seen) != expected_darts:
        raise ValueError("not all darts were assigned to faces")
    return faces


def validate_disk(
    graph: nx.Graph,
    rotations: dict[int, list[int]],
    boundary_size: int,
) -> dict[str, Any]:
    faces = rotation_faces(rotations)
    outer_candidates = [face for face in faces if len(face) == boundary_size]
    triangular_faces = [face for face in faces if len(face) == 3]
    checks: dict[str, Any] = {
        "order": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "simple": not graph.is_multigraph() and nx.number_of_selfloops(graph) == 0,
        "connected": nx.is_connected(graph),
        "faces": len(faces),
        "outer_face_candidates": len(outer_candidates),
        "triangular_inner_faces": len(triangular_faces),
        "expected_inner_faces": len(faces) - 1,
    }
    if len(outer_candidates) != 1:
        checks["valid_disk"] = False
        checks["reason"] = "outer face was not uniquely identified"
        return {"checks": checks, "faces": faces, "boundary": None}
    boundary = outer_candidates[0]
    checks["boundary_is_simple_cycle"] = len(boundary) == len(set(boundary))
    checks["all_other_faces_triangles"] = len(triangular_faces) == len(faces) - 1
    boundary_set = set(boundary)
    internal = sorted(set(graph) - boundary_set)
    checks["internal_vertices"] = len(internal)
    checks["boundary_degrees_odd"] = all(graph.degree(vertex) % 2 == 1 for vertex in boundary)
    checks["internal_degrees_even"] = all(graph.degree(vertex) % 2 == 0 for vertex in internal)
    checks["internal_minimum_degree_four"] = all(graph.degree(vertex) >= 4 for vertex in internal)
    checks["valid_disk"] = all(
        (
            checks["simple"],
            checks["connected"],
            checks["boundary_is_simple_cycle"],
            checks["all_other_faces_triangles"],
            checks["boundary_degrees_odd"],
            checks["internal_degrees_even"],
            checks["internal_minimum_degree_four"],
        )
    )
    return {"checks": checks, "faces": faces, "boundary": boundary}


def dihedral_maps(size: int) -> list[tuple[int, ...]]:
    maps: list[tuple[int, ...]] = []
    for direction in (1, -1):
        for offset in range(size):
            maps.append(tuple((offset + direction * index) % size for index in range(size)))
    return maps


def source_dual_context(source: dict[str, Any]) -> dict[str, Any]:
    primal = nx.from_graph6_bytes(source["source"]["graph6"].encode("ascii"))
    primal_checks = graph_validation(primal)
    if not primal_checks["barnette_predicates"]:
        raise ValueError(f"source failed Barnette predicates: {primal_checks}")
    _, faces, dart_face = enumerate_faces(primal)
    dual, edge_to_dual, vertex_faces = build_dual(primal, faces, dart_face)
    dual_checks = dual_validation(primal, dual, faces, vertex_faces)
    if not dual_checks["even_plane_triangulation"]:
        raise ValueError(f"source dual validation failed: {dual_checks}")

    target_cycle = [int(value) for value in source["face"]["vertices_cyclic_order"]]
    target_faces = [index for index, face in enumerate(faces) if cyclic_equal(face, target_cycle)]
    if len(target_faces) != 1:
        raise ValueError(f"expected one target face, found {target_faces}")
    target = target_faces[0]

    boundary_neighbors: list[int] = []
    for raw_edge in source["face"]["edges_cyclic_order"]:
        edge = ce(int(raw_edge[0]), int(raw_edge[1]))
        dual_edge = edge_to_dual[edge]
        if target not in dual_edge:
            raise ValueError(f"target face not incident with source boundary edge {edge}")
        neighbor = dual_edge[1] if dual_edge[0] == target else dual_edge[0]
        boundary_neighbors.append(neighbor)
    if len(boundary_neighbors) != len(set(boundary_neighbors)):
        raise ValueError(f"target dual neighbors are not distinct: {boundary_neighbors}")
    for index, left in enumerate(boundary_neighbors):
        right = boundary_neighbors[(index + 1) % len(boundary_neighbors)]
        if not dual.has_edge(left, right):
            raise ValueError(f"dual neighbor cycle edge absent: {(left, right)}")

    outside = dual.copy()
    outside.remove_node(target)
    return {
        "primal": primal,
        "primal_checks": primal_checks,
        "dual": dual,
        "dual_checks": dual_checks,
        "target": target,
        "outside": outside,
        "boundary_neighbors": boundary_neighbors,
    }


def assemble_dual(
    outside: nx.Graph,
    outside_boundary: list[int],
    disk: nx.Graph,
    disk_boundary: list[int],
    mapping: tuple[int, ...],
) -> nx.Graph:
    if len(outside_boundary) != len(disk_boundary) or len(mapping) != len(disk_boundary):
        raise ValueError("boundary-size mismatch")
    boundary_assignment = {
        disk_boundary[index]: outside_boundary[mapping[index]]
        for index in range(len(disk_boundary))
    }
    next_vertex = max(outside.nodes(), default=-1) + 1
    relabel: dict[int, int] = dict(boundary_assignment)
    for vertex in sorted(set(disk) - set(disk_boundary)):
        relabel[vertex] = next_vertex
        next_vertex += 1

    assembled = outside.copy()
    for left, right in disk.edges():
        mapped = ce(relabel[int(left)], relabel[int(right)])
        assembled.add_edge(*mapped)
    return assembled


def primal_from_triangulation(
    triangulation: nx.Graph,
) -> tuple[nx.Graph, dict[Edge, Edge], dict[str, Any]]:
    _, faces, dart_face = enumerate_faces(triangulation)
    if not all(len(face) == 3 for face in faces):
        raise ValueError("assembled dual has a nontriangular face")
    primal = nx.Graph()
    primal.add_nodes_from(range(len(faces)))
    primal_edge_to_dual: dict[Edge, Edge] = {}
    parallel = False
    for left, right in triangulation.edges():
        face_left = dart_face[(int(left), int(right))]
        face_right = dart_face[(int(right), int(left))]
        primal_edge = ce(face_left, face_right)
        dual_edge = ce(int(left), int(right))
        if primal.has_edge(*primal_edge):
            parallel = True
        primal.add_edge(*primal_edge)
        primal_edge_to_dual[primal_edge] = dual_edge
    checks = {
        "triangulation_vertices": triangulation.number_of_nodes(),
        "triangulation_edges": triangulation.number_of_edges(),
        "triangulation_faces": len(faces),
        "all_faces_triangles": True,
        "parallel_primal_edges_detected": parallel,
    }
    return primal, primal_edge_to_dual, checks


def quick_hamiltonicity(
    graph: nx.Graph,
    solver_name: str,
    max_rounds: int,
) -> dict[str, Any]:
    edges = sorted(ce(int(left), int(right)) for left, right in graph.edges())
    edge_var = {edge: index + 1 for index, edge in enumerate(edges)}
    clauses: list[list[int]] = []
    for vertex in graph:
        incident = [edge_var[ce(int(vertex), int(neighbor))] for neighbor in graph.neighbors(vertex)]
        clauses.extend(exactly_k_small(incident, 2))
    known_crossings: set[tuple[int, ...]] = set()
    rounds = 0
    started = time.time()
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        while rounds < max_rounds:
            rounds += 1
            if not solver.solve():
                return {
                    "classification": "exact_negative_unproved",
                    "rounds": rounds,
                    "clauses": len(clauses),
                    "elapsed_s": time.time() - started,
                }
            positive = {literal for literal in solver.get_model() if literal > 0}
            selected = [edge for edge, variable in edge_var.items() if variable in positive]
            cycle = nx.Graph()
            cycle.add_nodes_from(graph)
            cycle.add_edges_from(selected)
            if (
                len(selected) == graph.number_of_nodes()
                and all(cycle.degree(vertex) == 2 for vertex in graph)
                and nx.is_connected(cycle)
            ):
                return {
                    "classification": "verified_positive",
                    "rounds": rounds,
                    "clauses": len(clauses),
                    "elapsed_s": time.time() - started,
                    "cycle_edges": [list(edge) for edge in selected],
                    "cycle_sha256": hashlib.sha256(
                        json.dumps([list(edge) for edge in selected], sort_keys=True).encode("utf-8")
                    ).hexdigest(),
                }
            new_clauses: list[list[int]] = []
            for component in nx.connected_components(cycle):
                if len(component) == graph.number_of_nodes():
                    continue
                crossing = tuple(
                    sorted(
                        edge_var[ce(int(left), int(right))]
                        for left in component
                        for right in graph.neighbors(left)
                        if right not in component
                    )
                )
                if crossing in known_crossings:
                    continue
                known_crossings.add(crossing)
                new_clauses.extend(at_least_two(crossing))
            if not new_clauses:
                return {
                    "classification": "unknown",
                    "reason": "disconnected model produced no new cut",
                    "rounds": rounds,
                    "elapsed_s": time.time() - started,
                }
            for clause in new_clauses:
                clauses.append(clause)
                solver.add_clause(clause)
    return {
        "classification": "unknown",
        "reason": "maximum lazy-connectivity rounds reached",
        "rounds": rounds,
        "elapsed_s": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--disk-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-order", type=int, required=True)
    parser.add_argument("--boundary-size", type=int, default=12)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--max-rounds", type=int, default=10000)
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--proof-timeout", type=float, default=3600.0)
    parser.add_argument("--stop-after-certified", action="store_true")
    args = parser.parse_args()

    source = json.loads(args.source_input.read_text(encoding="utf-8"))
    context = source_dual_context(source)
    if len(context["boundary_neighbors"]) != args.boundary_size:
        raise SystemExit("source boundary size does not match requested disk size")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = [line for line in args.disk_input.read_text(encoding="ascii").splitlines() if line.strip()]
    started = time.time()
    counts: dict[str, int] = {}
    structural_records: list[dict[str, Any]] = []
    unknown_records: list[dict[str, Any]] = []
    certified_candidates: list[dict[str, Any]] = []
    seen_dual_graph6: set[str] = set()
    best_hamiltonian_rounds: list[dict[str, Any]] = []

    def increment(key: str, amount: int = 1) -> None:
        counts[key] = counts.get(key, 0) + amount

    for record_index, line in enumerate(records):
        increment("plantri_records")
        try:
            disk, rotations = parse_plantri_ascii(line)
            if disk.number_of_nodes() != args.expected_order:
                increment("wrong_order")
                continue
            disk_result = validate_disk(disk, rotations, args.boundary_size)
        except Exception as error:
            increment("malformed_records")
            unknown_records.append({"record_index": record_index, "reason": str(error)})
            continue
        if not disk_result["checks"]["valid_disk"]:
            increment("parity_or_disk_rejected")
            continue
        increment("parity_valid_disks")
        disk_boundary = [int(value) for value in disk_result["boundary"]]

        for map_index, mapping in enumerate(dihedral_maps(args.boundary_size)):
            increment("dihedral_maps_attempted")
            assembled_dual = assemble_dual(
                context["outside"],
                context["boundary_neighbors"],
                disk,
                disk_boundary,
                mapping,
            )
            dual_graph6 = nx.to_graph6_bytes(assembled_dual, header=False).decode("ascii").strip()
            if dual_graph6 in seen_dual_graph6:
                increment("duplicate_dual_assemblies")
                continue
            seen_dual_graph6.add(dual_graph6)
            increment("unique_dual_assemblies")

            planar, _ = nx.check_planarity(assembled_dual)
            if not planar:
                increment("nonplanar_assemblies")
                continue
            if not all(degree % 2 == 0 for _, degree in assembled_dual.degree()):
                increment("non_eulerian_assemblies")
                continue
            expected_edges = 3 * assembled_dual.number_of_nodes() - 6
            if assembled_dual.number_of_edges() != expected_edges:
                increment("non_triangulation_edge_count")
                continue
            dual_connectivity = nx.node_connectivity(assembled_dual)
            if dual_connectivity < 4:
                increment("dual_connectivity_below_four")
                continue

            try:
                primal, primal_edge_to_dual, dualization_checks = primal_from_triangulation(
                    assembled_dual
                )
            except Exception as error:
                increment("dualization_failures")
                unknown_records.append(
                    {
                        "record_index": record_index,
                        "map_index": map_index,
                        "reason": str(error),
                    }
                )
                continue
            primal_checks = graph_validation(primal)
            if not primal_checks["barnette_predicates"]:
                increment("failed_barnette_predicates")
                structural_records.append(
                    {
                        "record_index": record_index,
                        "map_index": map_index,
                        "dual_graph6": dual_graph6,
                        "dual_connectivity": dual_connectivity,
                        "dualization_checks": dualization_checks,
                        "primal_validation": primal_checks,
                    }
                )
                continue
            increment("barnette_assemblies")
            primal_graph6 = nx.to_graph6_bytes(primal, header=False).decode("ascii").strip()
            quick = quick_hamiltonicity(primal, args.solver, args.max_rounds)
            if quick["classification"] == "verified_positive":
                increment("verified_hamiltonian")
                best_hamiltonian_rounds.append(
                    {
                        "record_index": record_index,
                        "map_index": map_index,
                        "primal_order": primal.number_of_nodes(),
                        "rounds": quick["rounds"],
                        "cycle_sha256": quick["cycle_sha256"],
                        "primal_graph6_sha256": hashlib.sha256(
                            primal_graph6.encode("ascii")
                        ).hexdigest(),
                    }
                )
                continue
            if quick["classification"] != "exact_negative_unproved":
                increment("hamiltonicity_unknown")
                unknown_records.append(
                    {
                        "record_index": record_index,
                        "map_index": map_index,
                        "primal_graph6": primal_graph6,
                        "quick_result": quick,
                    }
                )
                continue

            increment("provisional_nonhamiltonian")
            candidate_hash = hashlib.sha256(primal_graph6.encode("ascii")).hexdigest()
            candidate_id = (
                f"dual-disk-n{args.expected_order}-r{record_index:08d}-"
                f"m{map_index:02d}-{candidate_hash[:12]}"
            )
            candidate_dir = args.output_dir / candidate_id
            primal_proof = solve_primal_case(
                primal,
                {
                    "case_id": candidate_id + "-primal",
                    "include_edges": [],
                    "exclude_edges": [],
                },
                candidate_dir / "primal-proof",
                args.solver,
                args.proof_solver,
                args.drat_trim,
                args.max_rounds,
                args.proof_timeout,
            )
            dual_proof = solve_dual_case(
                primal,
                assembled_dual,
                primal_edge_to_dual,
                {
                    "case_id": candidate_id + "-dual",
                    "include_edges": [],
                    "exclude_edges": [],
                },
                candidate_dir / "dual-proof",
                args.solver,
                args.proof_solver,
                args.drat_trim,
                args.max_rounds,
                args.proof_timeout,
            )
            candidate = {
                "candidate_id": candidate_id,
                "disk_record_index": record_index,
                "dihedral_map_index": map_index,
                "dihedral_mapping": list(mapping),
                "disk_ascii_sha256": hashlib.sha256(line.encode("ascii")).hexdigest(),
                "disk_validation": disk_result["checks"],
                "dual_graph6": dual_graph6,
                "dual_graph6_sha256": hashlib.sha256(dual_graph6.encode("ascii")).hexdigest(),
                "dual_order": assembled_dual.number_of_nodes(),
                "dual_connectivity": dual_connectivity,
                "primal_graph6": primal_graph6,
                "primal_graph6_sha256": candidate_hash,
                "primal_validation": primal_checks,
                "quick_result": quick,
                "primal_proof": primal_proof,
                "dual_proof": dual_proof,
            }
            candidate["certified_counterexample"] = all(
                (
                    primal_proof.get("classification") == "certified_negative",
                    primal_proof.get("proof_verification", {}).get("verified", False),
                    dual_proof.get("classification") == "certified_negative",
                    dual_proof.get("proof_verification", {}).get("verified", False),
                    primal_checks["barnette_predicates"],
                    dual_connectivity >= 4,
                )
            )
            if candidate["certified_counterexample"]:
                increment("certified_counterexamples")
                certified_candidates.append(candidate)
                (candidate_dir / "candidate.json").write_text(
                    json.dumps(candidate, indent=2), encoding="utf-8"
                )
                if args.stop_after_certified:
                    break
            else:
                increment("proof_escalation_not_certified")
                unknown_records.append(candidate)
        if certified_candidates and args.stop_after_certified:
            break
        if (record_index + 1) % 1000 == 0:
            print(
                json.dumps(
                    {
                        "processed_records": record_index + 1,
                        "counts": counts,
                        "certified_counterexamples": len(certified_candidates),
                    }
                ),
                flush=True,
            )

    best_hamiltonian_rounds.sort(key=lambda item: (-item["rounds"], item["primal_graph6_sha256"]))
    summary = {
        "date_utc": "2026-08-04",
        "campaign": "dual-disk-substitution-search",
        "expected_disk_order": args.expected_order,
        "boundary_size": args.boundary_size,
        "source": {
            "primal_validation": context["primal_checks"],
            "dual_validation": context["dual_checks"],
            "removed_dual_vertex": context["target"],
            "boundary_neighbors_cyclic_order": context["boundary_neighbors"],
        },
        "counts": counts,
        "unique_dual_assemblies": len(seen_dual_graph6),
        "certified_counterexamples": certified_candidates,
        "counterexample_found": bool(certified_candidates),
        "unknown_records": unknown_records,
        "complete_classification": not unknown_records,
        "hardest_hamiltonian_witnesses": best_hamiltonian_rounds[:100],
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
    }
    (args.output_dir / "dual_disk_substitution_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
