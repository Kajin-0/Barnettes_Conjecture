#!/usr/bin/env python3
"""Q-first exact screening of natural cyclic-4-cut Barnette patches.

For each retained canonical graph, enumerate natural cyclic 4-edge cuts and
select a deterministic, structurally diverse subset of cut sides. Test only
the two noncrossing two-path boundary states first:

    Q01_23 and Q03_12.

Positive MILP outputs are accepted only after an independent combinatorial
witness check. Solver infeasibility is *provisional* and is exported for a
separate proof-producing SAT verification. Timeouts and solver errors remain
unknown.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import platform
import time
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import scipy

import patch_gluing_search as pl
from cyclic_cut_patch_search import enumerate_patch_tasks

NONCROSSING_Q = [
    ((0, 1), (2, 3)),
    ((0, 3), (1, 2)),
]


def validate_pair_witness(
    patch: nx.Graph,
    terminals: tuple[int, int, int, int],
    pairing: pl.Pairing,
    selected_edges: list[list[int]] | list[tuple[int, int]] | None,
) -> dict[str, Any]:
    if selected_edges is None:
        return {"valid": False, "reason": "missing selected-edge witness"}
    edges = [pl.ce(int(u), int(v)) for u, v in selected_edges]
    edge_set = set(edges)
    patch_edges = {pl.ce(*edge) for edge in patch.edges()}
    H = nx.Graph()
    H.add_nodes_from(patch)
    H.add_edges_from(edges)
    terminal_set = set(terminals)
    degree_ok = all(
        H.degree(v) == (1 if v in terminal_set else 2)
        for v in patch
    )
    components = list(nx.connected_components(H))
    actual_pairs: list[tuple[int, int]] = []
    for component in components:
        indices = sorted(i for i, terminal in enumerate(terminals) if terminal in component)
        if len(indices) == 2:
            actual_pairs.append(tuple(indices))
    actual = pl.canonical_pairing(actual_pairs) if len(actual_pairs) == 2 else None
    expected = pl.canonical_pairing(pairing)
    checks = {
        "all_edges_in_patch": edge_set <= patch_edges,
        "no_duplicate_edges": len(edges) == len(edge_set),
        "selected_edge_count": len(edges),
        "expected_edge_count": patch.number_of_nodes() - 2,
        "degree_constraints": degree_ok,
        "components": len(components),
        "actual_pairing": actual,
        "expected_pairing": expected,
        "pairing_matches": actual == expected,
    }
    checks["valid"] = all(
        checks[key]
        for key in (
            "all_edges_in_patch",
            "no_duplicate_edges",
            "degree_constraints",
            "pairing_matches",
        )
    ) and checks["components"] == 2 and checks["selected_edge_count"] == checks["expected_edge_count"]
    return checks


def select_patch_tasks(tasks: list[dict[str, Any]], n: int, limit: int) -> list[dict[str, Any]]:
    """Deterministically retain balanced cuts while preserving side-size diversity."""
    if len(tasks) <= limit:
        return tasks
    by_size: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        size = len(task["side"]["nodes"])
        by_size[size].append(task)
    for group in by_size.values():
        group.sort(key=lambda task: task["key"])

    sizes = sorted(by_size, key=lambda size: (abs(size - n / 2.0), -min(size, n - size), size))
    selected: list[dict[str, Any]] = []
    cursor = {size: 0 for size in sizes}
    while len(selected) < limit:
        advanced = False
        for size in sizes:
            index = cursor[size]
            if index < len(by_size[size]):
                selected.append(by_size[size][index])
                cursor[size] += 1
                advanced = True
                if len(selected) >= limit:
                    break
        if not advanced:
            break
    return selected


def solve_payload(payload: tuple[str, dict[str, Any], float]) -> tuple[str, dict[str, Any]]:
    graph6, task, time_limit = payload
    graph = nx.from_graph6_bytes(graph6.encode("ascii"))
    side = task["side"]
    patch = graph.subgraph(side["nodes"]).copy()
    marker = 10_000_000 + 2 * int(task["cut_index"]) + int(task["side_index"])
    spec = pl.PatchSpec(
        graph_index=int(task["graph_index"]),
        removed_edge=(marker, marker + 1),
        terminals=tuple(int(x) for x in side["terminals"]),
        terminal_owner=tuple(int(x) for x in side["owners"]),
        terminal_colors=tuple(int(x) for x in side["colors"]),
    )
    states: dict[str, Any] = {}
    for pairing in NONCROSSING_Q:
        key = pl.pair_key(pairing)
        result = pl.solve_pair_state(patch, spec, pairing, time_limit)
        result_dict = asdict(result)
        validation = validate_pair_witness(
            patch,
            spec.terminals,
            pairing,
            result_dict.get("selected_edges"),
        ) if result.feasible else None
        if result.feasible and not validation["valid"]:
            result_dict["status"] = "invalid_witness"
            result_dict["feasible"] = None
        states[key] = {
            "solver": result_dict,
            "witness_validation": validation,
        }
    return task["key"], {
        "task": task,
        "patch_graph6": nx.to_graph6_bytes(
            nx.convert_node_labels_to_integers(patch, ordering="sorted"),
            header=False,
        ).decode("ascii").strip(),
        "patch_nodes": sorted(int(v) for v in patch),
        "patch_n": patch.number_of_nodes(),
        "patch_m": patch.number_of_edges(),
        "spec": asdict(spec),
        "states": states,
    }


def run_batch(
    graph6_by_index: dict[int, str],
    tasks: list[dict[str, Any]],
    time_limit: float,
    workers: int,
) -> dict[str, dict[str, Any]]:
    payloads = [(graph6_by_index[int(task["graph_index"])], task, time_limit) for task in tasks]
    results: dict[str, dict[str, Any]] = {}
    with cf.ProcessPoolExecutor(max_workers=workers) as executor:
        for key, result in executor.map(solve_payload, payloads, chunksize=1):
            results[key] = result
            compact = {
                state: data["solver"]["status"]
                for state, data in result["states"].items()
            }
            print(json.dumps({"patch": key, "n": result["patch_n"], "states": compact}), flush=True)
    return results


def state_classification(state: dict[str, Any]) -> str:
    solver = state["solver"]
    validation = state.get("witness_validation")
    if solver.get("feasible") is True and validation and validation.get("valid"):
        return "verified_positive"
    if solver.get("feasible") is False:
        return "provisional_negative"
    return "unknown"


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
    graph6_by_index = {int(record["pool_index"]): record["graph6"] for record in source_records}

    selected_tasks: list[dict[str, Any]] = []
    graph_metadata: dict[str, Any] = {}
    for record in source_records:
        graph_index = int(record["pool_index"])
        graph = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
        tasks, cut_count = enumerate_patch_tasks(graph, graph_index)
        selected = select_patch_tasks(tasks, graph.number_of_nodes(), args.patches_per_graph)
        selected_tasks.extend(selected)
        graph_metadata[str(graph_index)] = {
            "n": graph.number_of_nodes(),
            "m": graph.number_of_edges(),
            "cyclic_four_cuts": cut_count,
            "available_patch_sides": len(tasks),
            "selected_patch_sides": len(selected),
            "selected_size_histogram": dict(sorted(Counter(len(task["side"]["nodes"]) for task in selected).items())),
            "source_graph_sha256": hashlib.sha256(record["graph6"].encode("ascii")).hexdigest(),
        }

    first = run_batch(graph6_by_index, selected_tasks, args.state_time, args.workers)
    task_by_key = {task["key"]: task for task in selected_tasks}
    retry_keys = [
        key
        for key, result in first.items()
        if any(state_classification(state) != "verified_positive" for state in result["states"].values())
    ]
    if retry_keys:
        print(json.dumps({"retry_patch_count": len(retry_keys), "retry_time": args.retry_time}), flush=True)
        retries = run_batch(
            graph6_by_index,
            [task_by_key[key] for key in retry_keys],
            args.retry_time,
            args.workers,
        )
        first.update(retries)

    counts = Counter()
    candidate_cases: list[dict[str, Any]] = []
    for key, result in sorted(first.items()):
        for state_key, state in sorted(result["states"].items()):
            classification = state_classification(state)
            counts[classification] += 1
            if classification != "verified_positive":
                candidate_cases.append({
                    "case_id": f"{key}-{state_key}",
                    "classification": classification,
                    "parent_graph6": graph6_by_index[int(result["task"]["graph_index"])],
                    "patch_nodes": result["patch_nodes"],
                    "spec": result["spec"],
                    "state": state_key,
                    "milp_result": state,
                })

    summary = {
        "graphs_analyzed": len(source_records),
        "patch_sides_selected": len(selected_tasks),
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
            "verified_positive": "explicit selected-edge witness passed independent combinatorial validation",
            "provisional_negative": "MILP reported infeasible; not mathematical evidence; independent SAT proof required",
            "unknown": "timeout, solver error, or invalid/missing witness",
        },
        "parameters": vars(args) | {"verified": str(args.verified), "output": str(args.output)},
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
