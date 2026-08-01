#!/usr/bin/env python3
"""Exact-first search over heterogeneous four-terminal Barnette patches.

Unlike the pilot, this program computes exact boundary signatures before
forming patch pairs. It constructs and validates a glued graph only when two
complete signatures have no compatible Hamiltonian boundary state.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
import time
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import patch_gluing_search as pl


def edge_face_scores(G: nx.Graph) -> dict[tuple[int, int], float]:
    ok, emb = nx.check_planarity(G)
    if not ok:
        raise ValueError("nonplanar input")
    seen = set()
    dart_face: dict[tuple[int, int], int] = {}
    faces: list[list[int]] = []
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        face = emb.traverse_face(u, v, seen)
        fi = len(faces)
        faces.append(face)
        for j, a in enumerate(face):
            dart_face[(a, face[(j + 1) % len(face)])] = fi
    scores = {}
    for u, v in G.edges():
        a = len(faces[dart_face[(u, v)]])
        b = len(faces[dart_face[(v, u)]])
        scores[pl.ce(u, v)] = 8.0 * min(a, b) + 3.0 * max(a, b) + a * b / 4.0
    return scores


def signature_worker(task: tuple[int, str, tuple[int, int], float]):
    graph_index, graph6, edge, time_limit = task
    G = nx.from_graph6_bytes(graph6.encode())
    P, spec = pl.make_patch_spec(G, graph_index, edge)
    signature = pl.exact_signature(P, spec, time_limit)
    return spec.key, graph6, list(edge), signature


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
    ap.add_argument("--state-time", type=float, default=5.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--whole-time", type=float, default=120.0)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(args.verified.read_text(encoding="utf-8"))["results"]
    indices = [int(x) for x in args.indices.split(",") if x]
    tasks = []
    graph_metadata = {}
    for idx in indices:
        rec = data[idx]
        G = nx.from_graph6_bytes(rec["graph6"].encode())
        scores = edge_face_scores(G)
        chosen = sorted(scores, key=lambda e: (-scores[e], e))[: args.per_graph]
        graph_metadata[str(idx)] = {
            "n": G.number_of_nodes(),
            "chosen_edges": [list(e) for e in chosen],
            "edge_scores": [scores[e] for e in chosen],
        }
        tasks.extend((idx, rec["graph6"], edge, args.state_time) for edge in chosen)

    started = time.time()
    signatures = {}
    patch_info = {}
    with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(signature_worker, task): task for task in tasks}
        for future in cf.as_completed(futures):
            key, graph6, edge, signature = future.result()
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
    maps = pl.dihedral_maps()
    incompatible = []
    compatibility_counts = []
    for i, key1 in enumerate(complete):
        sig1 = signatures[key1]
        spec1 = restore_spec(sig1["patch"])
        for key2 in complete[i:]:
            sig2 = signatures[key2]
            spec2 = restore_spec(sig2["patch"])
            for mapping in maps:
                if not all(
                    spec1.terminal_colors[j] != spec2.terminal_colors[mapping[j]]
                    for j in range(4)
                ):
                    continue
                compatibility = pl.compatible_states(
                    sig1["feasible_states"], sig2["feasible_states"], mapping
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
            "rank": rank,
            "patch1": key1,
            "patch2": key2,
            "mapping": list(mapping),
            "validation": validation,
            "graph6": pl.g6(H),
        }
        if validation["barnette"]:
            ham = pl.hamiltonian_flow_milp(
                H, args.whole_time, 20260801 + rank
            )
            record["whole_graph_hamiltonicity"] = pl.asdict(ham)
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
            "output_dir": str(args.output_dir),
        },
        "graphs": graph_metadata,
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
    (args.output_dir / "exact_patch_library_results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps({"phase": "complete", **result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
