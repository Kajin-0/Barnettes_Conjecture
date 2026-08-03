#!/usr/bin/env python3
"""Search small face patches over a certified H-- pair for a forced edge.

For the candidate-489 face-edge pair (0,9), enumerate every connected planar
bipartite patch with 6, 8, or 10 vertices whose four labelled ports have degree
two and whose remaining vertices have degree three.  Glue every color-preserving
port permutation into the two deleted source edges, deduplicate the resulting
Barnette graphs by graph6, and test every newly introduced patch/glue edge.

A tested edge is forced precisely when the expanded graph has no Hamiltonian
cycle avoiding that edge.  Positive cases retain an independently validated
cycle witness.  Final negative status requires CaDiCaL plus drat-trim through
``solve_case`` from ``sat_verify_face_constraints.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

from sat_verify_face_constraints import graph_validation, solve_case

Edge = tuple[int, int]


def ce(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def degree_matrices(degrees: list[int]) -> Iterable[tuple[tuple[int, ...], ...]]:
    """Enumerate labelled square 0/1 matrices with given row/column degrees."""
    width = len(degrees)
    row_options = [list(itertools.combinations(range(width), degree)) for degree in degrees]
    for rows in itertools.product(*row_options):
        column_degrees = [0] * width
        for row in rows:
            for column in row:
                column_degrees[column] += 1
        if column_degrees == degrees:
            yield tuple(tuple(row) for row in rows)


def patch_from_matrix(rows: tuple[tuple[int, ...], ...]) -> tuple[nx.Graph, list[int], list[int]]:
    width = len(rows)
    left = list(range(width))
    right = list(range(width, 2 * width))
    patch = nx.Graph()
    patch.add_nodes_from(left, bipartite=0)
    patch.add_nodes_from(right, bipartite=1)
    for row_index, columns in enumerate(rows):
        for column in columns:
            patch.add_edge(left[row_index], right[column])
    return patch, left, right


def enumerate_expansions(
    source: nx.Graph,
    face_edges: list[Edge],
    pair_indices: tuple[int, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_colors = nx.bipartite.color(source)
    removed_edges = [face_edges[index] for index in pair_indices]
    core = source.copy()
    core.remove_edges_from(removed_edges)

    endpoints_by_color: dict[int, list[int]] = {0: [], 1: []}
    for edge in removed_edges:
        for vertex in edge:
            endpoints_by_color[int(source_colors[vertex])].append(vertex)
    for color in (0, 1):
        endpoints_by_color[color].sort()
        if len(endpoints_by_color[color]) != 2:
            raise ValueError(f"expected two source endpoints of color {color}")

    raw_matrix_counts: Counter[int] = Counter()
    connected_planar_patch_counts: Counter[int] = Counter()
    valid_before_dedup: Counter[int] = Counter()
    records_by_graph6: dict[str, dict[str, Any]] = {}
    source_order = source.number_of_nodes()

    for side_width in (3, 4, 5):
        patch_order = 2 * side_width
        degrees = [2, 2] + [3] * (side_width - 2)
        for matrix_index, rows in enumerate(degree_matrices(degrees)):
            raw_matrix_counts[patch_order] += 1
            patch, left, right = patch_from_matrix(rows)
            if not nx.is_connected(patch):
                continue
            patch_planar, _ = nx.check_planarity(patch, counterexample=False)
            if not patch_planar:
                continue
            connected_planar_patch_counts[patch_order] += 1

            # Source color 1 connects to patch color 0 (left); source color 0
            # connects to patch color 1 (right). Only the first two vertices on
            # each patch side are labelled ports; all other patch vertices have
            # internal degree three.
            for left_targets in itertools.permutations(endpoints_by_color[1]):
                for right_targets in itertools.permutations(endpoints_by_color[0]):
                    relabel = {
                        vertex: source_order + vertex
                        for vertex in patch.nodes()
                    }
                    expanded = core.copy()
                    expanded.add_nodes_from(relabel.values())
                    patch_edges = [
                        ce(relabel[u], relabel[v])
                        for u, v in patch.edges()
                    ]
                    expanded.add_edges_from(patch_edges)
                    glue_edges: list[Edge] = []
                    for port, target in zip(left[:2], left_targets, strict=True):
                        edge = ce(relabel[port], target)
                        expanded.add_edge(*edge)
                        glue_edges.append(edge)
                    for port, target in zip(right[:2], right_targets, strict=True):
                        edge = ce(relabel[port], target)
                        expanded.add_edge(*edge)
                        glue_edges.append(edge)

                    checks = graph_validation(expanded)
                    if not checks["barnette_predicates"]:
                        continue
                    valid_before_dedup[patch_order] += 1
                    graph6 = nx.to_graph6_bytes(expanded, header=False).decode("ascii").strip()
                    graph_hash = hashlib.sha256(graph6.encode("ascii")).hexdigest()
                    new_edges = sorted(set(patch_edges + glue_edges))
                    record = {
                        "patch_order": patch_order,
                        "matrix_index": matrix_index,
                        "matrix_rows": [list(row) for row in rows],
                        "left_targets": list(left_targets),
                        "right_targets": list(right_targets),
                        "graph6": graph6,
                        "graph6_sha256": graph_hash,
                        "graph_validation": checks,
                        "removed_source_edges": [list(edge) for edge in removed_edges],
                        "patch_edges": [list(edge) for edge in sorted(patch_edges)],
                        "glue_edges": [list(edge) for edge in sorted(glue_edges)],
                        "new_edges": [list(edge) for edge in new_edges],
                    }
                    previous = records_by_graph6.get(graph6)
                    if previous is None:
                        records_by_graph6[graph6] = record
                    else:
                        previous_key = (
                            previous["patch_order"],
                            previous["matrix_index"],
                            previous["left_targets"],
                            previous["right_targets"],
                        )
                        record_key = (
                            record["patch_order"],
                            record["matrix_index"],
                            record["left_targets"],
                            record["right_targets"],
                        )
                        if record_key < previous_key:
                            records_by_graph6[graph6] = record

    records = sorted(
        records_by_graph6.values(),
        key=lambda record: (
            record["patch_order"],
            record["graph6_sha256"],
        ),
    )
    for index, record in enumerate(records):
        record["candidate_index"] = index
        record["candidate_id"] = (
            f"pair{pair_indices[0]}_{pair_indices[1]}"
            f"-n{record['patch_order']}-c{index:04d}"
            f"-{record['graph6_sha256'][:12]}"
        )

    summary = {
        "pair_indices": list(pair_indices),
        "removed_source_edges": [list(edge) for edge in removed_edges],
        "raw_matrix_counts": {str(key): value for key, value in sorted(raw_matrix_counts.items())},
        "connected_planar_patch_counts": {
            str(key): value for key, value in sorted(connected_planar_patch_counts.items())
        },
        "valid_expansions_before_graph6_dedup": {
            str(key): value for key, value in sorted(valid_before_dedup.items())
        },
        "unique_valid_expansions": len(records),
        "unique_valid_by_patch_order": dict(
            sorted(Counter(record["patch_order"] for record in records).items())
        ),
        "new_edge_cases": sum(len(record["new_edges"]) for record in records),
    }
    return records, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pair-indices", default="0,9")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-rounds", type=int, default=20000)
    parser.add_argument("--proof-timeout", type=float, default=1800.0)
    args = parser.parse_args()

    if not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("invalid shard index/count")
    pair_indices = tuple(int(value) for value in args.pair_indices.split(","))
    if len(pair_indices) != 2:
        raise SystemExit("--pair-indices must contain exactly two indices")

    source_raw = args.source_input.read_bytes()
    source_data = json.loads(source_raw)
    source = nx.from_graph6_bytes(source_data["source"]["graph6"].encode("ascii"))
    source_checks = graph_validation(source)
    if not source_checks["barnette_predicates"]:
        raise SystemExit(f"source failed Barnette predicates: {source_checks}")
    face_edges = [ce(int(edge[0]), int(edge[1])) for edge in source_data["face"]["edges_cyclic_order"]]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    candidates, generation = enumerate_expansions(source, face_edges, pair_indices)
    if pair_indices == (0, 9):
        expected = {
            "unique_valid_expansions": 436,
            "unique_valid_by_patch_order": {6: 4, 10: 432},
            "new_edge_cases": 7388,
        }
        for key, value in expected.items():
            if generation[key] != value:
                raise SystemExit(f"generation regression for {key}: {generation[key]} != {value}")

    shard_candidates = [
        record
        for record in candidates
        if int(record["candidate_index"]) % args.shard_count == args.shard_index
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
        "generation": generation,
        "shard": {
            "index": args.shard_index,
            "count": args.shard_count,
            "candidate_count": len(shard_candidates),
            "new_edge_cases": sum(len(record["new_edges"]) for record in shard_candidates),
        },
        "candidates": shard_candidates,
    }
    (args.output_dir / "generated_candidates.json").write_text(
        json.dumps(generation_document, indent=2),
        encoding="utf-8",
    )

    candidate_summaries: list[dict[str, Any]] = []
    aggregate_counts: Counter[str] = Counter()
    forced_edges: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []
    cases_attempted = 0
    for candidate_position, record in enumerate(shard_candidates, 1):
        graph = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
        candidate_dir = args.output_dir / record["candidate_id"]
        candidate_dir.mkdir(parents=True, exist_ok=True)
        case_results: list[dict[str, Any]] = []
        for edge_position, raw_edge in enumerate(record["new_edges"], 1):
            edge = ce(int(raw_edge[0]), int(raw_edge[1]))
            case = {
                "case_id": f"{record['candidate_id']}-avoid-{edge[0]}_{edge[1]}",
                "include_edges": [],
                "exclude_edges": [list(edge)],
                "constraint_type": "forced_edge_screen",
            }
            print(
                json.dumps(
                    {
                        "candidate": candidate_position,
                        "candidates_in_shard": len(shard_candidates),
                        "candidate_id": record["candidate_id"],
                        "edge": edge_position,
                        "edges_in_candidate": len(record["new_edges"]),
                        "case_id": case["case_id"],
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
            cases_attempted += 1
            classification = str(result["classification"])
            aggregate_counts[classification] += 1
            compact = {
                key: value
                for key, value in result.items()
                if key
                in {
                    "case_id",
                    "classification",
                    "sat",
                    "exclude_edges",
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
            case_results.append(compact)
            if classification == "certified_negative":
                forced_edges.append(
                    {
                        "candidate_id": record["candidate_id"],
                        "candidate_index": record["candidate_index"],
                        "patch_order": record["patch_order"],
                        "graph6": record["graph6"],
                        "graph6_sha256": record["graph6_sha256"],
                        "forced_edge": list(edge),
                        "case_result": compact,
                        "construction": record,
                    }
                )
            elif classification != "verified_positive":
                incomplete.append(
                    {
                        "candidate_id": record["candidate_id"],
                        "edge": list(edge),
                        "classification": classification,
                    }
                )

        candidate_summary = {
            "candidate_id": record["candidate_id"],
            "candidate_index": record["candidate_index"],
            "patch_order": record["patch_order"],
            "graph6": record["graph6"],
            "graph6_sha256": record["graph6_sha256"],
            "graph_validation": record["graph_validation"],
            "new_edges_tested": len(record["new_edges"]),
            "classification_counts": dict(Counter(item["classification"] for item in case_results)),
            "forced_edges": [
                item["forced_edge"]
                for item in forced_edges
                if item["candidate_id"] == record["candidate_id"]
            ],
            "results": case_results,
        }
        candidate_summaries.append(candidate_summary)
        (candidate_dir / "candidate_summary.json").write_text(
            json.dumps(candidate_summary, indent=2),
            encoding="utf-8",
        )

    summary = {
        "date_utc": "2026-08-03",
        "campaign": "candidate489-small-patch-forced-edge-screen",
        "pair_indices": list(pair_indices),
        "generation": generation,
        "shard": generation_document["shard"],
        "candidates_attempted": len(shard_candidates),
        "cases_attempted": cases_attempted,
        "classification_counts": dict(aggregate_counts),
        "forced_edge_candidates": forced_edges,
        "forced_edge_count": len(forced_edges),
        "incomplete_cases": incomplete,
        "complete_classification": not incomplete,
        "required_edge_fragment_found": bool(forced_edges),
        "counterexample_found": False,
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
        "candidate_summaries": candidate_summaries,
    }
    (args.output_dir / "campaign_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "generation": generation,
                "shard": generation_document["shard"],
                "classification_counts": dict(aggregate_counts),
                "forced_edge_count": len(forced_edges),
                "incomplete_count": len(incomplete),
                "elapsed_s": summary["elapsed_s"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
