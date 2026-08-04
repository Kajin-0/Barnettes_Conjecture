#!/usr/bin/env python3
"""Convert canonical order-26 non-Hamiltonian bicubic planar seeds into six-port selectors.

The input is a plantri graph6 shard containing 2-connected planar bipartite
cubic graphs of order 26.  Hamiltonicity is decided exactly in memory.  Every
non-Hamiltonian seed is independently proof-certified, then every matching of
three seed edges is deleted.  The resulting six-port pole is glued to the exact
26-state candidate-489 source pole under every color-compatible terminal map.
Every simple cubic bipartite planar 3-connected zero-language assembly is sent
to whole-graph proof-producing SAT immediately.
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
from pysat.solvers import Solver

from exact_six_port_closure_search import (
    ce,
    color_compatible_maps,
    exact_language,
    states_compatible,
)
from sat_verify_face_constraints import (
    at_least_two,
    exactly_k_small,
    graph_validation,
    solve_case,
)

Edge = tuple[int, int]


def load_graph6(path: Path) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="ascii").splitlines():
        record = raw.strip()
        if not record or record.startswith(">>") or record in seen:
            continue
        seen.add(record)
        out.append(record)
    return out


def graph6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def exact_hamiltonian_cycle(
    graph: nx.Graph,
    solver_name: str,
    max_rounds: int,
) -> dict[str, Any]:
    """Exact lazy-subtour Hamiltonian decision with an explicit positive witness."""
    edges = sorted(ce(*edge) for edge in graph.edges())
    edge_var = {edge: index + 1 for index, edge in enumerate(edges)}
    clauses: list[list[int]] = []
    for vertex in graph:
        incident = [edge_var[ce(vertex, neighbor)] for neighbor in graph.neighbors(vertex)]
        clauses.extend(exactly_k_small(incident, 2))
    known: set[tuple[int, ...]] = set()
    added = 0
    started = time.time()
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        for round_index in range(1, max_rounds + 1):
            if not solver.solve():
                return {
                    "classification": "exact_negative",
                    "rounds": round_index,
                    "subtour_constraints": added,
                    "elapsed_s": time.time() - started,
                }
            positive = {literal for literal in solver.get_model() if literal > 0}
            selected = [edge for edge, variable in edge_var.items() if variable in positive]
            cover = nx.Graph()
            cover.add_nodes_from(graph)
            cover.add_edges_from(selected)
            if (
                len(selected) == graph.number_of_nodes()
                and all(cover.degree(vertex) == 2 for vertex in graph)
                and nx.is_connected(cover)
            ):
                return {
                    "classification": "verified_positive",
                    "rounds": round_index,
                    "subtour_constraints": added,
                    "elapsed_s": time.time() - started,
                    "witness": [list(edge) for edge in selected],
                }
            new_clauses: list[list[int]] = []
            for component in nx.connected_components(cover):
                if len(component) == graph.number_of_nodes():
                    continue
                crossing = tuple(
                    sorted(
                        edge_var[ce(u, v)]
                        for u in component
                        for v in graph.neighbors(u)
                        if v not in component
                    )
                )
                if crossing in known:
                    continue
                known.add(crossing)
                new_clauses.extend(at_least_two(crossing))
                added += 1
            if not new_clauses:
                return {
                    "classification": "unknown",
                    "reason": "no new subtour clause",
                    "rounds": round_index,
                    "elapsed_s": time.time() - started,
                }
            for clause in new_clauses:
                solver.add_clause(clause)
    return {
        "classification": "unknown",
        "reason": "maximum rounds reached",
        "rounds": max_rounds,
        "elapsed_s": time.time() - started,
    }


def three_edge_matchings(graph: nx.Graph) -> Iterable[tuple[Edge, Edge, Edge]]:
    edges = sorted(ce(*edge) for edge in graph.edges())
    for first_index, first in enumerate(edges):
        used_first = set(first)
        for second_index in range(first_index + 1, len(edges)):
            second = edges[second_index]
            if used_first & set(second):
                continue
            used_two = used_first | set(second)
            for third in edges[second_index + 1 :]:
                if used_two.isdisjoint(third):
                    yield first, second, third


def assembled_graph(
    source_core: nx.Graph,
    source_ports: list[int],
    patch: nx.Graph,
    patch_ports: list[int],
    mapping: tuple[int, ...],
) -> tuple[nx.Graph, list[Edge]]:
    offset = max(source_core.nodes()) + 1
    relabel = {vertex: offset + int(vertex) for vertex in patch}
    assembled = source_core.copy()
    assembled.add_edges_from((relabel[u], relabel[v]) for u, v in patch.edges())
    glue: list[Edge] = []
    for source_index, patch_index in enumerate(mapping):
        edge = ce(source_ports[source_index], relabel[patch_ports[patch_index]])
        assembled.add_edge(*edge)
        glue.append(edge)
    return assembled, sorted(glue)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--seed-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--call-budget", type=int, default=10_000_000)
    parser.add_argument("--max-rounds", type=int, default=100_000)
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--proof-timeout", type=float, default=3600.0)
    parser.add_argument("--wall-time", type=float, default=20_000.0)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    counts: Counter[str] = Counter()
    incomplete: list[dict[str, Any]] = []
    seed_records: list[dict[str, Any]] = []
    zero_records: list[dict[str, Any]] = []
    certified_candidates: list[dict[str, Any]] = []
    best_record: dict[str, Any] | None = None
    best_compatibility: int | None = None

    source_data = json.loads(args.source_input.read_text(encoding="utf-8"))
    source = nx.from_graph6_bytes(source_data["source"]["graph6"].encode("ascii"))
    source_checks = graph_validation(source)
    if not source_checks["barnette_predicates"]:
        raise SystemExit(f"source failed Barnette predicates: {source_checks}")
    removed_source = [ce(14, 18), ce(10, 17), ce(5, 11)]
    face = [int(value) for value in source_data["face"]["vertices_cyclic_order"]]
    terminal_set = {vertex for edge in removed_source for vertex in edge}
    source_ports = [vertex for vertex in face if vertex in terminal_set]
    source_core = source.copy()
    source_core.remove_edges_from(removed_source)
    source_language = exact_language(source_core, source_ports, args.call_budget)
    source_positive = [
        state for state in source_language if state["classification"] == "verified_positive"
    ]
    source_unknown = [state for state in source_language if state["classification"] == "unknown"]
    if len(source_positive) != 26 or source_unknown:
        raise SystemExit(
            f"source-language regression: positive={len(source_positive)} unknown={len(source_unknown)}"
        )
    source_coloring = nx.bipartite.color(source)
    source_colors = [int(source_coloring[vertex]) for vertex in source_ports]

    records = load_graph6(args.seed_input)
    checkpoint_path = args.output_dir / "checkpoint.json"

    def checkpoint(status: str) -> None:
        payload = {
            "campaign": "order26-obstruction-seed-six-port-search",
            "status": status,
            "counts": dict(counts),
            "seed_records": seed_records,
            "best_compatibility": best_compatibility,
            "best_record": best_record,
            "zero_records": zero_records,
            "certified_candidates": certified_candidates,
            "incomplete": incomplete,
            "elapsed_s": time.time() - started,
        }
        temporary = checkpoint_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(checkpoint_path)

    stop = False
    for record_index, record in enumerate(records):
        if time.time() - started > args.wall_time:
            counts["wall_time"] += 1
            checkpoint("wall_time_exhausted")
            break
        counts["input_records"] += 1
        try:
            seed = nx.from_graph6_bytes(record.encode("ascii"))
        except Exception as error:
            counts["malformed"] += 1
            incomplete.append({"record_index": record_index, "reason": str(error)})
            continue
        if (
            seed.number_of_nodes() != 26
            or seed.number_of_edges() != 39
            or not nx.is_connected(seed)
            or not nx.is_bipartite(seed)
            or not nx.check_planarity(seed)[0]
            or any(seed.degree(vertex) != 3 for vertex in seed)
            or nx.node_connectivity(seed) < 2
        ):
            counts["failed_seed_predicates"] += 1
            continue
        counts["accepted_seed_graphs"] += 1
        decision = exact_hamiltonian_cycle(seed, args.solver, args.max_rounds)
        if decision["classification"] == "unknown":
            counts["seed_unknown"] += 1
            incomplete.append(
                {"record_index": record_index, "seed_graph6": record, "decision": decision}
            )
            continue
        if decision["classification"] == "verified_positive":
            counts["hamiltonian_seeds"] += 1
            continue

        counts["nonhamiltonian_seeds"] += 1
        seed_id = f"seed-r{record_index:07d}-{sha_text(record)[:12]}"
        seed_dir = args.output_dir / seed_id
        seed_dir.mkdir(parents=True, exist_ok=True)
        seed_proof = solve_case(
            seed,
            {
                "case_id": seed_id + "-hamiltonicity",
                "constraint_type": "whole_graph_hamiltonicity",
                "include_edges": [],
                "exclude_edges": [],
            },
            seed_dir,
            args.solver,
            args.proof_solver,
            args.drat_trim,
            args.max_rounds,
            args.proof_timeout,
        )
        seed_info = {
            "record_index": record_index,
            "seed_id": seed_id,
            "graph6": record,
            "graph6_sha256": sha_text(record),
            "graph_validation": graph_validation(seed),
            "exact_decision": decision,
            "proof_result": seed_proof,
        }
        seed_records.append(seed_info)
        if not (
            seed_proof["classification"] == "certified_negative"
            and seed_proof.get("proof_verification", {}).get("verified", False)
        ):
            counts["seed_proof_incomplete"] += 1
            incomplete.append(seed_info)
            checkpoint("seed_proof_incomplete")
            continue
        counts["certified_nonhamiltonian_seeds"] += 1
        coloring = nx.bipartite.color(seed)

        for matching_index, removed in enumerate(three_edge_matchings(seed)):
            if time.time() - started > args.wall_time:
                counts["wall_time"] += 1
                checkpoint("wall_time_exhausted")
                stop = True
                break
            counts["edge_matchings"] += 1
            patch = seed.copy()
            patch.remove_edges_from(removed)
            patch_ports = sorted({vertex for edge in removed for vertex in edge})
            if len(patch_ports) != 6:
                raise SystemExit("matching produced non-six-port patch")
            if not nx.is_connected(patch):
                counts["disconnected_patches"] += 1
                continue
            patch_colors = [int(coloring[vertex]) for vertex in patch_ports]
            mappings = color_compatible_maps(source_colors, patch_colors)
            if not mappings:
                counts["color_incompatible_patches"] += 1
                continue

            structural: list[tuple[tuple[int, ...], nx.Graph, list[Edge], dict[str, Any]]] = []
            for mapping in mappings:
                assembled, glue = assembled_graph(
                    source_core, source_ports, patch, patch_ports, mapping
                )
                planar, _ = nx.check_planarity(assembled, counterexample=False)
                if not planar:
                    counts["nonplanar_maps"] += 1
                    continue
                if not nx.is_bipartite(assembled):
                    counts["nonbipartite_maps"] += 1
                    continue
                connectivity = nx.node_connectivity(assembled)
                if connectivity < 3:
                    counts[f"connectivity_{connectivity}_maps"] += 1
                    continue
                checks = graph_validation(assembled)
                if not checks["barnette_predicates"]:
                    counts["validation_regression"] += 1
                    incomplete.append(
                        {
                            "seed_id": seed_id,
                            "matching_index": matching_index,
                            "mapping": list(mapping),
                            "checks": checks,
                        }
                    )
                    continue
                structural.append((mapping, assembled, glue, checks))
            if not structural:
                continue
            counts["structurally_viable_patches"] += 1
            counts["structurally_viable_maps"] += len(structural)

            patch_language = exact_language(patch, patch_ports, args.call_budget)
            unknown_states = [
                state for state in patch_language if state["classification"] == "unknown"
            ]
            if unknown_states:
                counts["patch_language_unknown"] += 1
                incomplete.append(
                    {
                        "seed_id": seed_id,
                        "matching_index": matching_index,
                        "removed_edges": [list(edge) for edge in removed],
                        "unknown_states": unknown_states,
                    }
                )
                continue
            patch_positive = [
                state
                for state in patch_language
                if state["classification"] == "verified_positive"
            ]
            counts[f"patch_language_size_{len(patch_positive)}"] += 1

            for mapping, assembled, glue, checks in structural:
                compatibility = sum(
                    1
                    for source_state in source_positive
                    for patch_state in patch_positive
                    if states_compatible(source_state, patch_state, mapping)
                )
                counts["compatibility_maps"] += 1
                if best_compatibility is None or compatibility < best_compatibility:
                    best_compatibility = compatibility
                    best_record = {
                        "seed_id": seed_id,
                        "matching_index": matching_index,
                        "removed_edges": [list(edge) for edge in removed],
                        "patch_ports": patch_ports,
                        "mapping": list(mapping),
                        "patch_language_size": len(patch_positive),
                        "compatibility": compatibility,
                        "assembled_graph6": graph6(assembled),
                    }
                    checkpoint("new_best")
                    print(
                        json.dumps(
                            {
                                "seed_id": seed_id,
                                "matching_index": matching_index,
                                "new_best": compatibility,
                                "patch_language_size": len(patch_positive),
                            }
                        ),
                        flush=True,
                    )
                if compatibility != 0:
                    continue

                counts["zero_language_maps"] += 1
                candidate_g6 = graph6(assembled)
                candidate_id = (
                    f"asano26-m{matching_index:05d}-"
                    f"{sha_text(candidate_g6)[:12]}"
                )
                candidate_dir = args.output_dir / candidate_id
                candidate_dir.mkdir(parents=True, exist_ok=True)
                (candidate_dir / "candidate.g6").write_text(candidate_g6 + "\n")
                (candidate_dir / "candidate_edges.json").write_text(
                    json.dumps(
                        [list(ce(*edge)) for edge in sorted(assembled.edges())], indent=2
                    )
                )
                proof = solve_case(
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
                candidate = {
                    "candidate_id": candidate_id,
                    "seed_id": seed_id,
                    "removed_edges": [list(edge) for edge in removed],
                    "patch_ports": patch_ports,
                    "mapping": list(mapping),
                    "glue_edges": [list(edge) for edge in glue],
                    "patch_language_size": len(patch_positive),
                    "compatibility": 0,
                    "candidate_graph6": candidate_g6,
                    "candidate_graph6_sha256": sha_text(candidate_g6),
                    "graph_validation": checks,
                    "whole_graph_result": proof,
                }
                zero_records.append(candidate)
                if (
                    proof["classification"] == "certified_negative"
                    and proof.get("proof_verification", {}).get("verified", False)
                ):
                    counts["certified_counterexample_candidates"] += 1
                    certified_candidates.append(candidate)
                    checkpoint("certified_counterexample_candidate")
                    stop = True
                    break
                if proof["classification"] == "verified_positive":
                    checkpoint("language_composition_contradiction")
                    raise SystemExit("zero exact composition contradicted by Hamiltonian witness")
                counts["whole_graph_unknown"] += 1
                incomplete.append(candidate)
                checkpoint("whole_graph_unknown")
                stop = True
                break
            if stop:
                break
            if matching_index % 100 == 0:
                checkpoint("searching")
        if stop:
            break

    status = "certified_counterexample_candidate" if certified_candidates else "completed"
    if counts["wall_time"]:
        status = "wall_time_exhausted"
    elif incomplete:
        status = "incomplete"
    summary = {
        "date_utc": "2026-08-03",
        "campaign": "order26-obstruction-seed-six-port-search",
        "status": status,
        "source_positive_states": len(source_positive),
        "seed_input": str(args.seed_input),
        "seed_input_sha256": hashlib.sha256(args.seed_input.read_bytes()).hexdigest(),
        "counts": dict(counts),
        "seed_records": seed_records,
        "best_compatibility": best_compatibility,
        "best_record": best_record,
        "zero_records": zero_records,
        "certified_counterexample_candidates": certified_candidates,
        "counterexample_found": bool(certified_candidates),
        "incomplete": incomplete,
        "complete_classification": not incomplete and not counts["wall_time"],
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
    }
    (args.output_dir / "campaign_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    checkpoint(status)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
