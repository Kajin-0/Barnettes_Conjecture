#!/usr/bin/env python3
"""Emit the eight minimal candidate-489 cofacial two-edge avoidance cases.

These pairs were discovered by complete finite enumeration of the 322 face-2
masks allowed by local degree constraints.  Each listed pair had at least 21
locally feasible face-mask completions, but none extended to a Hamiltonian
cycle in the independent complement-matching recursion.  This generator only
materializes the cases; final negative status requires CaDiCaL plus drat-trim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PAIRS = [(0, 9), (1, 8), (2, 7), (2, 9), (2, 11), (3, 6), (4, 7), (8, 11)]
LOCAL_EXTENSION_COUNTS = [21, 24, 24, 24, 21, 21, 21, 21]


def canonical_edge(edge: list[int]) -> list[int]:
    return sorted((int(edge[0]), int(edge[1])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_data = json.loads(args.source_input.read_text(encoding="utf-8"))
    face = source_data["face"]
    edges = [canonical_edge(edge) for edge in face["edges_cyclic_order"]]
    if len(edges) != 12:
        raise SystemExit(f"expected 12 face edges, found {len(edges)}")

    cases = []
    for (left, right), local_count in zip(PAIRS, LOCAL_EXTENSION_COUNTS, strict=True):
        cases.append(
            {
                "case_id": f"candidate489-f2-avoid-e{left}-e{right}",
                "constraint_type": "cofacial_two_edge_avoidance",
                "face_index": int(face["face_index"]),
                "face_vertices_cyclic_order": face["vertices_cyclic_order"],
                "face_edge_indices": [left, right],
                "include_edges": [],
                "exclude_edges": [edges[left], edges[right]],
                "local_face_masks_extending_constraint": local_count,
            }
        )

    output = {
        "date_utc": "2026-08-03",
        "status": "provisional_pending_independent_drat",
        "objective": (
            "Verify eight minimal cofacial edge pairs for which no Hamiltonian "
            "cycle avoids both designated edges."
        ),
        "source": source_data["source"],
        "face": face,
        "derivation": {
            "face_edge_masks_total": 4096,
            "locally_feasible_face_masks": 322,
            "exact_hamiltonian_positive_masks": 100,
            "exact_negative_masks": 222,
            "matching_search_unknown_masks": 0,
            "matching_search_max_recursive_calls_per_mask": 3124,
            "prime_forbidden_cubes_width_2": 8,
            "negative_policy": (
                "The finite complement-matching result remains provisional here. "
                "Final status requires CaDiCaL UNSAT and drat-trim acceptance."
            ),
        },
        "cases": cases,
        "counterexample_found": False,
        "next_step": (
            "Proof-certify every case, then synthesize a simple cubic bipartite "
            "planar 3-connected face patch that forces both edges absent."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"cases": len(cases), "pairs": PAIRS, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
