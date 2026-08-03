#!/usr/bin/env python3
"""Generate every consecutive three-edge facial Hamiltonian constraint.

Given a committed Barnette graph record containing ``source.graph6``, enumerate
one planar embedding, canonicalize its face cycles, and emit every facial path

    v0-v1-v2-v3

as the Hamiltonian constraint

    exclude (v0,v1), include (v1,v2), exclude (v2,v3).

For a 3-connected planar graph the embedding is unique up to reflection, so the
canonical face set is independent of the embedding orientation returned by
NetworkX.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

Edge = tuple[int, int]


def ce(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def canonical_cycle(vertices: Iterable[int]) -> tuple[int, ...]:
    cycle = tuple(int(v) for v in vertices)
    if len(cycle) < 3:
        raise ValueError(f"invalid face cycle of length {len(cycle)}")
    candidates: list[tuple[int, ...]] = []
    for orientation in (cycle, tuple(reversed(cycle))):
        for shift in range(len(cycle)):
            candidates.append(orientation[shift:] + orientation[:shift])
    return min(candidates)


def enumerate_canonical_faces(graph: nx.Graph) -> list[tuple[int, ...]]:
    planar, embedding = nx.check_planarity(graph, counterexample=False)
    if not planar:
        raise ValueError("source graph is nonplanar")
    seen_darts: set[tuple[int, int]] = set()
    faces: list[tuple[int, ...]] = []
    for u, v in embedding.edges():
        if (u, v) in seen_darts:
            continue
        face = embedding.traverse_face(u, v, seen_darts)
        faces.append(canonical_cycle(face))
    faces.sort()
    if len(set(faces)) != len(faces):
        raise ValueError("canonical face enumeration produced duplicate face cycles")
    return faces


def graph_validation(graph: nx.Graph) -> dict[str, Any]:
    planar, _ = nx.check_planarity(graph, counterexample=False)
    connected = nx.is_connected(graph)
    result: dict[str, Any] = {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "simple": not graph.is_multigraph() and nx.number_of_selfloops(graph) == 0,
        "connected": connected,
        "cubic": all(graph.degree(vertex) == 3 for vertex in graph),
        "bipartite": nx.is_bipartite(graph),
        "planar": planar,
        "node_connectivity": nx.node_connectivity(graph) if connected else 0,
    }
    result["three_connected"] = result["node_connectivity"] >= 3
    result["barnette_predicates"] = all(
        result[key]
        for key in ("simple", "connected", "cubic", "bipartite", "planar", "three_connected")
    )
    return result


def build_cases(
    graph: nx.Graph,
    faces: list[tuple[int, ...]],
    source_label: str,
) -> list[dict[str, Any]]:
    graph_edges = {ce(*edge) for edge in graph.edges()}
    cases: list[dict[str, Any]] = []
    for face_index, face in enumerate(faces):
        length = len(face)
        if length % 2:
            raise ValueError(f"bipartite source has odd face {face_index}: {face}")
        for position in range(length):
            path = [face[(position + offset) % length] for offset in range(4)]
            outer_left = ce(path[0], path[1])
            middle = ce(path[1], path[2])
            outer_right = ce(path[2], path[3])
            required = {outer_left, middle, outer_right}
            if len(required) != 3 or not required <= graph_edges:
                raise ValueError(
                    f"malformed consecutive path on face {face_index}, "
                    f"position {position}: {path}"
                )
            cases.append(
                {
                    "case_id": (
                        f"{source_label}-f{face_index:02d}-p{position:02d}"
                        f"-mid{middle[0]}_{middle[1]}"
                        f"-out{outer_left[0]}_{outer_left[1]}"
                        f"-{outer_right[0]}_{outer_right[1]}"
                    ),
                    "constraint_type": "consecutive_facial_three_edge_path",
                    "face_index": face_index,
                    "face_length": length,
                    "face_vertices_canonical": list(face),
                    "path_position": position,
                    "path_vertices": path,
                    "include_edges": [list(middle)],
                    "exclude_edges": [list(outer_left), list(outer_right)],
                    "middle_edge": list(middle),
                    "outer_edges": [list(outer_left), list(outer_right)],
                }
            )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-label", default="candidate489")
    args = parser.parse_args()

    raw = args.source_input.read_bytes()
    data = json.loads(raw)
    source = data.get("source")
    if not isinstance(source, dict) or "graph6" not in source:
        raise SystemExit("input must contain source.graph6")

    graph = nx.from_graph6_bytes(str(source["graph6"]).encode("ascii"))
    checks = graph_validation(graph)
    if not checks["barnette_predicates"]:
        raise SystemExit(f"source failed Barnette predicates: {checks}")

    faces = enumerate_canonical_faces(graph)
    expected_faces = graph.number_of_edges() - graph.number_of_nodes() + 2
    face_edge_occurrences = sum(len(face) for face in faces)
    if len(faces) != expected_faces:
        raise SystemExit(f"Euler face count mismatch: {len(faces)} != {expected_faces}")
    if face_edge_occurrences != 2 * graph.number_of_edges():
        raise SystemExit(
            f"face-edge incidence mismatch: {face_edge_occurrences} "
            f"!= {2 * graph.number_of_edges()}"
        )

    cases = build_cases(graph, faces, args.source_label)
    if len(cases) != face_edge_occurrences:
        raise SystemExit(f"case count mismatch: {len(cases)} != {face_edge_occurrences}")

    unique_constraints = {
        (
            tuple(case["include_edges"][0]),
            tuple(sorted(tuple(edge) for edge in case["exclude_edges"])),
        )
        for case in cases
    }
    output = {
        "date_utc": "2026-08-03",
        "status": "generated_exact_case_set",
        "objective": (
            "Exhaustively test every consecutive facial three-edge path for a "
            "Hamiltonian cycle containing the middle edge and avoiding the two outer edges."
        ),
        "source": source,
        "source_input": str(args.source_input),
        "source_input_sha256": hashlib.sha256(raw).hexdigest(),
        "graph_validation": checks,
        "embedding_policy": (
            "NetworkX planar embedding; faces canonicalized over all rotations and both "
            "orientations. The source is 3-connected, so the facial structure is unique "
            "up to reflection."
        ),
        "face_summary": {
            "faces": len(faces),
            "expected_faces_by_euler": expected_faces,
            "face_lengths": [len(face) for face in faces],
            "face_edge_occurrences": face_edge_occurrences,
            "expected_face_edge_occurrences": 2 * graph.number_of_edges(),
        },
        "faces": [
            {
                "face_index": index,
                "length": len(face),
                "vertices_canonical": list(face),
            }
            for index, face in enumerate(faces)
        ],
        "case_summary": {
            "facial_path_occurrences": len(cases),
            "unique_edge_constraint_triples": len(unique_constraints),
            "all_cases_exhaustive": True,
        },
        "cases": cases,
        "counterexample_found": False,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "graph_validation": checks,
                "face_summary": output["face_summary"],
                "case_summary": output["case_summary"],
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
