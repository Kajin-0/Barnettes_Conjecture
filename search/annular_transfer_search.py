#!/usr/bin/env python3
"""Positive-witness search for exact transfer relations between nested cyclic cuts.

The script enumerates every natural cyclic 4-edge cut in selected parent graphs,
finds nested cut-side pairs, and treats the vertices between them as an annular
patch with four inner and four outer terminals.

For each realizable inner/outer boundary-state pair, it solves a connected
2-regular augmented-graph MILP. Positive states are accepted only through an
explicit selected-edge witness. Negative solver statuses remain provisional.
For Q-state inputs already present in a Q-first result file, the abstract core
edges are replaced by the stored core witness and the four real cut edges; the
resulting larger disk patch is then checked against the predicted output state.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import itertools
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix

STATES = {
    "P01": [(0, 1)],
    "P02": [(0, 2)],
    "P03": [(0, 3)],
    "P12": [(1, 2)],
    "P13": [(1, 3)],
    "P23": [(2, 3)],
    "Q01_23": [(0, 1), (2, 3)],
    "Q02_13": [(0, 2), (1, 3)],
    "Q03_12": [(0, 3), (1, 2)],
}
STATE_ORDER = list(STATES)


def ce(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def allowed_disk_states(side: dict, global_color: dict[int, int]) -> list[str]:
    """Return the four parity-allowed P states and two noncrossing Q states."""
    delta = sum(1 if global_color[v] == 0 else -1 for v in side["nodes"])
    colors = list(map(int, side["colors"]))
    allowed: list[str] = []
    for key, pairs in STATES.items():
        if key.startswith("Q"):
            if key in ("Q01_23", "Q03_12"):
                allowed.append(key)
            continue
        i, j = pairs[0]
        ci, cj = colors[i], colors[j]
        if ci != cj and delta == 0:
            allowed.append(key)
        elif ci == cj == 0 and delta == 1:
            allowed.append(key)
        elif ci == cj == 1 and delta == -1:
            allowed.append(key)
    return allowed


def solve_milp(
    c: np.ndarray,
    integrality: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
    rows: list[dict[int, float]],
    lo: list[float],
    hi: list[float],
    time_limit: float,
):
    rr: list[int] = []
    cc: list[int] = []
    dd: list[float] = []
    for row_index, row in enumerate(rows):
        for column, value in row.items():
            rr.append(row_index)
            cc.append(column)
            dd.append(value)
    matrix = csr_matrix((dd, (rr, cc)), shape=(len(rows), len(c)))
    started = time.time()
    result = milp(
        c=c,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(matrix, np.asarray(lo), np.asarray(hi)),
        options={
            "time_limit": float(time_limit),
            "mip_rel_gap": 0.0,
            "presolve": True,
        },
    )
    return result, time.time() - started


def solve_relation(payload: tuple) -> dict:
    (
        graph6,
        annulus_nodes,
        outer_terminals,
        inner_terminals,
        inner_state,
        outer_closure_state,
        time_limit,
    ) = payload
    parent = nx.from_graph6_bytes(graph6.encode("ascii"))
    annulus = parent.subgraph(annulus_nodes).copy()
    nodes = sorted(annulus)
    n = len(nodes)
    edges = sorted(ce(*edge) for edge in annulus.edges())
    edge_index = {edge: i for i, edge in enumerate(edges)}
    m = len(edges)

    artificial: list[tuple[int, int, str]] = []
    for a, b in STATES[outer_closure_state]:
        artificial.append((outer_terminals[a], outer_terminals[b], "outer"))
    for a, b in STATES[inner_state]:
        artificial.append((inner_terminals[a], inner_terminals[b], "inner"))

    artificial_degree: Counter[int] = Counter()
    for u, v, _ in artificial:
        artificial_degree[u] += 1
        artificial_degree[v] += 1
    if any(endpoint not in annulus for u, v, _ in artificial for endpoint in (u, v)):
        return {"classification": "invalid", "reason": "artificial endpoint absent"}

    real_degree_rhs = {v: 2 - artificial_degree[v] for v in nodes}
    if any(value < 0 or value > annulus.degree(v) for v, value in real_degree_rhs.items()):
        return {"classification": "structural_infeasible", "reason": "degree rhs"}

    arcs: list[tuple[str, int, int, int]] = []
    for edge_id, (u, v) in enumerate(edges):
        arcs.extend((("real", u, v, edge_id), ("real", v, u, edge_id)))
    for artificial_id, (u, v, _) in enumerate(artificial):
        arcs.extend((("art", u, v, artificial_id), ("art", v, u, artificial_id)))

    flow_offset = m
    variable_count = m + len(arcs)
    capacity = float(max(n - 1, 1))
    rows: list[dict[int, float]] = []
    lower: list[float] = []
    upper: list[float] = []

    for vertex in nodes:
        rows.append({edge_index[ce(vertex, neighbor)]: 1.0 for neighbor in annulus.neighbors(vertex)})
        lower.append(float(real_degree_rhs[vertex]))
        upper.append(float(real_degree_rhs[vertex]))

    root = nodes[0]
    for vertex in nodes:
        row: dict[int, float] = {}
        for arc_id, (_, source, target, _) in enumerate(arcs):
            if target == vertex:
                row[flow_offset + arc_id] = row.get(flow_offset + arc_id, 0.0) + 1.0
            if source == vertex:
                row[flow_offset + arc_id] = row.get(flow_offset + arc_id, 0.0) - 1.0
        rhs = -(n - 1.0) if vertex == root else 1.0
        rows.append(row)
        lower.append(rhs)
        upper.append(rhs)

    for arc_id, (kind, _, _, index) in enumerate(arcs):
        if kind == "real":
            rows.append({flow_offset + arc_id: 1.0, index: -capacity})
            lower.append(-np.inf)
            upper.append(0.0)
        else:
            rows.append({flow_offset + arc_id: 1.0})
            lower.append(-np.inf)
            upper.append(capacity)

    variable_lb = np.zeros(variable_count)
    variable_ub = np.r_[np.ones(m), np.full(len(arcs), capacity)]
    integrality = np.r_[np.ones(m), np.zeros(len(arcs))]
    result, elapsed = solve_milp(
        np.zeros(variable_count),
        integrality,
        variable_lb,
        variable_ub,
        rows,
        lower,
        upper,
        time_limit,
    )

    if result.x is None:
        classification = "provisional_negative" if result.status == 2 else "unknown"
        return {
            "classification": classification,
            "solver_status": int(result.status),
            "message": str(result.message),
            "elapsed_s": elapsed,
        }

    selected = [edges[i] for i, value in enumerate(result.x[:m]) if value > 0.5]
    witness = nx.MultiGraph()
    witness.add_nodes_from(nodes)
    for edge in selected:
        witness.add_edge(*edge, kind="real")
    for u, v, kind in artificial:
        witness.add_edge(u, v, kind=kind)
    valid = (
        nx.is_connected(witness)
        and all(witness.degree(v) == 2 for v in nodes)
        and all(annulus.has_edge(*edge) for edge in selected)
        and len(selected) == len(set(selected))
    )
    return {
        "classification": "verified_positive" if valid else "unknown",
        "solver_status": int(result.status),
        "message": str(result.message),
        "elapsed_s": elapsed,
        "selected_real_edges": [list(edge) for edge in selected] if valid else None,
        "artificial_edges": [[u, v, kind] for u, v, kind in artificial],
        "validation": {
            "connected": nx.is_connected(witness),
            "all_degree_two": all(witness.degree(v) == 2 for v in nodes),
            "selected_real_edge_count": len(selected),
            "valid": valid,
        },
    }


def enumerate_natural_cut_sides(parent: nx.Graph, graph_index: int):
    planar, embedding = nx.check_planarity(parent)
    if not planar:
        raise ValueError("nonplanar parent")

    seen: set[tuple[int, int]] = set()
    dart_face: dict[tuple[int, int], int] = {}
    faces: list[list[int]] = []
    for u, v in embedding.edges():
        if (u, v) in seen:
            continue
        face = embedding.traverse_face(u, v, seen)
        face_index = len(faces)
        faces.append(face)
        for i, vertex in enumerate(face):
            dart_face[(vertex, face[(i + 1) % len(face)])] = face_index

    dual = nx.Graph()
    edge_map: dict[tuple[int, int], tuple[int, int]] = {}
    for u, v in parent.edges():
        a = dart_face[(u, v)]
        b = dart_face[(v, u)]
        key = tuple(sorted((a, b)))
        dual.add_edge(a, b)
        edge_map[key] = ce(u, v)

    cycles_seen: set[frozenset] = set()
    cuts: dict[tuple, dict] = {}
    for u, v in itertools.combinations(sorted(dual), 2):
        common = sorted(set(dual[u]) & set(dual[v]))
        for a, b in itertools.combinations(common, 2):
            dual_edges = tuple(
                tuple(sorted(edge))
                for edge in ((u, a), (a, v), (v, b), (b, u))
            )
            cycle_key = frozenset(dual_edges)
            if cycle_key in cycles_seen:
                continue
            cycles_seen.add(cycle_key)
            try:
                ordered_cut = [edge_map[edge] for edge in dual_edges]
            except KeyError:
                continue
            cut_key = tuple(sorted(ordered_cut))
            if cut_key in cuts:
                continue

            remainder = parent.copy()
            remainder.remove_edges_from(ordered_cut)
            components = list(nx.connected_components(remainder))
            if len(components) != 2:
                continue
            if not all(
                remainder.subgraph(component).number_of_edges() >= len(component)
                for component in components
            ):
                continue

            sides: list[dict] = []
            valid = True
            color = nx.bipartite.color(parent)
            for component in components:
                terminals: list[int] = []
                owners: list[int] = []
                for x, y in ordered_cut:
                    if x in component:
                        terminals.append(x)
                        owners.append(y)
                    elif y in component:
                        terminals.append(y)
                        owners.append(x)
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
                    "cut_edges": [list(edge) for edge in ordered_cut],
                    "sides": sides,
                }

    tasks: list[dict] = []
    for cut_index, cut in enumerate(cuts.values()):
        for side_index, side in enumerate(cut["sides"]):
            tasks.append(
                {
                    "key": f"g{graph_index}-c{cut_index}-s{side_index}",
                    "graph_index": graph_index,
                    "cut_index": cut_index,
                    "side_index": side_index,
                    "cut": cut,
                    "side": side,
                }
            )
    return tasks, len(cuts)


def load_candidates(verified_path: Path, graph_limit: int, annuli_per_graph: int):
    verified = json.loads(verified_path.read_text(encoding="utf-8"))
    graph6_by_index = {
        int(record["pool_index"]): record["graph6"]
        for record in verified["results"][:graph_limit]
    }
    candidates: list[dict] = []

    for graph_index, graph6 in graph6_by_index.items():
        parent = nx.from_graph6_bytes(graph6.encode("ascii"))
        parent_order = parent.number_of_nodes()
        global_color = nx.bipartite.color(parent)
        tasks, cut_count = enumerate_natural_cut_sides(parent, graph_index)
        by_size: dict[int, list[dict]] = defaultdict(list)
        for task in tasks:
            by_size[len(task["side"]["nodes"])].append(task)
        sizes = sorted(by_size)
        raw: list[dict] = []
        seen: set[tuple] = set()

        for inner_size in sizes:
            for outer_size in sizes:
                if inner_size >= outer_size:
                    continue
                for inner in by_size[inner_size]:
                    inner_nodes = set(inner["side"]["nodes"])
                    for outer in by_size[outer_size]:
                        outer_nodes = set(outer["side"]["nodes"])
                        if not inner_nodes < outer_nodes:
                            continue
                        annulus_nodes = outer_nodes - inner_nodes
                        outer_terminals = tuple(map(int, outer["side"]["terminals"]))
                        inner_terminals = tuple(map(int, inner["side"]["owners"]))
                        if not set(outer_terminals) <= annulus_nodes:
                            continue
                        if not set(inner_terminals) <= annulus_nodes:
                            continue
                        if len(set(outer_terminals + inner_terminals)) != 8:
                            continue
                        if len(annulus_nodes) < 8:
                            continue
                        annulus = parent.subgraph(annulus_nodes)
                        if not nx.is_connected(annulus):
                            continue
                        boundary = set(outer_terminals + inner_terminals)
                        if any(annulus.degree(v) != 2 for v in boundary):
                            continue
                        if any(annulus.degree(v) != 3 for v in annulus_nodes - boundary):
                            continue
                        identity = (frozenset(annulus_nodes), outer_terminals, inner_terminals)
                        if identity in seen:
                            continue
                        seen.add(identity)

                        opposite_outer = outer["cut"]["sides"][1 - int(outer["side_index"])]
                        raw.append(
                            {
                                "graph_index": graph_index,
                                "inner_key": inner["key"],
                                "outer_key": outer["key"],
                                "annulus_nodes": sorted(annulus_nodes),
                                "annulus_n": len(annulus_nodes),
                                "inner_nodes": sorted(inner_nodes),
                                "outer_nodes": sorted(outer_nodes),
                                "inner_cut_edges": inner["cut"]["cut_edges"],
                                "inner_terminals": list(inner_terminals),
                                "outer_terminals": list(outer_terminals),
                                "inner_colors": inner["side"]["colors"],
                                "outer_colors": opposite_outer["colors"],
                                "inner_allowed_states": allowed_disk_states(inner["side"], global_color),
                                "outer_allowed_states": allowed_disk_states(opposite_outer, global_color),
                                "parent_cut_count": cut_count,
                            }
                        )

        candidates_by_size: dict[int, list[dict]] = defaultdict(list)
        for candidate in raw:
            candidates_by_size[candidate["annulus_n"]].append(candidate)
        for group in candidates_by_size.values():
            group.sort(key=lambda candidate: (candidate["inner_key"], candidate["outer_key"]))
        preferred_sizes = sorted(
            candidates_by_size,
            key=lambda size: (abs(size - parent_order / 3.0), -size),
        )
        chosen: list[dict] = []
        cursor = {size: 0 for size in preferred_sizes}
        while len(chosen) < annuli_per_graph:
            advanced = False
            for size in preferred_sizes:
                if cursor[size] < len(candidates_by_size[size]):
                    chosen.append(candidates_by_size[size][cursor[size]])
                    cursor[size] += 1
                    advanced = True
                    if len(chosen) >= annuli_per_graph:
                        break
            if not advanced:
                break
        for index, candidate in enumerate(chosen):
            candidate["annulus_id"] = f"g{graph_index}-a{index:03d}"
        candidates.extend(chosen)

    return graph6_by_index, candidates


def closure_to_actual(state: str) -> str:
    if state == "Q01_23":
        return "Q03_12"
    if state == "Q03_12":
        return "Q01_23"
    return state


def validate_composed_q_witness(
    parent: nx.Graph,
    candidate: dict,
    output_state: str,
    core_edges: list[list[int]],
    annulus_edges: list[list[int]],
) -> dict:
    outer_nodes = set(candidate["outer_nodes"])
    selected = [ce(*edge) for edge in core_edges]
    selected += [ce(*edge) for edge in annulus_edges]
    selected += [ce(*edge) for edge in candidate["inner_cut_edges"]]
    witness = nx.Graph()
    witness.add_nodes_from(outer_nodes)
    witness.add_edges_from(selected)
    outer_terminals = tuple(candidate["outer_terminals"])

    if output_state.startswith("P"):
        i, j = STATES[output_state][0]
        endpoints = {outer_terminals[i], outer_terminals[j]}
        expected_components = 1
        expected_edges = len(outer_nodes) - 1
        pairing_matches = True
    else:
        endpoints = set(outer_terminals)
        expected_components = 2
        expected_edges = len(outer_nodes) - 2
        actual_pairs: list[tuple[int, int]] = []
        for component in nx.connected_components(witness):
            ids = sorted(i for i, terminal in enumerate(outer_terminals) if terminal in component)
            if len(ids) == 2:
                actual_pairs.append(tuple(ids))
        actual = (
            tuple(sorted(tuple(sorted(pair)) for pair in actual_pairs))
            if len(actual_pairs) == 2
            else None
        )
        expected = tuple(sorted(tuple(sorted(pair)) for pair in STATES[output_state]))
        pairing_matches = actual == expected

    checks = {
        "all_edges_in_parent": all(parent.has_edge(*edge) for edge in selected),
        "no_duplicate_edges": len(selected) == len(set(selected)),
        "selected_edge_count": len(selected),
        "expected_edge_count": expected_edges,
        "components": nx.number_connected_components(witness),
        "expected_components": expected_components,
        "degree_constraints": all(
            witness.degree(v) == (1 if v in endpoints else 2) for v in outer_nodes
        ),
        "pairing_matches": pairing_matches,
    }
    checks["valid"] = all(
        (
            checks["all_edges_in_parent"],
            checks["no_duplicate_edges"],
            checks["selected_edge_count"] == expected_edges,
            checks["components"] == expected_components,
            checks["degree_constraints"],
            checks["pairing_matches"],
        )
    )
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q-results", type=Path, required=True)
    parser.add_argument("--verified", type=Path, required=True)
    parser.add_argument("--graphs", type=int, default=2)
    parser.add_argument("--annuli-per-graph", type=int, default=12)
    parser.add_argument("--time-limit", type=float, default=3.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.time()

    graph6_by_index, candidates = load_candidates(
        args.verified,
        args.graphs,
        args.annuli_per_graph,
    )
    payloads: list[tuple] = []
    metadata: list[tuple[str, str, str]] = []
    for candidate in candidates:
        for inner_state in candidate["inner_allowed_states"]:
            for outer_state in candidate["outer_allowed_states"]:
                payloads.append(
                    (
                        graph6_by_index[candidate["graph_index"]],
                        candidate["annulus_nodes"],
                        candidate["outer_terminals"],
                        candidate["inner_terminals"],
                        inner_state,
                        outer_state,
                        args.time_limit,
                    )
                )
                metadata.append((candidate["annulus_id"], inner_state, outer_state))

    relations = {
        candidate["annulus_id"]: {"candidate": candidate, "states": {}}
        for candidate in candidates
    }
    with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for (annulus_id, inner_state, outer_state), result in zip(
            metadata,
            executor.map(solve_relation, payloads, chunksize=1),
        ):
            relations[annulus_id]["states"][f"{inner_state}->{outer_state}"] = result

    q_data = json.loads(args.q_results.read_text(encoding="utf-8"))
    q_lookup = q_data.get("patch_results", {})
    positive_cardinalities: list[int] = []
    classifications: Counter[str] = Counter()
    provisional_cases: list[dict] = []
    composition_checks: Counter[str] = Counter()

    for annulus_id, record in relations.items():
        positives: list[str] = []
        composed: list[dict] = []
        candidate = record["candidate"]
        parent = nx.from_graph6_bytes(
            graph6_by_index[candidate["graph_index"]].encode("ascii")
        )
        for raw_key, result in record["states"].items():
            classifications[result["classification"]] += 1
            input_state, closure_state = raw_key.split("->")
            output_state = closure_to_actual(closure_state)
            actual_key = f"{input_state}->{output_state}"
            if result["classification"] == "verified_positive":
                positives.append(actual_key)
                if input_state.startswith("Q") and candidate["inner_key"] in q_lookup:
                    core_edges = (
                        q_lookup[candidate["inner_key"]]
                        ["states"]
                        .get(input_state, {})
                        .get("solver", {})
                        .get("selected_edges")
                    )
                    if core_edges is not None:
                        validation = validate_composed_q_witness(
                            parent,
                            candidate,
                            output_state,
                            core_edges,
                            result["selected_real_edges"],
                        )
                        composition_checks[
                            "valid" if validation["valid"] else "invalid"
                        ] += 1
                        composed.append(
                            {"transition": actual_key, "validation": validation}
                        )
            elif result["classification"] != "structural_infeasible":
                provisional_cases.append(
                    {
                        "annulus_id": annulus_id,
                        "state_pair": actual_key,
                        **result,
                    }
                )

        positives = sorted(set(positives))
        record["positive_entries"] = positives
        record["positive_cardinality"] = len(positives)
        record["composed_q_validations"] = composed
        record["pattern_sha256"] = hashlib.sha256(
            "\n".join(positives).encode("utf-8")
        ).hexdigest()
        positive_cardinalities.append(len(positives))

    summary = {
        "graphs": len(graph6_by_index),
        "annuli": len(candidates),
        "state_pairs_attempted": len(payloads),
        "classification_counts": dict(classifications),
        "positive_cardinality_histogram": dict(Counter(positive_cardinalities)),
        "minimum_positive_cardinality": (
            min(positive_cardinalities) if positive_cardinalities else None
        ),
        "maximum_positive_cardinality": (
            max(positive_cardinalities) if positive_cardinalities else None
        ),
        "distinct_positive_patterns": len(
            {record["pattern_sha256"] for record in relations.values()}
        ),
        "composed_q_witness_validations": dict(composition_checks),
        "provisional_or_unknown_cases": len(provisional_cases),
        "elapsed_s": time.time() - started,
        "counterexample_found": False,
    }
    output = {
        "parameters": {
            "q_results": str(args.q_results),
            "verified": str(args.verified),
            "graphs": args.graphs,
            "annuli_per_graph": args.annuli_per_graph,
            "time_limit": args.time_limit,
            "workers": args.workers,
            "output": str(args.output),
        },
        "state_order": STATE_ORDER,
        "summary": summary,
        "provisional_cases": provisional_cases,
        "relations": relations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
