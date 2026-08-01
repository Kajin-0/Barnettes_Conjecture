#!/usr/bin/env python3
"""Search natural cyclic-6-cut patches through matching-complement states.

A six-terminal Hamiltonian boundary state is a spanning collection of one,
two, or three disjoint paths. Its omitted internal edges form a matching that
saturates every internal vertex and every used terminal while leaving unused
terminals exposed. For an exposed set E, this matching is a perfect matching
of P-E.

This program samples those matchings, records independently validated positive
states, deepens sparse signatures, and compares patch signatures under all
bipartition-preserving dihedral boundary maps. Sampling misses and observed
zero compatibility are provisional only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import itertools
import json
import platform
import time
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import scipy
from scipy.optimize import linear_sum_assignment


def ce(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def g6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()


def canonical_cycle(cycle: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    values = list(cycle)
    n = len(values)
    reverse = list(reversed(values))
    return min(
        [tuple(values[i:] + values[:i]) for i in range(n)]
        + [tuple(reverse[i:] + reverse[:i]) for i in range(n)]
    )


def undirected_cycles_of_length(graph: nx.Graph, length: int) -> list[tuple[int, ...]]:
    found: set[tuple[int, ...]] = set()
    for start in sorted(graph):
        def dfs(path: list[int], used: set[int]) -> None:
            current = path[-1]
            if len(path) == length:
                if graph.has_edge(current, start):
                    found.add(canonical_cycle(path))
                return
            for neighbor in graph.neighbors(current):
                if neighbor == start or neighbor in used or neighbor < start:
                    continue
                dfs(path + [neighbor], used | {neighbor})
        dfs([start], {start})
    return sorted(found)


def dual_data(graph: nx.Graph):
    planar, embedding = nx.check_planarity(graph)
    if not planar:
        raise ValueError("nonplanar input")
    seen: set[tuple[int, int]] = set()
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
    for u, v in graph.edges():
        a = dart_face[(u, v)]
        b = dart_face[(v, u)]
        key = ce(a, b)
        if key in edge_map:
            raise ValueError("parallel dual edges are not supported by this pilot")
        dual.add_edge(a, b)
        edge_map[key] = ce(u, v)
    return dual, edge_map


def components_ignoring_edges(
    graph: nx.Graph, cut_edges: list[tuple[int, int]]
) -> list[set[int]]:
    cut = {ce(*edge) for edge in cut_edges}
    unseen = set(graph)
    components: list[set[int]] = []
    while unseen:
        root = next(iter(unseen))
        unseen.remove(root)
        component = {root}
        stack = [root]
        while stack:
            u = stack.pop()
            for v in graph.neighbors(u):
                if ce(u, v) in cut or v not in unseen:
                    continue
                unseen.remove(v)
                component.add(v)
                stack.append(v)
        components.append(component)
        if len(components) > 2:
            break
    return components


def enumerate_cyclic_six_cut_sides(
    graph: nx.Graph, graph_index: int
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    dual, edge_map = dual_data(graph)
    dual_cycles = undirected_cycles_of_length(dual, 6)
    cuts: dict[tuple[tuple[int, int], ...], dict[str, Any]] = {}

    for cycle in dual_cycles:
        dual_edges = [ce(cycle[i], cycle[(i + 1) % 6]) for i in range(6)]
        ordered_cut = [edge_map[edge] for edge in dual_edges]
        cut_key = tuple(sorted(ordered_cut))
        if cut_key in cuts:
            continue
        components = components_ignoring_edges(graph, ordered_cut)
        if len(components) != 2:
            continue
        sides = []
        valid = True
        for component in components:
            internal_edges = sum(
                1 for u, v in graph.edges() if u in component and v in component
            )
            if internal_edges < len(component):
                valid = False
            terminals: list[int] = []
            owners: list[int] = []
            for u, v in ordered_cut:
                if u in component:
                    terminals.append(u)
                    owners.append(v)
                elif v in component:
                    terminals.append(v)
                    owners.append(u)
                else:
                    valid = False
            if len(set(terminals)) != 6:
                valid = False
            sides.append(
                {
                    "nodes": sorted(component),
                    "terminals": terminals,
                    "owners": owners,
                }
            )
        if valid:
            cuts[cut_key] = {
                "dual_cycle": list(cycle),
                "cut_edges": [list(edge) for edge in ordered_cut],
                "sides": sides,
            }

    tasks: list[dict[str, Any]] = []
    for cut_index, cut in enumerate(cuts.values()):
        for side_index, side in enumerate(cut["sides"]):
            tasks.append(
                {
                    "key": f"g{graph_index}-c{cut_index}-s{side_index}",
                    "graph_index": graph_index,
                    "cut_index": cut_index,
                    "side_index": side_index,
                    "dual_cycle": cut["dual_cycle"],
                    "cut_edges": cut["cut_edges"],
                    "side": side,
                }
            )
    keys = [task["key"] for task in tasks]
    if len(keys) != len(set(keys)):
        raise RuntimeError("six-terminal task-key collision")
    return tasks, {
        "dual_six_cycles": len(dual_cycles),
        "cyclic_six_cuts": len(cuts),
        "patch_sides": len(tasks),
    }


def feasible_exposed_sets(
    patch: nx.Graph, terminals: tuple[int, ...]
) -> tuple[list[tuple[int, ...]], dict[int, int]]:
    color = nx.bipartite.color(patch)
    feasible: list[tuple[int, ...]] = []
    for exposed_count in (0, 2, 4):
        for exposed_indices in itertools.combinations(range(6), exposed_count):
            exposed = {terminals[i] for i in exposed_indices}
            left = sum(c == 0 and v not in exposed for v, c in color.items())
            right = sum(c == 1 and v not in exposed for v, c in color.items())
            if left == right:
                feasible.append(tuple(exposed_indices))
    return feasible, color


def canonical_pairing(pairs: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(ce(a, b) for a, b in pairs))


def state_key(
    components: list[set[int]],
    terminals: tuple[int, ...],
    exposed_indices: tuple[int, ...],
) -> tuple[str | None, tuple[tuple[int, int], ...] | None]:
    used = set(range(6)) - set(exposed_indices)
    pairs: list[tuple[int, int]] = []
    for component in components:
        endpoint_indices = sorted(
            i for i, terminal in enumerate(terminals)
            if i in used and terminal in component
        )
        if len(endpoint_indices) == 2:
            pairs.append((endpoint_indices[0], endpoint_indices[1]))
        elif endpoint_indices:
            return None, None
    if len(pairs) != len(used) // 2:
        return None, None
    pairing = canonical_pairing(pairs)
    key = (
        "U"
        + "".join(map(str, sorted(used)))
        + "_"
        + "_".join(f"{a}{b}" for a, b in pairing)
    )
    return key, pairing


def validate_state_witness(
    patch: nx.Graph,
    terminals: tuple[int, ...],
    exposed_indices: tuple[int, ...],
    selected_edges: list[tuple[int, int]],
    expected_pairing: tuple[tuple[int, int], ...],
) -> dict[str, Any]:
    selected = {ce(*edge) for edge in selected_edges}
    patch_edges = {ce(*edge) for edge in patch.edges()}
    subgraph = nx.Graph()
    subgraph.add_nodes_from(patch)
    subgraph.add_edges_from(selected)
    exposed = set(exposed_indices)
    terminal_index = {terminal: i for i, terminal in enumerate(terminals)}
    degree_ok = True
    for vertex in patch:
        if vertex in terminal_index:
            expected_degree = 2 if terminal_index[vertex] in exposed else 1
        else:
            expected_degree = 2
        degree_ok &= subgraph.degree(vertex) == expected_degree
    components = list(nx.connected_components(subgraph))
    key, actual_pairing = state_key(components, terminals, exposed_indices)
    checks = {
        "all_edges_in_patch": selected <= patch_edges,
        "no_duplicate_edges": len(selected_edges) == len(selected),
        "degree_constraints": bool(degree_ok),
        "components": len(components),
        "expected_components": (6 - len(exposed_indices)) // 2,
        "actual_pairing": actual_pairing,
        "expected_pairing": expected_pairing,
        "pairing_matches": actual_pairing == expected_pairing,
        "state_key": key,
    }
    checks["valid"] = (
        checks["all_edges_in_patch"]
        and checks["no_duplicate_edges"]
        and checks["degree_constraints"]
        and checks["components"] == checks["expected_components"]
        and checks["pairing_matches"]
    )
    return checks


def sample_task(payload):
    graph6, task, trials, seed, retain_edges = payload
    graph = nx.from_graph6_bytes(graph6.encode("ascii"))
    side = task["side"]
    patch = graph.subgraph(side["nodes"]).copy()
    terminals = tuple(int(v) for v in side["terminals"])
    exposed_options, color = feasible_exposed_sets(patch, terminals)
    rng = np.random.default_rng(seed)
    states: dict[str, Any] = {}
    best_components = 10**9
    invalid_witnesses = 0

    for trial in range(trials):
        exposed_indices = exposed_options[int(rng.integers(len(exposed_options)))]
        exposed_vertices = {terminals[i] for i in exposed_indices}
        left = sorted(
            v for v, c in color.items() if c == 0 and v not in exposed_vertices
        )
        right = sorted(
            v for v, c in color.items() if c == 1 and v not in exposed_vertices
        )
        right_index = {v: i for i, v in enumerate(right)}
        allowed = np.zeros((len(left), len(right)), dtype=bool)
        for i, u in enumerate(left):
            for v in patch.neighbors(u):
                if v in right_index:
                    allowed[i, right_index[v]] = True
        cost = np.full(allowed.shape, 1.0e12)
        cost[allowed] = rng.exponential(size=int(allowed.sum()))
        rows, columns = linear_sum_assignment(cost)
        if any(not allowed[i, j] for i, j in zip(rows, columns)):
            continue
        matching = {ce(left[i], right[j]) for i, j in zip(rows, columns)}
        selected_edges = [
            ce(*edge) for edge in patch.edges() if ce(*edge) not in matching
        ]
        subgraph = nx.Graph()
        subgraph.add_nodes_from(patch)
        subgraph.add_edges_from(selected_edges)
        components = list(nx.connected_components(subgraph))
        best_components = min(best_components, len(components))
        key, pairing = state_key(components, terminals, exposed_indices)
        if key is None or key in states:
            continue
        validation = validate_state_witness(
            patch, terminals, exposed_indices, selected_edges, pairing
        )
        if not validation["valid"]:
            invalid_witnesses += 1
            continue
        witness = {
            "trial": trial + 1,
            "exposed_indices": list(exposed_indices),
            "pairing": [list(pair) for pair in pairing],
            "selected_edge_sha256": hashlib.sha256(
                json.dumps(sorted(selected_edges), separators=(",", ":")).encode()
            ).hexdigest(),
            "validation": validation,
        }
        if retain_edges:
            witness["selected_edges"] = [list(edge) for edge in sorted(selected_edges)]
        states[key] = witness

    return {
        "key": task["key"],
        "graph_index": task["graph_index"],
        "cut_index": task["cut_index"],
        "side_index": task["side_index"],
        "patch_n": patch.number_of_nodes(),
        "patch_m": patch.number_of_edges(),
        "colors": [int(color[t]) for t in terminals],
        "terminals": list(terminals),
        "nodes": side["nodes"],
        "cut_edges": task["cut_edges"],
        "states": states,
        "state_count": len(states),
        "best_components": best_components,
        "trials": trials,
        "invalid_witnesses": invalid_witnesses,
    }


def dihedral_maps() -> list[tuple[int, ...]]:
    rotations = {
        tuple((i + rotation) % 6 for i in range(6)) for rotation in range(6)
    }
    reflections = {
        tuple((rotation - i) % 6 for i in range(6)) for rotation in range(6)
    }
    return sorted(rotations | reflections)


def parse_state(key: str):
    used_text, pairing_text = key.split("_", 1)
    used = tuple(map(int, used_text[1:]))
    pairing = tuple(tuple(map(int, item)) for item in pairing_text.split("_"))
    return used, pairing


def states_compatible(state1: str, state2: str, mapping: tuple[int, ...]) -> bool:
    used1, pairing1 = parse_state(state1)
    used2, pairing2 = parse_state(state2)
    if tuple(sorted(mapping[i] for i in used1)) != tuple(sorted(used2)):
        return False
    inverse = {mapping[i]: i for i in range(6)}
    pairing2_back = [ce(inverse[a], inverse[b]) for a, b in pairing2]
    union = nx.MultiGraph()
    union.add_nodes_from(used1)
    union.add_edges_from(pairing1)
    union.add_edges_from(pairing2_back)
    return (
        bool(used1)
        and nx.is_connected(nx.Graph(union))
        and all(union.degree(vertex) == 2 for vertex in used1)
    )


def compatibility_summary(results: list[dict[str, Any]]):
    groups: dict[tuple[tuple[int, ...], frozenset[str]], list[str]] = {}
    for result in results:
        group_key = (tuple(result["colors"]), frozenset(result["states"]))
        groups.setdefault(group_key, []).append(result["key"])
    group_items = list(groups.items())
    universe = sorted(
        set().union(*(set(result["states"]) for result in results))
    )
    maps = dihedral_maps()
    compatibility = {
        mapping: {
            state1: {
                state2 for state2 in universe
                if states_compatible(state1, state2, mapping)
            }
            for state1 in universe
        }
        for mapping in maps
    }
    histogram = Counter()
    zero_candidates = []
    minimum = None
    pair_maps = 0

    for i, ((colors1, states1), keys1) in enumerate(group_items):
        for j in range(i, len(group_items)):
            (colors2, states2), keys2 = group_items[j]
            for mapping in maps:
                if not all(colors1[k] != colors2[mapping[k]] for k in range(6)):
                    continue
                count = sum(
                    len(compatibility[mapping][state1] & states2)
                    for state1 in states1
                )
                histogram[count] += 1
                pair_maps += 1
                minimum = count if minimum is None else min(minimum, count)
                if count == 0:
                    zero_candidates.append(
                        {
                            "group1": i,
                            "group2": j,
                            "representative_patch1": keys1[0],
                            "representative_patch2": keys2[0],
                            "mapping": list(mapping),
                            "group1_size": len(keys1),
                            "group2_size": len(keys2),
                        }
                    )
    return {
        "state_universe_size": len(universe),
        "signature_groups": len(groups),
        "pair_maps": pair_maps,
        "minimum_observed_compatibility": minimum,
        "compatibility_histogram": dict(sorted(histogram.items())),
        "zero_observed_compatibility_maps": len(zero_candidates),
        "zero_candidates": zero_candidates,
    }


def run_payloads(payloads, workers):
    results = []
    with cf.ProcessPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(sample_task, payloads, chunksize=2):
            results.append(result)
            print(
                json.dumps(
                    {
                        "patch": result["key"],
                        "n": result["patch_n"],
                        "states": result["state_count"],
                        "best_components": result["best_components"],
                    }
                ),
                flush=True,
            )
    keys = [result["key"] for result in results]
    if len(keys) != len(set(keys)):
        raise RuntimeError("duplicate six-terminal result keys")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, required=True)
    parser.add_argument("--graphs", type=int, default=8)
    parser.add_argument("--trials", type=int, default=64)
    parser.add_argument("--deep-count", type=int, default=100)
    parser.add_argument("--deep-trials", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.time()
    verified = json.loads(args.verified.read_text(encoding="utf-8"))
    records = verified["results"][: args.graphs]
    graph_records = {}
    tasks = []
    graph6_by_index = {}

    for record in records:
        graph_index = int(record["pool_index"])
        graph = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
        graph_tasks, metrics = enumerate_cyclic_six_cut_sides(graph, graph_index)
        tasks.extend(graph_tasks)
        graph6_by_index[graph_index] = record["graph6"]
        graph_records[str(graph_index)] = {
            "n": graph.number_of_nodes(),
            "m": graph.number_of_edges(),
            "graph6": record["graph6"],
            "sha256": hashlib.sha256(record["graph6"].encode()).hexdigest(),
            **metrics,
        }
        print(json.dumps({"graph": graph_index, **metrics}), flush=True)

    payloads = [
        (
            graph6_by_index[int(task["graph_index"])],
            task,
            args.trials,
            args.seed + index,
            False,
        )
        for index, task in enumerate(tasks)
    ]
    results = run_payloads(payloads, args.workers)
    result_by_key = {result["key"]: result for result in results}
    task_by_key = {task["key"]: task for task in tasks}

    sparse = sorted(
        results,
        key=lambda result: (
            result["state_count"],
            result["best_components"],
            -result["patch_n"],
            result["key"],
        ),
    )[: args.deep_count]
    deep_payloads = [
        (
            graph6_by_index[int(result["graph_index"])],
            task_by_key[result["key"]],
            args.deep_trials,
            args.seed + 10_000_000 + index,
            True,
        )
        for index, result in enumerate(sparse)
    ]
    deep_results = run_payloads(deep_payloads, args.workers) if deep_payloads else []
    for deep in deep_results:
        original = result_by_key[deep["key"]]
        merged_states = dict(original["states"])
        merged_states.update(deep["states"])
        deep["states"] = merged_states
        deep["state_count"] = len(merged_states)
        deep["initial_state_count"] = original["state_count"]
        deep["best_components"] = min(
            original["best_components"], deep["best_components"]
        )
        result_by_key[deep["key"]] = deep
    results = [result_by_key[key] for key in sorted(result_by_key)]

    compatibility = compatibility_summary(results)
    state_counts = Counter(result["state_count"] for result in results)
    summary = {
        "campaign": "six-terminal-matching-interface-pilot",
        "graphs": len(records),
        "patch_sides": len(results),
        "initial_trials_per_patch": args.trials,
        "deepened_patches": len(deep_results),
        "deep_trials_per_patch": args.deep_trials,
        "minimum_observed_states": min(state_counts) if state_counts else None,
        "maximum_observed_states": max(state_counts) if state_counts else None,
        "state_count_histogram": dict(sorted(state_counts.items())),
        "invalid_sampled_witnesses": sum(
            result["invalid_witnesses"] for result in results
        ),
        "elapsed_s": time.time() - started,
        "counterexample_found": False,
        **{k: v for k, v in compatibility.items() if k != "zero_candidates"},
    }
    output = {
        "status": "heuristic_positive_screen",
        "interpretation": (
            "Observed states are validated positive witnesses. Missing states and "
            "zero observed compatibility are provisional until exact proof-producing "
            "completion."
        ),
        "parameters": vars(args)
        | {"verified": str(args.verified), "output": str(args.output)},
        "software": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "networkx": nx.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "summary": summary,
        "graphs": graph_records,
        "results": results,
        "zero_candidates": compatibility["zero_candidates"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
