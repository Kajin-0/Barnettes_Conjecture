#!/usr/bin/env python3
"""Rank canonical plantri Barnette graphs for exact patch analysis.

The input is one or more graph6 files generated with plantri -bc4dg.
Candidates are validated, filtered against two known easy structural regimes,
and ranked by fragmentation of complementary 2-factors sampled through random
perfect matchings.  This is a ranking heuristic only; no negative conclusion is
made from sampling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import networkx as nx
import numpy as np
from scipy.optimize import linear_sum_assignment


def faces_and_adjacency(G: nx.Graph):
    ok, emb = nx.check_planarity(G, counterexample=False)
    if not ok:
        raise ValueError("nonplanar")
    seen = set()
    faces = []
    dart_face = {}
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        face = emb.traverse_face(u, v, seen)
        fi = len(faces)
        faces.append(face)
        for i, a in enumerate(face):
            b = face[(i + 1) % len(face)]
            dart_face[(a, b)] = fi
    adj = [set() for _ in faces]
    for u, v in G.edges():
        a = dart_face[(u, v)]
        b = dart_face[(v, u)]
        if a != b:
            adj[a].add(b)
            adj[b].add(a)
    return faces, adj


def face_metrics(G: nx.Graph) -> dict:
    faces, adj = faces_and_adjacency(G)
    sizes = [len(f) for f in faces]
    big = {i for i, s in enumerate(sizes) if s >= 6}
    big_neighbours = [sum(j in big for j in adj[i]) for i in range(len(faces))]
    return {
        "num_faces": len(faces),
        "face_sizes": sorted(sizes),
        "max_face": max(sizes),
        "count4": sum(s == 4 for s in sizes),
        "count6": sum(s == 6 for s in sizes),
        "count8": sum(s == 8 for s in sizes),
        "count10plus": sum(s >= 10 for s in sizes),
        "max_big_neighbors": max(big_neighbours),
        "sum_big_neighbor_excess": sum(max(x - 4, 0) for x in big_neighbours),
    }


def fragmentation(G: nx.Graph, trials: int, seed: int) -> dict:
    color = nx.bipartite.color(G)
    A = sorted(v for v, c in color.items() if c == 0)
    B = sorted(v for v, c in color.items() if c == 1)
    if len(A) != len(B):
        raise ValueError("unbalanced bipartition")
    bidx = {v: i for i, v in enumerate(B)}
    n = len(A)
    allowed = np.zeros((n, n), dtype=bool)
    for i, u in enumerate(A):
        for v in G.neighbors(u):
            allowed[i, bidx[v]] = True
    rng = np.random.default_rng(seed)
    components = []
    hits = 0
    for _ in range(trials):
        cost = np.full((n, n), 1.0e12)
        cost[allowed] = rng.exponential(size=int(allowed.sum()))
        rows, cols = linear_sum_assignment(cost)
        matching = {tuple(sorted((A[i], B[j]))) for i, j in zip(rows, cols)}
        H = nx.Graph()
        H.add_nodes_from(G)
        H.add_edges_from(e for e in G.edges() if tuple(sorted(e)) not in matching)
        k = nx.number_connected_components(H)
        components.append(k)
        hits += int(k == 1)
    a = np.asarray(components, dtype=float)
    return {
        "trials": trials,
        "hamiltonian_hits": hits,
        "minimum_components": int(a.min()),
        "q05_components": float(np.quantile(a, 0.05)),
        "median_components": float(np.median(a)),
        "mean_components": float(a.mean()),
        "maximum_components": int(a.max()),
    }


def iter_graph6(paths: Iterable[Path]):
    seen = set()
    for path in paths:
        for raw in path.read_bytes().splitlines():
            raw = raw.strip()
            if not raw or raw.startswith(b">>"):
                continue
            try:
                G = nx.from_graph6_bytes(raw)
            except Exception:
                continue
            enc = nx.to_graph6_bytes(G, header=False).decode().strip()
            if enc not in seen:
                seen.add(enc)
                yield enc, G


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--order", type=int, default=92)
    ap.add_argument("--trials", type=int, default=128)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260801)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    records = []
    rejected = {"decode_or_order": 0, "class": 0, "easy_faces": 0, "easy_adjacency": 0}
    for serial, (enc, G) in enumerate(iter_graph6(args.inputs)):
        if G.number_of_nodes() != args.order:
            rejected["decode_or_order"] += 1
            continue
        planar, _ = nx.check_planarity(G, counterexample=False)
        if not (planar and nx.is_bipartite(G) and nx.is_connected(G) and all(d == 3 for _, d in G.degree())):
            rejected["class"] += 1
            continue
        fm = face_metrics(G)
        if fm["max_face"] <= 8:
            rejected["easy_faces"] += 1
            continue
        if fm["max_big_neighbors"] <= 4:
            rejected["easy_adjacency"] += 1
            continue
        frag = fragmentation(G, args.trials, args.seed + serial)
        score = (
            1000.0 * frag["minimum_components"]
            + 40.0 * frag["q05_components"]
            + 10.0 * frag["median_components"]
            + 4.0 * fm["sum_big_neighbor_excess"]
            + fm["max_face"]
            - 500.0 * frag["hamiltonian_hits"]
        )
        records.append({
            "graph6": enc,
            "sha256": hashlib.sha256(enc.encode()).hexdigest(),
            "n": G.number_of_nodes(),
            "m": G.number_of_edges(),
            "face_metrics": fm,
            "fragmentation": frag,
            "ranking_score": score,
        })

    records.sort(key=lambda r: (-r["ranking_score"], r["sha256"]))
    retained = records[: args.top]
    verified = {
        "metadata": {
            "generator": "plantri -bc4dg",
            "order": args.order,
            "ranking_is_heuristic": True,
            "input_unique_graphs": len(records) + sum(rejected.values()),
            "eligible_graphs": len(records),
            "rejected": rejected,
        },
        "results": [
            {
                "pool_index": i,
                "n": r["n"],
                "graph6": r["graph6"],
                "mode": "plantri-canonical-cyclic4",
                "structural_score": r["ranking_score"],
                "face_metrics": r["face_metrics"],
                "fragmentation": r["fragmentation"],
            }
            for i, r in enumerate(retained)
        ],
        "all_ranked": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verified, indent=2), encoding="utf-8")
    print(json.dumps({
        "input_unique": verified["metadata"]["input_unique_graphs"],
        "eligible": len(records),
        "retained": len(retained),
        "rejected": rejected,
        "top": [{"sha256": r["sha256"][:16], "score": r["ranking_score"], **r["fragmentation"], "max_face": r["face_metrics"]["max_face"], "max_big_neighbors": r["face_metrics"]["max_big_neighbors"]} for r in retained],
    }, indent=2))


if __name__ == "__main__":
    main()
