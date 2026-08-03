#!/usr/bin/env python3
"""Exhaustively scan retained Barnette parents for consecutive facial failures."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path
from typing import Any

import networkx as nx

from generate_consecutive_face_cases import (
    build_cases,
    enumerate_canonical_faces,
    graph_validation,
)
from sat_verify_face_constraints import solve_case


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "case_id",
        "classification",
        "sat",
        "include_edges",
        "exclude_edges",
        "rounds",
        "added_subtour_constraints",
        "elapsed_s",
        "witness_path",
        "witness_sha256",
        "cnf_path",
        "cnf_sha256",
        "proof_path",
        "proof_sha256",
        "proof_verification",
        "reason",
        "reasons",
    }
    return {key: value for key, value in result.items() if key in keep}


def load_parent_records(paths: list[Path], order_filter: int | None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for path in paths:
        raw = path.read_bytes()
        data = json.loads(raw)
        metadata = data.get("metadata", {})
        inferred_order = int(metadata["order"]) if "order" in metadata else None
        for record in data.get("results", []):
            graph6 = str(record["graph6"])
            order = int(record.get("n", inferred_order))
            if order_filter is not None and order != order_filter:
                continue
            digest = hashlib.sha256(graph6.encode("ascii")).hexdigest()
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            records.append(
                {
                    "parent_id": f"order{order}-pool{int(record.get('pool_index', len(records))):02d}",
                    "order": order,
                    "pool_index": int(record.get("pool_index", len(records))),
                    "graph6": graph6,
                    "graph6_sha256": digest,
                    "source_path": str(path),
                    "source_sha256": hashlib.sha256(raw).hexdigest(),
                    "structural_score": record.get("structural_score"),
                    "face_metrics": record.get("face_metrics"),
                    "fragmentation": record.get("fragmentation"),
                }
            )
    records.sort(key=lambda item: (item["order"], item["pool_index"], item["graph6_sha256"]))
    return records


def process_parent(
    parent: dict[str, Any],
    output_dir: Path,
    solver_name: str,
    proof_solver: str | None,
    drat_trim: str | None,
    max_rounds: int,
    proof_timeout: float,
    max_cases_per_parent: int,
) -> dict[str, Any]:
    started = time.time()
    parent_dir = output_dir / parent["parent_id"]
    parent_dir.mkdir(parents=True, exist_ok=True)

    graph = nx.from_graph6_bytes(parent["graph6"].encode("ascii"))
    checks = graph_validation(graph)
    if not checks["barnette_predicates"]:
        summary = {
            "parent_id": parent["parent_id"],
            "classification": "malformed_parent",
            "graph_validation": checks,
            "counterexample_found": False,
        }
        (parent_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    faces = enumerate_canonical_faces(graph)
    expected_faces = graph.number_of_edges() - graph.number_of_nodes() + 2
    face_occurrences = sum(len(face) for face in faces)
    if len(faces) != expected_faces or face_occurrences != 2 * graph.number_of_edges():
        summary = {
            "parent_id": parent["parent_id"],
            "classification": "malformed_embedding",
            "graph_validation": checks,
            "faces": len(faces),
            "expected_faces": expected_faces,
            "face_edge_occurrences": face_occurrences,
            "expected_face_edge_occurrences": 2 * graph.number_of_edges(),
            "counterexample_found": False,
        }
        (parent_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    cases = build_cases(graph, faces, parent["parent_id"])
    if len(cases) > max_cases_per_parent:
        cases = cases[:max_cases_per_parent]
    case_document = {
        "date_utc": "2026-08-03",
        "status": "generated_exact_case_set",
        "objective": (
            "Test every consecutive facial path for a Hamiltonian cycle containing "
            "the middle edge and avoiding the outer edges."
        ),
        "source": {
            "parent_id": parent["parent_id"],
            "order": parent["order"],
            "pool_index": parent["pool_index"],
            "graph6": parent["graph6"],
            "graph6_sha256": parent["graph6_sha256"],
            "source_path": parent["source_path"],
            "source_sha256": parent["source_sha256"],
        },
        "graph_validation": checks,
        "face_summary": {
            "faces": len(faces),
            "expected_faces_by_euler": expected_faces,
            "face_lengths": [len(face) for face in faces],
            "face_edge_occurrences": face_occurrences,
        },
        "faces": [
            {"face_index": index, "length": len(face), "vertices_canonical": list(face)}
            for index, face in enumerate(faces)
        ],
        "case_summary": {
            "facial_path_occurrences": len(cases),
            "expected_full_count": face_occurrences,
            "all_cases_exhaustive": len(cases) == face_occurrences,
        },
        "cases": cases,
    }
    (parent_dir / "cases.json").write_text(json.dumps(case_document, indent=2), encoding="utf-8")

    proof_dir = parent_dir / "proof"
    results: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    negative_ids: list[str] = []
    incomplete_ids: list[str] = []
    for index, case in enumerate(cases, 1):
        print(
            json.dumps(
                {
                    "parent": parent["parent_id"],
                    "case": index,
                    "total": len(cases),
                    "id": case["case_id"],
                }
            ),
            flush=True,
        )
        result = solve_case(
            graph,
            case,
            proof_dir,
            solver_name,
            proof_solver,
            drat_trim,
            max_rounds,
            proof_timeout,
        )
        results.append(compact_result(result))
        classification = result["classification"]
        counts[classification] = counts.get(classification, 0) + 1
        if classification == "certified_negative":
            negative_ids.append(case["case_id"])
        elif classification != "verified_positive":
            incomplete_ids.append(case["case_id"])

    summary = {
        "parent_id": parent["parent_id"],
        "order": parent["order"],
        "pool_index": parent["pool_index"],
        "graph6": parent["graph6"],
        "graph6_sha256": parent["graph6_sha256"],
        "graph_validation": checks,
        "face_summary": case_document["face_summary"],
        "cases_attempted": len(cases),
        "classification_counts": counts,
        "certified_negative_case_ids": negative_ids,
        "incomplete_case_ids": incomplete_ids,
        "theorem_complete_breakthrough": bool(negative_ids),
        "complete_classification": not incomplete_ids and len(cases) == face_occurrences,
        "counterexample_found": False,
        "elapsed_s": time.time() - started,
        "results": results,
    }
    (parent_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parents", type=Path, nargs="+", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--order", type=int, default=None)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-rounds", type=int, default=20000)
    parser.add_argument("--proof-timeout", type=float, default=1800.0)
    parser.add_argument("--max-parents", type=int, default=100)
    parser.add_argument("--max-cases-per-parent", type=int, default=1000)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    parents = load_parent_records(args.parents, args.order)[: args.max_parents]
    if not parents:
        raise SystemExit("no parent records loaded")

    started = time.time()
    parent_summaries: list[dict[str, Any]] = []
    for index, parent in enumerate(parents, 1):
        print(
            json.dumps(
                {
                    "parent_index": index,
                    "parents_total": len(parents),
                    "parent_id": parent["parent_id"],
                }
            ),
            flush=True,
        )
        parent_summaries.append(
            process_parent(
                parent,
                args.output_dir,
                args.solver,
                args.proof_solver,
                args.drat_trim,
                args.max_rounds,
                args.proof_timeout,
                args.max_cases_per_parent,
            )
        )

    aggregate_counts: dict[str, int] = {}
    breakthroughs: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []
    total_cases = 0
    for summary in parent_summaries:
        total_cases += int(summary.get("cases_attempted", 0))
        for key, value in summary.get("classification_counts", {}).items():
            aggregate_counts[key] = aggregate_counts.get(key, 0) + int(value)
        if summary.get("certified_negative_case_ids"):
            breakthroughs.append(
                {
                    "parent_id": summary["parent_id"],
                    "order": summary["order"],
                    "pool_index": summary["pool_index"],
                    "graph6": summary["graph6"],
                    "graph6_sha256": summary["graph6_sha256"],
                    "case_ids": summary["certified_negative_case_ids"],
                }
            )
        if not summary.get("complete_classification", False):
            incomplete.append(
                {
                    "parent_id": summary["parent_id"],
                    "incomplete_case_ids": summary.get("incomplete_case_ids", []),
                    "classification": summary.get("classification"),
                }
            )

    campaign_summary = {
        "date_utc": "2026-08-03",
        "campaign": "grand-v3-retained-parent-consecutive-facial-scan",
        "order_filter": args.order,
        "parents_attempted": len(parent_summaries),
        "cases_attempted": total_cases,
        "classification_counts": aggregate_counts,
        "breakthroughs": breakthroughs,
        "incomplete_parents": incomplete,
        "theorem_complete_breakthrough": bool(breakthroughs),
        "complete_classification": not incomplete,
        "counterexample_found": False,
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
    }
    (args.output_dir / "campaign_summary.json").write_text(
        json.dumps(campaign_summary, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(campaign_summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
