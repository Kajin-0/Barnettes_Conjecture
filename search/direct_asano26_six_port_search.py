#!/usr/bin/env python3
"""Direct exact six-port extraction search from the 26-vertex Asano graph.

The seed is constructed internally as three copies of a cube with one edge
removed, joined between two degree-three hub vertices.  This produces the
26-vertex cubic bipartite planar non-Hamiltonian graph.  Every matching of
three seed edges is assigned to one deterministic residue shard.  Deleting the
matching exposes six degree-two ports.  Every color-compatible gluing to the
candidate-489 exact six-pole is filtered for planarity and 3-connectivity.

Boundary states are then decided lazily and exactly.  A map is rejected as soon
as one compatible path-cover witness is found.  A map survives only if every
patch state compatible with one of the source's 26 positive states is exactly
negative.  Such a zero-language Barnette assembly is sent immediately to the
whole-graph CaDiCaL/DRAT pipeline.
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

from exact_six_port_closure_search import (
    all_pairings,
    ce,
    color_compatible_maps,
    exact_language,
    exact_path_cover_state,
    states_compatible,
)
from sat_verify_face_constraints import graph_validation, solve_case

Edge = tuple[int, int]


def build_asano26() -> tuple[nx.Graph, dict[str, Any]]:
    """Construct the 26-vertex graph from three identical edge-deleted cubes."""
    graph = nx.Graph()
    left_hub, right_hub = 0, 1
    next_vertex = 2
    modules: list[dict[str, Any]] = []
    for module_index in range(3):
        left, right, a, b, c, d, e, f = range(next_vertex, next_vertex + 8)
        next_vertex += 8
        internal_edges = [
            ce(left, a),
            ce(left, e),
            ce(right, b),
            ce(right, f),
            ce(a, b),
            ce(a, c),
            ce(e, f),
            ce(e, c),
            ce(c, d),
            ce(d, b),
            ce(d, f),
        ]
        hub_edges = [ce(left_hub, left), ce(right_hub, right)]
        graph.add_edges_from(internal_edges + hub_edges)
        modules.append(
            {
                "module_index": module_index,
                "vertices": [left, right, a, b, c, d, e, f],
                "internal_edges": [list(edge) for edge in internal_edges],
                "hub_edges": [list(edge) for edge in hub_edges],
            }
        )
    manifest = {
        "construction": "three edge-deleted cubes between two degree-three hubs",
        "hubs": [left_hub, right_hub],
        "modules": modules,
    }
    return graph, manifest


def graph6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def all_state_specs() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for active_size in (2, 4, 6):
        for active in itertools.combinations(range(6), active_size):
            for pairing in all_pairings(active):
                result.append(
                    {
                        "active": list(active),
                        "pairing": [list(pair) for pair in pairing],
                    }
                )
    if len(result) != 75:
        raise ValueError(f"six-port state-space mismatch: {len(result)}")
    return result


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


def assemble(
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
    glue_edges: list[Edge] = []
    for source_index, patch_index in enumerate(mapping):
        edge = ce(source_ports[source_index], relabel[patch_ports[patch_index]])
        assembled.add_edge(*edge)
        glue_edges.append(edge)
    return assembled, sorted(glue_edges)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--matching-residue", type=int, required=True)
    parser.add_argument("--matching-modulus", type=int, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--call-budget", type=int, default=10_000_000)
    parser.add_argument("--max-rounds", type=int, default=100_000)
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--proof-timeout", type=float, default=3600.0)
    parser.add_argument("--wall-time", type=float, default=20_000.0)
    args = parser.parse_args()

    if args.matching_modulus <= 0:
        raise SystemExit("matching modulus must be positive")
    if not 0 <= args.matching_residue < args.matching_modulus:
        raise SystemExit("matching residue outside modulus")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.output_dir / "checkpoint.json"
    started = time.time()
    counts: Counter[str] = Counter()
    incomplete: list[dict[str, Any]] = []
    zero_records: list[dict[str, Any]] = []
    certified_candidates: list[dict[str, Any]] = []
    best_record: dict[str, Any] | None = None
    best_first_witness_rank: int | None = None

    seed, construction_manifest = build_asano26()
    seed_validation = graph_validation(seed)
    seed_graph6 = graph6(seed)
    if not all(
        (
            seed_validation["simple"],
            seed_validation["connected"],
            seed_validation["cubic"],
            seed_validation["bipartite"],
            seed_validation["planar"],
            seed_validation["node_connectivity"] == 2,
            seed.number_of_nodes() == 26,
            seed.number_of_edges() == 39,
        )
    ):
        raise SystemExit(f"Asano-26 construction regression: {seed_validation}")

    seed_proof_dir = args.output_dir / "asano26-seed-proof"
    seed_proof = solve_case(
        seed,
        {
            "case_id": "asano26-seed-hamiltonicity",
            "constraint_type": "whole_graph_hamiltonicity",
            "include_edges": [],
            "exclude_edges": [],
        },
        seed_proof_dir,
        args.solver,
        args.proof_solver,
        args.drat_trim,
        args.max_rounds,
        args.proof_timeout,
    )
    seed_certified = (
        seed_proof["classification"] == "certified_negative"
        and seed_proof.get("proof_verification", {}).get("verified", False)
    )
    if not seed_certified:
        incomplete.append({"reason": "seed proof incomplete", "seed_proof": seed_proof})
        save_json(
            checkpoint_path,
            {
                "campaign": "direct-asano26-six-port-search",
                "status": "seed_proof_incomplete",
                "seed_validation": seed_validation,
                "seed_proof": seed_proof,
                "incomplete": incomplete,
            },
        )
        raise SystemExit("Asano-26 seed lacks a checked non-Hamiltonicity proof")

    source_data = json.loads(args.source_input.read_text(encoding="utf-8"))
    source = nx.from_graph6_bytes(source_data["source"]["graph6"].encode("ascii"))
    source_validation = graph_validation(source)
    if not source_validation["barnette_predicates"]:
        raise SystemExit(f"source failed Barnette predicates: {source_validation}")
    removed_source = [ce(14, 18), ce(10, 17), ce(5, 11)]
    face = [int(value) for value in source_data["face"]["vertices_cyclic_order"]]
    source_terminal_set = {vertex for edge in removed_source for vertex in edge}
    source_ports = [vertex for vertex in face if vertex in source_terminal_set]
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
    seed_coloring = nx.bipartite.color(seed)
    state_specs = all_state_specs()

    def checkpoint(status: str, matching_index: int | None = None) -> None:
        save_json(
            checkpoint_path,
            {
                "campaign": "direct-asano26-six-port-search",
                "status": status,
                "matching_residue": args.matching_residue,
                "matching_modulus": args.matching_modulus,
                "matching_index": matching_index,
                "seed_graph6": seed_graph6,
                "seed_graph6_sha256": sha256_text(seed_graph6),
                "seed_validation": seed_validation,
                "seed_proof": seed_proof,
                "counts": dict(counts),
                "best_first_witness_rank": best_first_witness_rank,
                "best_record": best_record,
                "zero_records": zero_records,
                "certified_candidates": certified_candidates,
                "incomplete": incomplete,
                "elapsed_s": time.time() - started,
            },
        )

    stop = False
    total_matchings = 0
    assigned_matchings = 0
    for matching_index, removed in enumerate(three_edge_matchings(seed)):
        total_matchings += 1
        if matching_index % args.matching_modulus != args.matching_residue:
            continue
        assigned_matchings += 1
        counts["assigned_matchings"] += 1
        if time.time() - started > args.wall_time:
            counts["wall_time"] += 1
            checkpoint("wall_time_exhausted", matching_index)
            break

        patch = seed.copy()
        patch.remove_edges_from(removed)
        patch_ports = sorted({vertex for edge in removed for vertex in edge})
        if len(patch_ports) != 6:
            raise SystemExit("three-edge matching did not expose six distinct ports")
        if not nx.is_connected(patch):
            counts["disconnected_patches"] += 1
            continue
        patch_colors = [int(seed_coloring[vertex]) for vertex in patch_ports]
        mappings = color_compatible_maps(source_colors, patch_colors)
        if not mappings:
            counts["color_incompatible_patches"] += 1
            continue

        viable: list[tuple[tuple[int, ...], nx.Graph, list[Edge], dict[str, Any]]] = []
        for mapping in mappings:
            assembled, glue_edges = assemble(
                source_core, source_ports, patch, patch_ports, mapping
            )
            if not nx.check_planarity(assembled, counterexample=False)[0]:
                counts["nonplanar_maps"] += 1
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
                        "matching_index": matching_index,
                        "removed_edges": [list(edge) for edge in removed],
                        "mapping": list(mapping),
                        "checks": checks,
                    }
                )
                continue
            viable.append((mapping, assembled, glue_edges, checks))
        if not viable:
            continue

        counts["structurally_viable_patches"] += 1
        counts["structurally_viable_maps"] += len(viable)
        state_cache: dict[
            tuple[tuple[int, ...], tuple[tuple[int, int], ...]], dict[str, Any]
        ] = {}

        for mapping, assembled, glue_edges, checks in viable:
            relevant = [
                spec
                for spec in state_specs
                if any(states_compatible(source_state, spec, mapping) for source_state in source_positive)
            ]
            relevant.sort(key=lambda spec: (len(spec["active"]), spec["active"], spec["pairing"]))
            counts["structurally_viable_map_state_targets"] += len(relevant)
            compatible_witness: dict[str, Any] | None = None
            witness_rank: int | None = None
            for rank, spec in enumerate(relevant, 1):
                key = (
                    tuple(int(value) for value in spec["active"]),
                    tuple(tuple(int(value) for value in pair) for pair in spec["pairing"]),
                )
                if key not in state_cache:
                    state_cache[key] = exact_path_cover_state(
                        patch,
                        patch_ports,
                        key[0],
                        key[1],
                        args.call_budget,
                    )
                    counts["exact_state_decisions"] += 1
                result = state_cache[key]
                if result["classification"] == "unknown":
                    counts["state_unknown"] += 1
                    incomplete.append(
                        {
                            "matching_index": matching_index,
                            "removed_edges": [list(edge) for edge in removed],
                            "mapping": list(mapping),
                            "state": spec,
                            "result": result,
                        }
                    )
                    compatible_witness = {"classification": "unknown", "state": spec}
                    break
                if result["classification"] == "verified_positive":
                    compatible_witness = {"state": spec, "result": result}
                    witness_rank = rank
                    counts["maps_with_compatible_witness"] += 1
                    counts[f"first_witness_active_{len(spec['active'])}"] += 1
                    break

            if compatible_witness is not None:
                if witness_rank is not None and (
                    best_first_witness_rank is None or witness_rank > best_first_witness_rank
                ):
                    best_first_witness_rank = witness_rank
                    best_record = {
                        "matching_index": matching_index,
                        "removed_edges": [list(edge) for edge in removed],
                        "patch_ports": patch_ports,
                        "mapping": list(mapping),
                        "relevant_states": len(relevant),
                        "first_witness_rank": witness_rank,
                        "first_witness": compatible_witness,
                        "assembled_graph6": graph6(assembled),
                    }
                    checkpoint("new_hardest_positive", matching_index)
                    print(
                        json.dumps(
                            {
                                "matching_index": matching_index,
                                "new_hardest_positive_rank": witness_rank,
                                "relevant_states": len(relevant),
                            }
                        ),
                        flush=True,
                    )
                continue

            counts["zero_language_maps"] += 1
            candidate_graph6 = graph6(assembled)
            candidate_id = (
                f"asano26-direct-r{args.matching_residue}-m{matching_index:05d}-"
                f"{sha256_text(candidate_graph6)[:12]}"
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
            candidate = {
                "candidate_id": candidate_id,
                "matching_index": matching_index,
                "removed_edges": [list(edge) for edge in removed],
                "patch_ports": patch_ports,
                "mapping": list(mapping),
                "glue_edges": [list(edge) for edge in glue_edges],
                "relevant_states": len(relevant),
                "all_relevant_states_exact_negative": True,
                "candidate_graph6": candidate_graph6,
                "candidate_graph6_sha256": sha256_text(candidate_graph6),
                "graph_validation": checks,
                "whole_graph_result": proof_result,
            }
            zero_records.append(candidate)
            if (
                proof_result["classification"] == "certified_negative"
                and proof_result.get("proof_verification", {}).get("verified", False)
            ):
                counts["certified_counterexample_candidates"] += 1
                certified_candidates.append(candidate)
                checkpoint("certified_counterexample_candidate", matching_index)
                stop = True
                break
            if proof_result["classification"] == "verified_positive":
                checkpoint("language_composition_contradiction", matching_index)
                raise SystemExit("zero exact composition contradicted by Hamiltonian witness")
            counts["whole_graph_unknown"] += 1
            incomplete.append(candidate)
            checkpoint("whole_graph_unknown", matching_index)
            stop = True
            break
        if stop:
            break
        if assigned_matchings % 25 == 0:
            checkpoint("searching", matching_index)

    # Count the global matching space deterministically even if this residue stopped early.
    if not stop and not counts["wall_time"]:
        total_matchings = sum(1 for _ in three_edge_matchings(seed))
        assigned_expected = sum(
            1
            for index, _ in enumerate(three_edge_matchings(seed))
            if index % args.matching_modulus == args.matching_residue
        )
        if assigned_matchings != assigned_expected:
            incomplete.append(
                {
                    "reason": "assigned matching count mismatch",
                    "observed": assigned_matchings,
                    "expected": assigned_expected,
                }
            )

    status = "certified_counterexample_candidate" if certified_candidates else "completed"
    if counts["wall_time"]:
        status = "wall_time_exhausted"
    elif incomplete:
        status = "incomplete"
    summary = {
        "date_utc": "2026-08-03",
        "campaign": "direct-asano26-six-port-search",
        "status": status,
        "matching_residue": args.matching_residue,
        "matching_modulus": args.matching_modulus,
        "total_matching_space": total_matchings,
        "assigned_matchings_processed": assigned_matchings,
        "seed": {
            "graph6": seed_graph6,
            "graph6_sha256": sha256_text(seed_graph6),
            "construction_manifest": construction_manifest,
            "graph_validation": seed_validation,
            "nonhamiltonicity_proof": seed_proof,
        },
        "source_positive_states": len(source_positive),
        "counts": dict(counts),
        "best_first_witness_rank": best_first_witness_rank,
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
    save_json(args.output_dir / "campaign_summary.json", summary)
    checkpoint(status)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
