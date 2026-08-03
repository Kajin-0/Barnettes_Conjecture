#!/usr/bin/env python3
"""Compose two candidate-489 unavoidable-pair four-poles exactly.

Each source pole is formed by deleting one of the eight proof-certified
cofacial edge pairs from canonical order-100 candidate 489. Two disjoint copies
are joined across their four degree-two terminals under every bipartition-
preserving bijection. The script retains graph6-distinct assemblies that are
simple, cubic, bipartite, planar, and 3-connected, then solves whole-graph
Hamiltonicity with witness validation and proof-producing negative escalation.
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
from typing import Any

import networkx as nx

from sat_verify_face_constraints import graph_validation, solve_case

CERTIFIED_PAIRS = [
    (0, 9),
    (1, 8),
    (2, 7),
    (2, 9),
    (2, 11),
    (3, 6),
    (4, 7),
    (8, 11),
]


def ce(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def relabel_second_copy(graph: nx.Graph, offset: int) -> tuple[nx.Graph, dict[int, int]]:
    mapping = {vertex: offset + index for index, vertex in enumerate(sorted(graph.nodes()))}
    return nx.relabel_nodes(graph, mapping, copy=True), mapping


def compose_pair_poles(
    source: nx.Graph,
    face_edges: list[tuple[int, int]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_colors = nx.bipartite.color(source)
    second, second_mapping = relabel_second_copy(source, max(source.nodes()) + 1)
    second_colors = {second_mapping[v]: color for v, color in source_colors.items()}

    raw_maps = 0
    barnette_maps = 0
    records_by_graph6: dict[str, dict[str, Any]] = {}

    for left_index, pair_left in enumerate(CERTIFIED_PAIRS):
        for right_index in range(left_index, len(CERTIFIED_PAIRS)):
            pair_right = CERTIFIED_PAIRS[right_index]
            removed_left = [face_edges[index] for index in pair_left]
            removed_right_original = [face_edges[index] for index in pair_right]
            removed_right = [
                ce(second_mapping[u], second_mapping[v])
                for u, v in removed_right_original
            ]

            left_core = source.copy()
            left_core.remove_edges_from(removed_left)
            right_core = second.copy()
            right_core.remove_edges_from(removed_right)

            left_terminals: dict[int, list[int]] = {0: [], 1: []}
            right_terminals: dict[int, list[int]] = {0: [], 1: []}
            for edge in removed_left:
                for vertex in edge:
                    left_terminals[int(source_colors[vertex])].append(vertex)
            for edge in removed_right:
                for vertex in edge:
                    right_terminals[int(second_colors[vertex])].append(vertex)
            for color in (0, 1):
                left_terminals[color].sort()
                right_terminals[color].sort()
                if len(left_terminals[color]) != 2 or len(right_terminals[color]) != 2:
                    raise ValueError("each pole must expose two terminals of each color")

            # Join opposite colors across the two copies. There are 2!*2!=4
            # bipartition-preserving maps for every unordered pair of poles.
            for targets_for_left_zero in itertools.permutations(right_terminals[1]):
                for targets_for_left_one in itertools.permutations(right_terminals[0]):
                    raw_maps += 1
                    assembled = nx.compose(left_core, right_core)
                    glue_edges: list[tuple[int, int]] = []
                    for source_terminal, target_terminal in zip(
                        left_terminals[0], targets_for_left_zero, strict=True
                    ):
                        edge = ce(source_terminal, target_terminal)
                        assembled.add_edge(*edge)
                        glue_edges.append(edge)
                    for source_terminal, target_terminal in zip(
                        left_terminals[1], targets_for_left_one, strict=True
                    ):
                        edge = ce(source_terminal, target_terminal)
                        assembled.add_edge(*edge)
                        glue_edges.append(edge)

                    checks = graph_validation(assembled)
                    if not checks["barnette_predicates"]:
                        continue
                    barnette_maps += 1
                    graph6 = nx.to_graph6_bytes(assembled, header=False).decode("ascii").strip()
                    graph_hash = hashlib.sha256(graph6.encode("ascii")).hexdigest()
                    record = {
                        "left_pair_list_index": left_index,
                        "right_pair_list_index": right_index,
                        "left_face_edge_indices": list(pair_left),
                        "right_face_edge_indices": list(pair_right),
                        "left_removed_edges": [list(edge) for edge in removed_left],
                        "right_removed_edges_original_labels": [
                            list(edge) for edge in removed_right_original
                        ],
                        "right_removed_edges_relabelled": [list(edge) for edge in removed_right],
                        "left_terminals_by_color": {
                            str(color): left_terminals[color] for color in (0, 1)
                        },
                        "right_terminals_by_color": {
                            str(color): right_terminals[color] for color in (0, 1)
                        },
                        "targets_for_left_color_zero": list(targets_for_left_zero),
                        "targets_for_left_color_one": list(targets_for_left_one),
                        "glue_edges": [list(edge) for edge in sorted(glue_edges)],
                        "graph6": graph6,
                        "graph6_sha256": graph_hash,
                        "graph_validation": checks,
                    }
                    previous = records_by_graph6.get(graph6)
                    if previous is None:
                        records_by_graph6[graph6] = record
                    else:
                        previous_key = (
                            previous["left_pair_list_index"],
                            previous["right_pair_list_index"],
                            previous["glue_edges"],
                        )
                        record_key = (
                            record["left_pair_list_index"],
                            record["right_pair_list_index"],
                            record["glue_edges"],
                        )
                        if record_key < previous_key:
                            records_by_graph6[graph6] = record

    records = sorted(
        records_by_graph6.values(),
        key=lambda item: (
            item["left_pair_list_index"],
            item["right_pair_list_index"],
            item["graph6_sha256"],
        ),
    )
    for candidate_index, record in enumerate(records):
        record["candidate_index"] = candidate_index
        record["candidate_id"] = (
            f"pole-p{record['left_pair_list_index']}"
            f"-p{record['right_pair_list_index']}"
            f"-c{candidate_index:03d}"
            f"-{record['graph6_sha256'][:12]}"
        )

    generation = {
        "certified_pair_count": len(CERTIFIED_PAIRS),
        "unordered_pair_combinations": len(CERTIFIED_PAIRS) * (len(CERTIFIED_PAIRS) + 1) // 2,
        "color_preserving_maps_per_pair": 4,
        "raw_maps": raw_maps,
        "barnette_maps_before_graph6_dedup": barnette_maps,
        "unique_barnette_assemblies": len(records),
    }
    return records, generation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-rounds", type=int, default=50000)
    parser.add_argument("--proof-timeout", type=float, default=3600.0)
    args = parser.parse_args()

    if not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("invalid shard")
    source_raw = args.source_input.read_bytes()
    source_data = json.loads(source_raw)
    source = nx.from_graph6_bytes(source_data["source"]["graph6"].encode("ascii"))
    source_checks = graph_validation(source)
    if not source_checks["barnette_predicates"]:
        raise SystemExit(f"source is not Barnette: {source_checks}")
    face_edges = [ce(int(edge[0]), int(edge[1])) for edge in source_data["face"]["edges_cyclic_order"]]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    candidates, generation = compose_pair_poles(source, face_edges)
    expected = {
        "raw_maps": 144,
        "barnette_maps_before_graph6_dedup": 72,
        "unique_barnette_assemblies": 72,
    }
    for key, expected_value in expected.items():
        if generation[key] != expected_value:
            raise SystemExit(
                f"generation regression for {key}: {generation[key]} != {expected_value}"
            )

    shard_candidates = [
        candidate
        for candidate in candidates
        if int(candidate["candidate_index"]) % args.shard_count == args.shard_index
    ]
    generation_document = {
        "date_utc": "2026-08-03",
        "status": "exact_generated_candidate_family",
        "source_input": str(args.source_input),
        "source_input_sha256": hashlib.sha256(source_raw).hexdigest(),
        "source_graph6_sha256": hashlib.sha256(
            source_data["source"]["graph6"].encode("ascii")
        ).hexdigest(),
        "source_validation": source_checks,
        "certified_pairs": [list(pair) for pair in CERTIFIED_PAIRS],
        "generation": generation,
        "shard": {
            "index": args.shard_index,
            "count": args.shard_count,
            "candidates": len(shard_candidates),
        },
        "candidates": shard_candidates,
    }
    (args.output_dir / "generated_candidates.json").write_text(
        json.dumps(generation_document, indent=2), encoding="utf-8"
    )

    results: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    counterexample_candidates: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []

    for position, candidate in enumerate(shard_candidates, 1):
        graph = nx.from_graph6_bytes(candidate["graph6"].encode("ascii"))
        candidate_dir = args.output_dir / candidate["candidate_id"]
        candidate_dir.mkdir(parents=True, exist_ok=True)
        case = {
            "case_id": f"{candidate['candidate_id']}-hamiltonicity",
            "constraint_type": "whole_graph_hamiltonicity",
            "include_edges": [],
            "exclude_edges": [],
        }
        print(
            json.dumps(
                {
                    "candidate": position,
                    "candidates_in_shard": len(shard_candidates),
                    "candidate_id": candidate["candidate_id"],
                }
            ),
            flush=True,
        )
        result = solve_case(
            graph,
            case,
            candidate_dir,
            args.solver,
            args.proof_solver,
            args.drat_trim,
            args.max_rounds,
            args.proof_timeout,
        )
        classification = str(result["classification"])
        counts[classification] += 1
        compact_result = {
            key: value
            for key, value in result.items()
            if key
            in {
                "case_id",
                "classification",
                "sat",
                "rounds",
                "added_subtour_constraints",
                "elapsed_s",
                "witness_path",
                "witness_sha256",
                "cnf_path",
                "cnf_sha256",
                "proof_path",
                "proof_sha256",
                "proof_verification",
                "reason",
                "reasons",
            }
        }
        record = {
            "candidate": candidate,
            "classification": classification,
            "result": compact_result,
        }
        results.append(record)
        if classification == "certified_negative":
            counterexample_candidates.append(record)
        elif classification != "verified_positive":
            incomplete.append(record)

        (candidate_dir / "candidate_summary.json").write_text(
            json.dumps(record, indent=2), encoding="utf-8"
        )

    summary = {
        "date_utc": "2026-08-03",
        "campaign": "two-copy-unavoidable-pair-pole-composition",
        "generation": generation,
        "shard": generation_document["shard"],
        "candidates_attempted": len(shard_candidates),
        "classification_counts": dict(counts),
        "counterexample_candidates": counterexample_candidates,
        "counterexample_candidate_count": len(counterexample_candidates),
        "incomplete_cases": incomplete,
        "complete_classification": not incomplete,
        "counterexample_found": bool(counterexample_candidates),
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
        "results": results,
    }
    (args.output_dir / "campaign_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "generation": generation,
                "shard": generation_document["shard"],
                "classification_counts": dict(counts),
                "counterexample_candidate_count": len(counterexample_candidates),
                "incomplete_count": len(incomplete),
                "elapsed_s": summary["elapsed_s"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
