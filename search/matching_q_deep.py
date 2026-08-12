#!/usr/bin/env python3
"""Deepen perfect-matching sampling on the hardest zero-hit Q patches."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import time
from pathlib import Path

import networkx as nx

from cyclic_cut_patch_search import enumerate_patch_tasks
from matching_q_screen import TARGETS, sample_task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, required=True)
    parser.add_argument("--screen", type=Path, required=True)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--trials", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    screen = json.loads(args.screen.read_text())
    verified = json.loads(args.verified.read_text())["results"]
    records = {int(record["pool_index"]): record for record in verified}
    zero_hit = [result for result in screen["results"].values() if not result["found"]]
    zero_hit.sort(key=lambda result: (result["best_components"], -result["patch_n"], result["key"]))
    chosen = zero_hit[: args.count]
    keys = {result["key"] for result in chosen}
    task_map = {}
    graph6 = {}

    for graph_index, record in records.items():
        if not any(key.startswith(f"g{graph_index}-") for key in keys):
            continue
        graph = nx.from_graph6_bytes(record["graph6"].encode())
        tasks, _ = enumerate_patch_tasks(graph, graph_index)
        graph6[graph_index] = record["graph6"]
        for task in tasks:
            if task["key"] in keys:
                task_map[task["key"]] = task

    payloads = []
    for index, result in enumerate(chosen):
        graph_index = int(re.match(r"g(\d+)-", result["key"]).group(1))
        payloads.append(
            (graph6[graph_index], task_map[result["key"]], args.trials, args.seed + index)
        )

    started = time.time()
    results = []
    with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(sample_task, payloads, chunksize=1):
            results.append(result)
            print(
                json.dumps(
                    {
                        "key": result["key"],
                        "n": result["patch_n"],
                        "found": sorted(result["found"]),
                        "trials": result["trials"],
                        "best_components": result["best_components"],
                    }
                ),
                flush=True,
            )

    summary = {
        "cases": len(results),
        "both_found": sum(TARGETS <= set(result["found"]) for result in results),
        "one_found": sum(len(result["found"]) == 1 for result in results),
        "zero_found": sum(not result["found"] for result in results),
        "elapsed_s": time.time() - started,
        "trials_cap": args.trials,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"summary": summary, "results": results}, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
