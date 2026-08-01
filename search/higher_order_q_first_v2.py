#!/usr/bin/env python3
"""Collision-safe multi-graph driver for the higher-order Q-first search.

The original cyclic-cut enumerator numbers cuts independently inside each
parent graph. This driver namespaces every task as

    g<graph-index>-c<cut-index>-s<side-index>

before batching, retrying, and exporting SAT candidates. It also asserts key
uniqueness at every stage so a future indexing regression fails closed instead
of silently overwriting results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import scipy

import higher_order_q_first as q1
from cyclic_cut_patch_search import enumerate_patch_tasks


def namespace_tasks(tasks: list[dict[str, Any]], graph_index: int) -> list[dict[str, Any]]:
    output = []
    for task in tasks:
        local_key = str(task["key"])
        namespaced = dict(task)
        namespaced["local_key"] = local_key
        namespaced["key"] = f"g{graph_index}-{local_key}"
        output.append(namespaced)
    keys = [task["key"] for task in output]
    if len(keys) != len(set(keys)):
        raise RuntimeError(f"duplicate task key inside graph {graph_index}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, required=True)
    parser.add_argument("--graphs", type=int, default=6)
    parser.add_argument("--patches-per-graph", type=int, default=320)
    parser.add_argument("--state-time", type=float, default=4.0)
    parser.add_argument("--retry-time", type=float, default=45.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.time()
    verified = json.loads(args.verified.read_text(encoding="utf-8"))
    source_records = verified["results"][: args.graphs]
    graph6_by_index = {
        int(record["pool_index"]): record["graph6"] for record in source_records
    }

    selected_tasks: list[dict[str, Any]] = []
    graph_metadata: dict[str, Any] = {}
    for record in source_records:
        graph_index = int(record["pool_index"])
        graph = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
        raw_tasks, cut_count = enumerate_patch_tasks(graph, graph_index)
        tasks = namespace_tasks(raw_tasks, graph_index)
        selected = q1.select_patch_tasks(
            tasks, graph.number_of_nodes(), args.patches_per_graph
        )
        selected_tasks.extend(selected)
        graph_metadata[str(graph_index)] = {
            "n": graph.number_of_nodes(),
            "m": graph.number_of_edges(),
            "cyclic_four_cuts": cut_count,
            "available_patch_sides": len(tasks),
            "selected_patch_sides": len(selected),
            "selected_size_histogram": dict(
                sorted(Counter(len(task["side"]["nodes"]) for task in selected).items())
            ),
            "source_graph_sha256": hashlib.sha256(
                record["graph6"].encode("ascii")
            ).hexdigest(),
        }

    all_keys = [task["key"] for task in selected_tasks]
    if len(all_keys) != len(set(all_keys)):
        duplicates = sorted(key for key, count in Counter(all_keys).items() if count > 1)
        raise RuntimeError(f"cross-graph task-key collision: {duplicates[:20]}")

    first = q1.run_batch(
        graph6_by_index, selected_tasks, args.state_time, args.workers
    )
    if len(first) != len(selected_tasks):
        raise RuntimeError(
            f"result cardinality mismatch: {len(first)} results for "
            f"{len(selected_tasks)} selected patches"
        )

    task_by_key = {task["key"]: task for task in selected_tasks}
    retry_keys = [
        key
        for key, result in first.items()
        if any(
            q1.state_classification(state) != "verified_positive"
            for state in result["states"].values()
        )
    ]
    if retry_keys:
        print(
            json.dumps(
                {"retry_patch_count": len(retry_keys), "retry_time": args.retry_time}
            ),
            flush=True,
        )
        retries = q1.run_batch(
            graph6_by_index,
            [task_by_key[key] for key in retry_keys],
            args.retry_time,
            args.workers,
        )
        if set(retries) != set(retry_keys):
            raise RuntimeError("retry result keys do not match requested keys")
        first.update(retries)

    counts = Counter()
    candidate_cases: list[dict[str, Any]] = []
    for key, result in sorted(first.items()):
        for state_key, state in sorted(result["states"].items()):
            classification = q1.state_classification(state)
            counts[classification] += 1
            if classification != "verified_positive":
                candidate_cases.append(
                    {
                        "case_id": f"{key}-{state_key}",
                        "classification": classification,
                        "parent_graph6": graph6_by_index[
                            int(result["task"]["graph_index"])
                        ],
                        "patch_nodes": result["patch_nodes"],
                        "spec": result["spec"],
                        "state": state_key,
                        "milp_result": state,
                    }
                )

    summary = {
        "driver_version": 2,
        "task_key_scheme": "g<graph>-c<cut>-s<side>",
        "task_keys_unique": True,
        "graphs_analyzed": len(source_records),
        "patch_sides_selected": len(selected_tasks),
        "patch_results_recorded": len(first),
        "q_states_attempted": 2 * len(selected_tasks),
        "verified_positive_q_states": counts["verified_positive"],
        "provisional_negative_q_states": counts["provisional_negative"],
        "unknown_q_states": counts["unknown"],
        "candidate_cases_for_independent_sat": len(candidate_cases),
        "independently_certified_missing_q_states": 0,
        "counterexample_found": False,
        "elapsed_s": time.time() - started,
    }
    output = {
        "classification_policy": {
            "verified_positive": (
                "explicit selected-edge witness passed independent combinatorial "
                "validation"
            ),
            "provisional_negative": (
                "MILP reported infeasible; not mathematical evidence; independent "
                "SAT proof required"
            ),
            "unknown": "timeout, solver error, or invalid/missing witness",
        },
        "parameters": vars(args)
        | {"verified": str(args.verified), "output": str(args.output)},
        "software": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "networkx": nx.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "graphs": graph_metadata,
        "summary": summary,
        "candidate_cases": candidate_cases,
        "patch_results": first,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
