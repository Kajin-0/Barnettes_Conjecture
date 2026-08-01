#!/usr/bin/env python3
"""Generate adversarial Barnette populations at exact target orders by C4 expansion.

Small canonical cyclically 4-connected Barnette graphs are used as seeds. Each
candidate is grown using only facial C4 expansions, independently validated,
filtered against implemented easy face regimes, ranked by randomized
perfect-matching fragmentation, and exact-tested for Hamiltonicity.

The population is heuristic and noncanonical. Positive cycle witnesses are
independently checked. Infeasibility and timeout are never final claims.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import platform
import random
import time
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import scipy

import adversarial_evolution as evo

MODES = ("uniform", "large-main", "large-sides", "cluster", "balanced", "four-face")


def read_graph6(paths: list[Path]) -> list[str]:
    seen = set()
    output = []
    for path in paths:
        for raw in path.read_bytes().splitlines():
            raw = raw.strip()
            if not raw or raw.startswith(b">>"):
                continue
            graph = nx.from_graph6_bytes(raw)
            encoded = evo.g6(graph)
            if encoded not in seen:
                seen.add(encoded)
                output.append(encoded)
    return output


def site_weight(site: evo.Site, mode: str) -> float:
    _, _, _, _, main, separation, side1, side2 = site
    balance = separation * (main - separation)
    big_sides = int(side1 >= 6) + int(side2 >= 6)
    if mode == "uniform":
        return 1.0
    if mode == "large-main":
        return 1.0 + main**3
    if mode == "large-sides":
        return 1.0 + side1**3 + side2**3 + 200.0 * big_sides
    if mode == "cluster":
        return 1.0 + main**2 + side1**2 + side2**2 + 500.0 * big_sides
    if mode == "balanced":
        return 1.0 + balance**2 + 30.0 * big_sides
    if mode == "four-face":
        return 100.0 if main == 4 else 1.0
    raise ValueError(mode)


def grow(payload: dict[str, Any]) -> dict[str, Any]:
    target = int(payload["target"])
    seed_graph6 = payload["seed_graph6"]
    seed_index = int(payload["seed_index"])
    mode = payload["mode"]
    random_seed = int(payload["random_seed"])
    trials = int(payload["matching_trials"])
    rng = random.Random(random_seed)
    graph = nx.from_graph6_bytes(seed_graph6.encode("ascii"))
    history = []
    while graph.number_of_nodes() < target:
        sites = evo.c4_sites(graph)
        if not sites:
            return {
                "status": "generation_failure",
                "reason": "no facial C4 site",
                "target": target,
                "seed_index": seed_index,
                "mode": mode,
                "random_seed": random_seed,
            }
        weights = [site_weight(site, mode) for site in sites]
        selected = rng.choices(sites, weights=weights, k=1)[0]
        graph = evo.c4_expand(graph, selected)
        history.append({"site": list(selected), "n": graph.number_of_nodes()})
    if graph.number_of_nodes() != target:
        return {
            "status": "generation_failure",
            "reason": "target overshoot",
            "target": target,
            "seed_index": seed_index,
            "mode": mode,
            "random_seed": random_seed,
        }

    validation = evo.barnette_validation(graph, compute_connectivity=True)
    metrics = evo.face_metrics(graph)
    eligible = (
        validation["barnette"]
        and metrics["max_face"] >= 10
        and metrics["max_big_neighbors"] >= 5
    )
    fragmentation = (
        evo.randomized_matching_fragmentation(graph, trials, random_seed + 1_000_000)
        if eligible
        else None
    )
    encoded = evo.g6(graph)
    return {
        "status": "ok",
        "target": target,
        "seed_index": seed_index,
        "seed_graph6": seed_graph6,
        "mode": mode,
        "random_seed": random_seed,
        "graph6": encoded,
        "sha256": hashlib.sha256(encoded.encode("ascii")).hexdigest(),
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "history": history,
        "validation": validation,
        "face_metrics": metrics,
        "eligible": eligible,
        "fragmentation": fragmentation,
    }


def ranking_key(record: dict[str, Any]) -> tuple:
    fragmentation = record["fragmentation"]
    metrics = record["face_metrics"]
    return (
        -fragmentation["hamiltonian_hits"],
        fragmentation["minimum_components"],
        fragmentation["q05_components"],
        fragmentation["median_components"],
        fragmentation["mean_components"],
        metrics["sum_big_neighbor_excess"],
        metrics["max_face"],
    )


def cycle_validation(graph: nx.Graph, edges) -> dict[str, Any]:
    if not edges:
        return {"valid": False, "reason": "missing edges"}
    chosen = [evo.ce(*edge) for edge in edges]
    subgraph = nx.Graph()
    subgraph.add_nodes_from(graph)
    subgraph.add_edges_from(chosen)
    checks = {
        "edge_count": len(chosen),
        "expected_edge_count": graph.number_of_nodes(),
        "all_edges_in_graph": all(graph.has_edge(*edge) for edge in chosen),
        "no_duplicates": len(chosen) == len(set(chosen)),
        "degree_two": all(subgraph.degree(v) == 2 for v in graph),
        "connected": nx.is_connected(subgraph),
    }
    checks["valid"] = (
        checks["edge_count"] == checks["expected_edge_count"]
        and checks["all_edges_in_graph"]
        and checks["no_duplicates"]
        and checks["degree_two"]
        and checks["connected"]
    )
    return checks


def exact_test(payload: tuple[dict[str, Any], float, int]) -> dict[str, Any]:
    record, time_limit, seed = payload
    graph = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
    result = evo.hamiltonian_flow_milp(graph, time_limit, seed)
    result_dict = result.__dict__.copy()
    result_dict["cycle_validation"] = (
        cycle_validation(graph, result.cycle_edges) if result.cycle_edges else None
    )
    return {"pool_index": record["pool_index"], "hamiltonicity": result_dict}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--target", type=int, required=True)
    parser.add_argument("--attempts", type=int, default=480)
    parser.add_argument("--matching-trials", type=int, default=256)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--ham-time", type=float, default=20.0)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.time()
    seeds = read_graph6(args.inputs)
    reachable_seeds = [
        graph6
        for graph6 in seeds
        if (args.target - nx.from_graph6_bytes(graph6.encode()).number_of_nodes()) >= 0
        and (args.target - nx.from_graph6_bytes(graph6.encode()).number_of_nodes()) % 4 == 0
    ]
    if not reachable_seeds:
        raise SystemExit("No reachable seed graph")

    rng = random.Random(args.seed + args.target)
    payloads = []
    for attempt in range(args.attempts):
        seed_index = rng.randrange(len(reachable_seeds))
        payloads.append(
            {
                "target": args.target,
                "seed_graph6": reachable_seeds[seed_index],
                "seed_index": seed_index,
                "mode": MODES[attempt % len(MODES)],
                "random_seed": args.seed + args.target * 100_000 + attempt,
                "matching_trials": args.matching_trials,
            }
        )

    generated = []
    with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for index, record in enumerate(executor.map(grow, payloads, chunksize=1), 1):
            generated.append(record)
            if index % 20 == 0:
                print(
                    json.dumps(
                        {
                            "phase": "generation",
                            "target": args.target,
                            "completed": index,
                            "eligible": sum(r.get("eligible", False) for r in generated),
                        }
                    ),
                    flush=True,
                )

    unique: dict[str, dict[str, Any]] = {}
    failures = Counter()
    for record in generated:
        if record.get("status") != "ok":
            failures[record.get("reason", "unknown")] += 1
            continue
        encoded = record["graph6"]
        previous = unique.get(encoded)
        if previous is None or (
            record.get("eligible", False)
            and not previous.get("eligible", False)
        ):
            unique[encoded] = record

    eligible = [record for record in unique.values() if record["eligible"]]
    eligible.sort(key=ranking_key, reverse=True)
    retained = eligible[: args.top]
    for pool_index, record in enumerate(retained):
        record["pool_index"] = pool_index
        record["mode"] = "pure-c4-expansion-fallback"
        record["structural_score"] = evo.structural_score(record["face_metrics"])

    exact_payloads = [
        (record, args.ham_time, args.seed + args.target * 10_000 + index)
        for index, record in enumerate(retained)
    ]
    exact_results = []
    with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(exact_test, exact_payloads, chunksize=1):
            exact_results.append(result)
            print(
                json.dumps(
                    {
                        "phase": "exact_hamiltonicity",
                        "target": args.target,
                        "pool_index": result["pool_index"],
                        "status": result["hamiltonicity"]["status"],
                        "hamiltonian": result["hamiltonicity"]["hamiltonian"],
                        "elapsed_s": result["hamiltonicity"]["elapsed_s"],
                    }
                ),
                flush=True,
            )
    exact_by_index = {result["pool_index"]: result["hamiltonicity"] for result in exact_results}
    results = []
    for record in retained:
        compact = {
            "pool_index": record["pool_index"],
            "n": record["n"],
            "graph6": record["graph6"],
            "mode": record["mode"],
            "structural_score": record["structural_score"],
            "face_metrics": record["face_metrics"],
            "fragmentation": record["fragmentation"],
            "validation": record["validation"],
            "seed_index": record["seed_index"],
            "expansion_mode": record["mode"],
            "history": record["history"],
            "hamiltonicity": exact_by_index[record["pool_index"]],
        }
        results.append(compact)

    summary = {
        "target": args.target,
        "seed_graphs": len(seeds),
        "reachable_seed_graphs": len(reachable_seeds),
        "attempts": args.attempts,
        "generation_failures": dict(failures),
        "unique_graph6": len(unique),
        "eligible": len(eligible),
        "retained": len(results),
        "whole_graph_hamiltonian_witnesses": sum(
            result["hamiltonicity"]["hamiltonian"] is True
            and (result["hamiltonicity"].get("cycle_validation") or {}).get("valid")
            for result in results
        ),
        "whole_graph_provisional_infeasible": sum(
            result["hamiltonicity"]["hamiltonian"] is False for result in results
        ),
        "whole_graph_unknown": sum(
            result["hamiltonicity"]["hamiltonian"] is None for result in results
        ),
        "elapsed_s": time.time() - started,
        "counterexample_found": False,
    }
    output = {
        "metadata": {
            "campaign": "pure-c4-expansion-order-fallback",
            "canonical": False,
            "ranking_is_heuristic": True,
            "software": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "networkx": nx.__version__,
                "numpy": np.__version__,
                "scipy": scipy.__version__,
            },
            "parameters": vars(args)
            | {"inputs": [str(path) for path in args.inputs], "output": str(args.output)},
        },
        "summary": summary,
        "results": results,
        "all_unique": list(unique.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"phase": "complete", **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
