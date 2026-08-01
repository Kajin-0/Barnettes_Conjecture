#!/usr/bin/env python3
"""Directly synthesize graphs from sparse six-terminal patches.

Sampled signature incompatibility is not proof. This program instead glues
zero-observed-state six-terminal patches under planar bipartition-preserving
dihedral maps, validates the assembled graph, and tests Hamiltonicity directly.

Each whole-graph MILP runs in a child process with an external wall-clock
limit. Positive cycles are independently validated. MILP infeasibility is only
provisional and is exported for proof-producing SAT; timeout and process
failure remain unknown.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import networkx as nx

import patch_gluing_search as pl


def maps6() -> list[tuple[int, ...]]:
    return sorted(
        {tuple((i + r) % 6 for i in range(6)) for r in range(6)}
        | {tuple((r - i) % 6 for i in range(6)) for r in range(6)}
    )


def glue_patch_records(
    parent1: nx.Graph,
    record1: dict[str, Any],
    parent2: nx.Graph,
    record2: dict[str, Any],
    mapping: tuple[int, ...],
) -> nx.Graph:
    patch1 = parent1.subgraph(record1["nodes"]).copy()
    patch2 = parent2.subgraph(record2["nodes"]).copy()
    graph = nx.Graph()
    graph.add_nodes_from((0, v) for v in patch1)
    graph.add_edges_from(((0, u), (0, v)) for u, v in patch1.edges())
    graph.add_nodes_from((1, v) for v in patch2)
    graph.add_edges_from(((1, u), (1, v)) for u, v in patch2.edges())
    for i in range(6):
        graph.add_edge(
            (0, record1["terminals"][i]),
            (1, record2["terminals"][mapping[i]]),
        )
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def validate_cycle(graph: nx.Graph, edges: list[list[int]] | list[tuple[int, int]] | None) -> dict[str, Any]:
    if edges is None:
        return {"valid": False, "reason": "missing cycle witness"}
    chosen = [pl.ce(int(u), int(v)) for u, v in edges]
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


def solve_one(candidate_path: Path, time_limit: float, seed: int) -> int:
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    graph = nx.from_graph6_bytes(candidate["graph6"].encode("ascii"))
    result = pl.hamiltonian_flow_milp(graph, time_limit, seed)
    output = result.__dict__.copy()
    output["cycle_validation"] = (
        validate_cycle(graph, result.cycle_edges) if result.cycle_edges else None
    )
    print(json.dumps(output), flush=True)
    return 0


def run_child(payload: tuple[dict[str, Any], float, float, int, str]) -> tuple[int, dict[str, Any]]:
    candidate, milp_time, wall_time, seed, script = payload
    with tempfile.TemporaryDirectory(prefix="barnette-six-glue-") as temporary:
        path = Path(temporary) / "candidate.json"
        path.write_text(json.dumps(candidate), encoding="utf-8")
        try:
            process = subprocess.run(
                [
                    sys.executable,
                    script,
                    "--solve-one",
                    str(path),
                    "--milp-time",
                    str(milp_time),
                    "--seed",
                    str(seed),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=wall_time,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            return candidate["rank"], {
                "status": "external_timeout",
                "hamiltonian": None,
                "elapsed_s": wall_time,
                "stdout": (error.stdout or "")[-4000:] if isinstance(error.stdout, str) else "",
                "stderr": (error.stderr or "")[-4000:] if isinstance(error.stderr, str) else "",
            }
        if process.returncode != 0:
            return candidate["rank"], {
                "status": "child_failure",
                "hamiltonian": None,
                "returncode": process.returncode,
                "stdout": process.stdout[-4000:],
                "stderr": process.stderr[-4000:],
            }
        lines = [line for line in process.stdout.splitlines() if line.strip()]
        try:
            result = json.loads(lines[-1])
        except Exception:
            result = {
                "status": "malformed_child_output",
                "hamiltonian": None,
                "stdout": process.stdout[-8000:],
                "stderr": process.stderr[-8000:],
            }
        return candidate["rank"], result


def candidate_score(first: dict[str, Any], second: dict[str, Any]) -> float:
    return (
        1000.0 * (first["best_components"] + second["best_components"])
        + 10.0 * (first["patch_n"] + second["patch_n"])
        + min(first["patch_n"], second["patch_n"])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate-cap", type=int, default=240)
    parser.add_argument("--solve-cap", type=int, default=160)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--milp-time", type=float, default=15.0)
    parser.add_argument("--wall-time", type=float, default=25.0)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--solve-one", type=Path, default=None)
    args = parser.parse_args()

    if args.solve_one is not None:
        raise SystemExit(solve_one(args.solve_one, args.milp_time, args.seed))
    if args.input is None or args.output is None:
        parser.error("--input and --output are required in campaign mode")

    started = time.time()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    graph_records = data["graphs"]
    parents = {
        int(index): nx.from_graph6_bytes(record["graph6"].encode("ascii"))
        for index, record in graph_records.items()
    }
    sparse = [record for record in data["results"] if record["state_count"] == 0]
    sparse.sort(
        key=lambda record: (
            -record["best_components"],
            -record["patch_n"],
            record["key"],
        )
    )

    specifications = []
    for i, first in enumerate(sparse):
        for j in range(i, len(sparse)):
            second = sparse[j]
            for mapping in maps6():
                if all(
                    first["colors"][k] != second["colors"][mapping[k]]
                    for k in range(6)
                ):
                    specifications.append(
                        (candidate_score(first, second), i, j, mapping)
                    )
    specifications.sort(reverse=True)

    candidates = []
    seen = set()
    pair_maps_checked = 0
    for score, i, j, mapping in specifications:
        if len(candidates) >= args.candidate_cap:
            break
        first, second = sparse[i], sparse[j]
        graph = glue_patch_records(
            parents[int(first["graph_index"])],
            first,
            parents[int(second["graph_index"])],
            second,
            mapping,
        )
        pair_maps_checked += 1
        planar, _ = nx.check_planarity(graph)
        cheap_valid = (
            nx.number_of_selfloops(graph) == 0
            and all(degree == 3 for _, degree in graph.degree())
            and nx.is_bipartite(graph)
            and planar
        )
        if not cheap_valid:
            continue
        encoded = nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()
        if encoded in seen:
            continue
        seen.add(encoded)
        candidates.append(
            {
                "rank": len(candidates) + 1,
                "score": score,
                "patch1": first["key"],
                "patch2": second["key"],
                "mapping": list(mapping),
                "patch1_n": first["patch_n"],
                "patch2_n": second["patch_n"],
                "matching_fragmentation_sum": (
                    first["best_components"] + second["best_components"]
                ),
                "n": graph.number_of_nodes(),
                "m": graph.number_of_edges(),
                "graph6": encoded,
                "cheap_predicates": {
                    "simple": nx.number_of_selfloops(graph) == 0,
                    "cubic": all(degree == 3 for _, degree in graph.degree()),
                    "bipartite": nx.is_bipartite(graph),
                    "planar": planar,
                },
            }
        )

    solve_candidates = candidates[: args.solve_cap]
    payloads = [
        (
            candidate,
            args.milp_time,
            args.wall_time,
            args.seed + candidate["rank"],
            str(Path(__file__).resolve()),
        )
        for candidate in solve_candidates
    ]
    results: dict[int, dict[str, Any]] = {}
    with cf.ThreadPoolExecutor(max_workers=args.workers) as executor:
        for rank, result in executor.map(run_child, payloads):
            results[rank] = result
            print(
                json.dumps(
                    {
                        "rank": rank,
                        "status": result.get("status"),
                        "hamiltonian": result.get("hamiltonian"),
                        "elapsed_s": result.get("elapsed_s"),
                        "valid": (
                            result.get("cycle_validation", {}) or {}
                        ).get("valid"),
                    }
                ),
                flush=True,
            )

    positive = 0
    provisional = []
    unknown = []
    invalid_positive = []
    for candidate in solve_candidates:
        result = results[candidate["rank"]]
        validation = result.get("cycle_validation") or {}
        if result.get("hamiltonian") is True and validation.get("valid"):
            positive += 1
        elif result.get("hamiltonian") is False:
            graph = nx.from_graph6_bytes(candidate["graph6"].encode("ascii"))
            candidate["vertex_connectivity"] = nx.node_connectivity(graph)
            provisional.append(candidate["rank"])
        elif result.get("hamiltonian") is True:
            invalid_positive.append(candidate["rank"])
        else:
            graph = nx.from_graph6_bytes(candidate["graph6"].encode("ascii"))
            candidate["vertex_connectivity"] = nx.node_connectivity(graph)
            unknown.append(candidate["rank"])

    summary = {
        "source_zero_observed_state_patches": len(sparse),
        "raw_pair_maps": len(specifications),
        "pair_maps_checked_for_candidate_pool": pair_maps_checked,
        "unique_structurally_valid_candidates": len(candidates),
        "exact_hamiltonicity_attempts": len(solve_candidates),
        "validated_hamiltonian_cycles": positive,
        "provisional_infeasible": len(provisional),
        "unknown": len(unknown),
        "invalid_positive_witnesses": len(invalid_positive),
        "provisional_candidate_ranks": provisional,
        "unknown_candidate_ranks": unknown,
        "invalid_positive_ranks": invalid_positive,
        "elapsed_s": time.time() - started,
        "counterexample_found": False,
    }
    output = {
        "classification_policy": {
            "positive": "explicit Hamiltonian cycle independently validated",
            "infeasible": "provisional only; proof-producing SAT required",
            "timeout_or_failure": "unknown",
        },
        "parameters": vars(args)
        | {"input": str(args.input), "output": str(args.output)},
        "summary": summary,
        "candidates": candidates,
        "results": {str(rank): result for rank, result in sorted(results.items())},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
