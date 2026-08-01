#!/usr/bin/env python3
"""Exact four-terminal patch signatures using SAT and subtour cuts.

Each Hamilton-path or two-path-cover boundary state is reduced to a Hamiltonian
cycle in an augmented multigraph with one or two forced artificial edges.
Degree-two constraints are encoded in CNF. Disconnected cycle covers are cut
iteratively until a spanning cycle is found or the final CNF is UNSAT.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import networkx as nx
from pysat.solvers import Cadical195, Glucose4, Minisat22

sys.path.insert(0, str(Path(__file__).resolve().parent))
import patch_gluing_search as pl


@dataclass
class SatStateResult:
    status: str
    feasible: bool | None
    elapsed_s: float
    solver: str
    iterations: int
    cuts: int
    clauses: int
    selected_real_edges: list[list[int]] | None = None


def edge_face_scores(G: nx.Graph) -> dict[tuple[int, int], float]:
    ok, emb = nx.check_planarity(G)
    if not ok:
        raise ValueError("nonplanar input")
    seen = set()
    dart_face = {}
    faces = []
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        face = emb.traverse_face(u, v, seen)
        fi = len(faces)
        faces.append(face)
        for j, a in enumerate(face):
            dart_face[(a, face[(j + 1) % len(face)])] = fi
    score = {}
    for u, v in G.edges():
        a = len(faces[dart_face[(u, v)]])
        b = len(faces[dart_face[(v, u)]])
        score[pl.ce(u, v)] = 8.0 * min(a, b) + 3.0 * max(a, b) + a * b / 4.0
    return score


def new_solver():
    for cls, name in (
        (Cadical195, "cadical195"),
        (Glucose4, "glucose4"),
        (Minisat22, "minisat22"),
    ):
        try:
            return cls(), name
        except Exception:
            continue
    raise RuntimeError("no PySAT backend is available")


def exactly_two(variables: list[int]) -> list[list[int]]:
    if len(variables) == 2:
        return [[variables[0]], [variables[1]]]
    if len(variables) != 3:
        raise ValueError(f"unexpected augmented degree {len(variables)}")
    a, b, c = variables
    return [[a, b], [a, c], [b, c], [-a, -b, -c]]


def augmented_cycle(P: nx.Graph, artificial_edges, time_limit: float) -> SatStateResult:
    # The third field distinguishes artificial parallel edges from real edges.
    records = [(int(u), int(v), False) for u, v in sorted(pl.ce(*e) for e in P.edges())]
    records.extend((int(u), int(v), True) for u, v in artificial_edges)
    incidence = {v: [] for v in P}
    for variable, (u, v, _) in enumerate(records, 1):
        incidence[u].append(variable)
        incidence[v].append(variable)

    clauses = []
    for v in sorted(P):
        clauses.extend(exactly_two(incidence[v]))
    for variable, (_, _, artificial) in enumerate(records, 1):
        if artificial:
            clauses.append([variable])

    solver, solver_name = new_solver()
    for clause in clauses:
        solver.add_clause(clause)
    started = time.time()
    iterations = 0
    cuts = 0
    try:
        while True:
            remaining = time_limit - (time.time() - started)
            if remaining <= 0:
                return SatStateResult(
                    "timeout", None, time.time() - started, solver_name,
                    iterations, cuts, len(clauses)
                )
            timer = threading.Timer(remaining, solver.interrupt)
            timer.daemon = True
            timer.start()
            satisfiable = solver.solve_limited(expect_interrupt=True)
            timer.cancel()
            solver.clear_interrupt()
            iterations += 1
            if satisfiable is None:
                return SatStateResult(
                    "timeout", None, time.time() - started, solver_name,
                    iterations, cuts, len(clauses)
                )
            if not satisfiable:
                return SatStateResult(
                    "infeasible", False, time.time() - started, solver_name,
                    iterations, cuts, len(clauses)
                )

            positive = {x for x in solver.get_model() if x > 0}
            selected = [
                records[i - 1] for i in positive if 1 <= i <= len(records)
            ]
            H = nx.MultiGraph()
            H.add_nodes_from(P)
            H.add_edges_from((u, v) for u, v, _ in selected)
            components = list(nx.connected_components(nx.Graph(H)))
            if len(components) == 1 and all(H.degree(v) == 2 for v in P):
                real = [list(pl.ce(u, v)) for u, v, artificial in selected if not artificial]
                return SatStateResult(
                    "feasible", True, time.time() - started, solver_name,
                    iterations, cuts, len(clauses), sorted(real)
                )

            all_nodes = set(P)
            for component in components:
                if component == all_nodes:
                    continue
                cut = [
                    variable
                    for variable, (u, v, _) in enumerate(records, 1)
                    if (u in component) != (v in component)
                ]
                if not cut:
                    raise AssertionError("zero cut in a connected patch")
                solver.add_clause(cut)
                clauses.append(cut)
                cuts += 1
    finally:
        solver.delete()


def validate_path(P, spec, state, selected) -> bool:
    endpoints = {spec.terminals[i] for i in state}
    H = nx.Graph()
    H.add_nodes_from(P)
    H.add_edges_from(tuple(e) for e in selected)
    return nx.is_connected(H) and all(
        H.degree(v) == (1 if v in endpoints else 2) for v in P
    )


def validate_pair(P, spec, pairing, selected) -> bool:
    H = nx.Graph()
    H.add_nodes_from(P)
    H.add_edges_from(tuple(e) for e in selected)
    components = list(nx.connected_components(H))
    actual = []
    for component in components:
        ids = sorted(i for i, terminal in enumerate(spec.terminals) if terminal in component)
        if len(ids) == 2:
            actual.append(tuple(ids))
    return len(components) == 2 and pl.canonical_pairing(actual) == pl.canonical_pairing(pairing)


def exact_sat_signature(P, spec, time_limit: float) -> dict:
    states = {}
    feasible = []
    unknown = []
    for state in pl.ALL_PATH_STATES:
        u, v = (spec.terminals[i] for i in state)
        result = augmented_cycle(P, [(u, v)], time_limit)
        if result.feasible and not validate_path(P, spec, state, result.selected_real_edges):
            result.status = "invalid_witness"
            result.feasible = None
        key = pl.path_key(state)
        states[key] = asdict(result)
        if result.feasible:
            feasible.append(key)
        if result.feasible is None:
            unknown.append(key)

    for pairing in pl.ALL_PAIR_STATES:
        (i0, i1), (j0, j1) = pairing
        artificial = [
            (spec.terminals[i0], spec.terminals[j0]),
            (spec.terminals[i1], spec.terminals[j1]),
        ]
        result = augmented_cycle(P, artificial, time_limit)
        if result.feasible and not validate_pair(P, spec, pairing, result.selected_real_edges):
            result.status = "invalid_witness"
            result.feasible = None
        key = pl.pair_key(pairing)
        states[key] = asdict(result)
        if result.feasible:
            feasible.append(key)
        if result.feasible is None:
            unknown.append(key)

    return {
        "patch": asdict(spec),
        "complete": not unknown,
        "feasible_states": sorted(feasible),
        "unknown_states": sorted(unknown),
        "states": states,
    }


def signature_worker(task):
    graph_index, graph6, edge, time_limit = task
    G = nx.from_graph6_bytes(graph6.encode())
    P, spec = pl.make_patch_spec(G, graph_index, edge)
    return spec.key, graph6, list(edge), exact_sat_signature(P, spec, time_limit)


def restore_spec(raw: dict) -> pl.PatchSpec:
    return pl.PatchSpec(
        graph_index=int(raw["graph_index"]),
        removed_edge=tuple(raw["removed_edge"]),
        terminals=tuple(raw["terminals"]),
        terminal_owner=tuple(raw["terminal_owner"]),
        terminal_colors=tuple(raw["terminal_colors"]),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", type=Path, required=True)
    ap.add_argument("--indices", required=True)
    ap.add_argument("--per-graph", type=int, default=4)
    ap.add_argument("--state-time", type=float, default=10.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--whole-time", type=float, default=120.0)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(args.verified.read_text(encoding="utf-8"))["results"]
    indices = [int(x) for x in args.indices.split(",") if x]
    tasks = []
    for index in indices:
        record = data[index]
        G = nx.from_graph6_bytes(record["graph6"].encode())
        scores = edge_face_scores(G)
        selected = sorted(scores, key=lambda e: (-scores[e], e))[: args.per_graph]
        tasks.extend((index, record["graph6"], edge, args.state_time) for edge in selected)

    started = time.time()
    signatures = {}
    patch_info = {}
    with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for key, graph6, edge, signature in executor.map(signature_worker, tasks):
            signatures[key] = signature
            patch_info[key] = {"graph6": graph6, "edge": edge}
            print(json.dumps({
                "phase": "signature",
                "patch": key,
                "complete": signature["complete"],
                "feasible": signature["feasible_states"],
                "unknown": signature["unknown_states"],
            }), flush=True)

    complete = sorted(k for k, signature in signatures.items() if signature["complete"])
    compatibility_counts = []
    incompatible = []
    for i, key1 in enumerate(complete):
        spec1 = restore_spec(signatures[key1]["patch"])
        for key2 in complete[i:]:
            spec2 = restore_spec(signatures[key2]["patch"])
            for mapping in pl.dihedral_maps():
                if not all(
                    spec1.terminal_colors[j] != spec2.terminal_colors[mapping[j]]
                    for j in range(4)
                ):
                    continue
                compatibility = pl.compatible_states(
                    signatures[key1]["feasible_states"],
                    signatures[key2]["feasible_states"],
                    mapping,
                )
                compatibility_counts.append(len(compatibility))
                if not compatibility:
                    incompatible.append((key1, key2, mapping))

    tested = []
    counterexample = None
    for rank, (key1, key2, mapping) in enumerate(incompatible, 1):
        info1, info2 = patch_info[key1], patch_info[key2]
        G1 = nx.from_graph6_bytes(info1["graph6"].encode())
        G2 = nx.from_graph6_bytes(info2["graph6"].encode())
        P1, spec1 = pl.make_patch_spec(
            G1, signatures[key1]["patch"]["graph_index"], tuple(info1["edge"])
        )
        P2, spec2 = pl.make_patch_spec(
            G2, signatures[key2]["patch"]["graph_index"], tuple(info2["edge"])
        )
        H = pl.glue_patches(P1, spec1, P2, spec2, mapping)
        validation = pl.validate_barnette(H)
        record = {
            "patch1": key1,
            "patch2": key2,
            "mapping": list(mapping),
            "validation": validation,
            "graph6": pl.g6(H),
        }
        if validation["barnette"]:
            ham = pl.hamiltonian_flow_milp(H, args.whole_time, 20260801 + rank)
            record["whole_graph_hamiltonicity"] = asdict(ham)
            if ham.hamiltonian is False:
                counterexample = record
                (args.output_dir / "counterexample.graph6").write_text(
                    record["graph6"] + "\n", encoding="ascii"
                )
                tested.append(record)
                break
        tested.append(record)

    result = {
        "metadata": {"elapsed_s": time.time() - started},
        "parameters": {
            "verified": str(args.verified),
            "indices": indices,
            "per_graph": args.per_graph,
            "state_time": args.state_time,
            "workers": args.workers,
            "whole_time": args.whole_time,
        },
        "summary": {
            "patches": len(tasks),
            "complete_signatures": len(complete),
            "unknown_signatures": len(tasks) - len(complete),
            "pair_maps_checked": len(compatibility_counts),
            "minimum_compatibility": min(compatibility_counts) if compatibility_counts else None,
            "incompatible_pair_maps": len(incompatible),
            "tested_incompatible": len(tested),
            "counterexample_found": counterexample is not None,
        },
        "signatures": signatures,
        "incompatible_candidates": [
            {"patch1": a, "patch2": b, "mapping": list(mapping)}
            for a, b, mapping in incompatible
        ],
        "tested": tested,
        "counterexample": counterexample,
    }
    (args.output_dir / "sat_patch_library_results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps({"phase": "complete", **result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
