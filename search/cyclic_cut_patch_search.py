#!/usr/bin/env python3
"""Exact four-terminal signatures of natural cyclic 4-edge-cut patches.

For a cubic plane graph, a separating 4-cycle in the planar dual corresponds to
a cyclic 4-edge cut in the primal graph.  Each side is a four-terminal patch.
This program computes all nine Hamiltonian boundary states exactly with the
MILP implementation in patch_gluing_search.py, retries timeouts at a longer
budget, and compares every planar bipartition-preserving pair of signatures.

A timeout is always reported as unknown.  Only solver-proven infeasibility is
used to remove a boundary state.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx

import patch_gluing_search as pl


def dual_data(G: nx.Graph):
    planar, embedding = nx.check_planarity(G)
    if not planar:
        raise ValueError("input graph is not planar")
    seen = set()
    dart_face: dict[tuple[int, int], int] = {}
    faces: list[list[int]] = []
    for u, v in embedding.edges():
        if (u, v) in seen:
            continue
        face = embedding.traverse_face(u, v, seen)
        face_index = len(faces)
        faces.append(face)
        for i, a in enumerate(face):
            dart_face[(a, face[(i + 1) % len(face)])] = face_index

    dual = nx.Graph()
    edge_map: dict[tuple[int, int], tuple[int, int]] = {}
    for u, v in G.edges():
        a = dart_face[(u, v)]
        b = dart_face[(v, u)]
        key = tuple(sorted((a, b)))
        dual.add_edge(a, b)
        edge_map[key] = pl.ce(u, v)
    return dual, edge_map


def dual_four_cycles(dual: nx.Graph):
    seen = set()
    for u, v in itertools.combinations(sorted(dual), 2):
        common = sorted(set(dual[u]) & set(dual[v]))
        for a, b in itertools.combinations(common, 2):
            cycle = (u, a, v, b)
            edges = tuple(
                tuple(sorted(edge))
                for edge in ((u, a), (a, v), (v, b), (b, u))
            )
            key = frozenset(edges)
            if key not in seen:
                seen.add(key)
                yield cycle, edges


def enumerate_patch_tasks(G: nx.Graph, graph_index: int):
    dual, edge_map = dual_data(G)
    color = nx.bipartite.color(G)
    cuts: dict[tuple[tuple[int, int], ...], dict[str, Any]] = {}

    for dual_cycle, dual_edges in dual_four_cycles(dual):
        ordered_cut = [edge_map[edge] for edge in dual_edges]
        cut_key = tuple(sorted(ordered_cut))
        if cut_key in cuts:
            continue

        remainder = G.copy()
        remainder.remove_edges_from(ordered_cut)
        components = list(nx.connected_components(remainder))
        if len(components) != 2:
            continue
        if not all(
            remainder.subgraph(component).number_of_edges() >= len(component)
            for component in components
        ):
            continue

        sides = []
        valid = True
        for component in components:
            terminals = []
            owners = []
            for u, v in ordered_cut:
                if u in component:
                    terminals.append(u)
                    owners.append(v)
                elif v in component:
                    terminals.append(v)
                    owners.append(u)
                else:
                    valid = False
            if len(set(terminals)) != 4:
                valid = False
            sides.append(
                {
                    "nodes": sorted(component),
                    "terminals": terminals,
                    "owners": owners,
                    "colors": [int(color[t]) for t in terminals],
                }
            )

        if valid:
            cuts[cut_key] = {
                "dual_cycle": list(dual_cycle),
                "cut_edges": [list(edge) for edge in ordered_cut],
                "sides": sides,
            }

    tasks = []
    for cut_index, cut in enumerate(cuts.values()):
        for side_index, side in enumerate(cut["sides"]):
            tasks.append(
                {
                    "key": f"c{cut_index}-s{side_index}",
                    "graph_index": graph_index,
                    "cut_index": cut_index,
                    "side_index": side_index,
                    "cut": cut,
                    "side": side,
                }
            )
    return tasks, len(cuts)


def solve_task(payload):
    graph6, task, time_limit = payload
    G = nx.from_graph6_bytes(graph6.encode())
    side = task["side"]
    patch = G.subgraph(side["nodes"]).copy()
    marker = 1_000_000 + 2 * task["cut_index"] + task["side_index"]
    spec = pl.PatchSpec(
        graph_index=task["graph_index"],
        removed_edge=(marker, marker + 10_000_000),
        terminals=tuple(side["terminals"]),
        terminal_owner=tuple(side["owners"]),
        terminal_colors=tuple(side["colors"]),
    )
    signature = pl.exact_signature(patch, spec, time_limit)
    return task["key"], signature


def restore_spec(signature):
    raw = signature["patch"]
    return pl.PatchSpec(
        graph_index=int(raw["graph_index"]),
        removed_edge=tuple(raw["removed_edge"]),
        terminals=tuple(raw["terminals"]),
        terminal_owner=tuple(raw["terminal_owner"]),
        terminal_colors=tuple(raw["terminal_colors"]),
    )


def compatibility_summary(signatures):
    groups = Counter()
    for signature in signatures.values():
        spec = restore_spec(signature)
        groups[(spec.terminal_colors, tuple(signature["feasible_states"]))] += 1

    pair_maps = 0
    histogram = Counter()
    incompatible = 0
    grouped = list(groups.items())
    for i, ((colors1, states1), count1) in enumerate(grouped):
        for j in range(i, len(grouped)):
            (colors2, states2), count2 = grouped[j]
            number_of_pairs = (
                count1 * count2
                if i != j
                else count1 * (count1 + 1) // 2
            )
            for mapping in pl.dihedral_maps():
                if not all(
                    colors1[k] != colors2[mapping[k]] for k in range(4)
                ):
                    continue
                compatible = len(
                    pl.compatible_states(states1, states2, mapping)
                )
                pair_maps += number_of_pairs
                histogram[compatible] += number_of_pairs
                if compatible == 0:
                    incompatible += number_of_pairs

    return {
        "signature_groups": len(groups),
        "pair_maps": pair_maps,
        "compatibility_histogram": dict(sorted(histogram.items())),
        "minimum_compatibility": min(histogram) if histogram else None,
        "incompatible_pair_maps": incompatible,
    }


def run_batch(graph6, tasks, time_limit, workers):
    output = {}
    payloads = [(graph6, task, time_limit) for task in tasks]
    with cf.ProcessPoolExecutor(max_workers=workers) as executor:
        for key, signature in executor.map(solve_task, payloads):
            output[key] = signature
            print(
                json.dumps(
                    {
                        "patch": key,
                        "complete": signature["complete"],
                        "feasible_states": signature["feasible_states"],
                        "unknown_states": signature["unknown_states"],
                    }
                ),
                flush=True,
            )
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, required=True)
    parser.add_argument("--graph-index", type=int, default=0)
    parser.add_argument("--state-time", type=float, default=5.0)
    parser.add_argument("--retry-time", type=float, default=90.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.verified.read_text(encoding="utf-8"))["results"]
    record = data[args.graph_index]
    graph6 = record["graph6"]
    graph = nx.from_graph6_bytes(graph6.encode())
    tasks, number_of_cuts = enumerate_patch_tasks(graph, args.graph_index)
    task_by_key = {task["key"]: task for task in tasks}

    signatures = run_batch(graph6, tasks, args.state_time, args.workers)
    unknown_keys = [
        key for key, signature in signatures.items() if not signature["complete"]
    ]
    if unknown_keys:
        retries = run_batch(
            graph6,
            [task_by_key[key] for key in unknown_keys],
            args.retry_time,
            args.workers,
        )
        signatures.update(retries)

    unresolved = [
        key for key, signature in signatures.items() if not signature["complete"]
    ]
    complete = {
        key: signature
        for key, signature in signatures.items()
        if signature["complete"]
    }
    restrictive = {
        key: {
            "task": task_by_key[key],
            "signature": signature,
        }
        for key, signature in complete.items()
        if len(signature["feasible_states"]) < 6
    }

    summary = {
        "graph_index": args.graph_index,
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "cyclic_four_cuts": number_of_cuts,
        "patch_sides": len(tasks),
        "complete_signatures": len(complete),
        "unresolved_signatures": len(unresolved),
        "signature_size_counts": dict(
            Counter(len(signature["feasible_states"]) for signature in complete.values())
        ),
        "restrictive_patches": len(restrictive),
        **compatibility_summary(complete),
    }

    result = {
        "parameters": {
            "verified": str(args.verified),
            "graph_index": args.graph_index,
            "state_time": args.state_time,
            "retry_time": args.retry_time,
            "workers": args.workers,
        },
        "parent_graph6": graph6,
        "summary": summary,
        "restrictive": restrictive,
        "unresolved": unresolved,
        "signatures": signatures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
