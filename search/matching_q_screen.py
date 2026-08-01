#!/usr/bin/env python3
"""Screen natural cyclic-4-cut sides through perfect-matching complements.

For a cut-side patch, a two-path Q state is exactly the complement of a
perfect matching whose complement has two components with the requested
terminal pairing. Sampling is used only for prioritization: positive witnesses
are checkable, while zero hits have no negative mathematical meaning.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import linear_sum_assignment

from cyclic_cut_patch_search import enumerate_patch_tasks
import patch_gluing_search as pl

TARGETS = {"Q01_23", "Q03_12"}


def sample_task(payload):
    graph6, task, trials, seed = payload
    graph = nx.from_graph6_bytes(graph6.encode("ascii"))
    side = task["side"]
    patch = graph.subgraph(side["nodes"]).copy()
    terminals = tuple(side["terminals"])
    color = nx.bipartite.color(patch)
    left = sorted(v for v, c in color.items() if c == 0)
    right = sorted(v for v, c in color.items() if c == 1)
    result = {
        "key": task["key"],
        "patch_n": len(patch),
        "patch_m": patch.number_of_edges(),
        "terminals": terminals,
        "found": {},
        "trials": 0,
        "best_components": 10**9,
    }
    if len(left) != len(right):
        result["error"] = "unbalanced patch bipartition"
        return result

    right_index = {v: i for i, v in enumerate(right)}
    allowed = np.zeros((len(left), len(right)), dtype=bool)
    for i, u in enumerate(left):
        for v in patch.neighbors(u):
            allowed[i, right_index[v]] = True

    rng = np.random.default_rng(seed)
    for trial in range(trials):
        cost = np.full(allowed.shape, 1.0e12)
        cost[allowed] = rng.exponential(size=int(allowed.sum()))
        rows, cols = linear_sum_assignment(cost)
        if any(not allowed[i, j] for i, j in zip(rows, cols)):
            result["error"] = "no perfect matching"
            break
        matching = {pl.ce(left[i], right[j]) for i, j in zip(rows, cols)}
        selected = [
            pl.ce(*edge)
            for edge in patch.edges()
            if pl.ce(*edge) not in matching
        ]
        complement = nx.Graph()
        complement.add_nodes_from(patch)
        complement.add_edges_from(selected)
        components = list(nx.connected_components(complement))
        result["best_components"] = min(result["best_components"], len(components))
        result["trials"] = trial + 1
        if len(components) != 2:
            continue
        pairs = []
        for component in components:
            ids = sorted(i for i, terminal in enumerate(terminals) if terminal in component)
            if len(ids) == 2:
                pairs.append(tuple(ids))
        if len(pairs) != 2:
            continue
        key = pl.pair_key(pl.canonical_pairing(pairs))
        if key in TARGETS and key not in result["found"]:
            result["found"][key] = {
                "selected_edges": selected,
                "matching_edges": sorted(matching),
                "trial": trial + 1,
            }
            if TARGETS <= set(result["found"]):
                break
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, required=True)
    parser.add_argument("--graphs", type=int, default=8)
    parser.add_argument("--trials", type=int, default=64)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260801)
    args = parser.parse_args()

    data = json.loads(args.verified.read_text())["results"][: args.graphs]
    all_results = {}
    graph_metadata = {}
    started = time.time()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    for record in data:
        graph_index = int(record["pool_index"])
        graph = nx.from_graph6_bytes(record["graph6"].encode())
        tasks, cuts = enumerate_patch_tasks(graph, graph_index)
        graph_metadata[str(graph_index)] = {
            "cuts": cuts,
            "patch_sides": len(tasks),
            "n": len(graph),
            "sha256": hashlib.sha256(record["graph6"].encode()).hexdigest(),
        }
        payloads = [
            (record["graph6"], task, args.trials, args.seed + graph_index * 100000 + i)
            for i, task in enumerate(tasks)
        ]
        with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
            for result in executor.map(sample_task, payloads, chunksize=4):
                all_results[result["key"]] = result
        summary = Counter()
        for result in all_results.values():
            if result["key"].startswith(f"g{graph_index}-"):
                for state in TARGETS:
                    summary[state + "_found"] += int(state in result["found"])
                summary["both_found"] += int(TARGETS <= set(result["found"]))
        print(
            json.dumps(
                {"graph": graph_index, **graph_metadata[str(graph_index)], **summary}
            ),
            flush=True,
        )
        output = {
            "parameters": {
                "trials": args.trials,
                "graphs": args.graphs,
                "seed": args.seed,
            },
            "elapsed_s": time.time() - started,
            "graphs": graph_metadata,
            "results": all_results,
        }
        args.output.write_text(json.dumps(output, indent=2))

    total = Counter()
    for result in all_results.values():
        for state in TARGETS:
            total[state + "_found"] += int(state in result["found"])
        total["both_found"] += int(TARGETS <= set(result["found"]))
        total["patches"] += 1
    print(json.dumps({"final": dict(total), "elapsed_s": time.time() - started}, indent=2))


if __name__ == "__main__":
    main()
