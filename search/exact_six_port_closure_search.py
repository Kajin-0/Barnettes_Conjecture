#!/usr/bin/env python3
"""Search canonical six-port patches for an exact zero-language closure.

The source pole is canonical order-100 candidate 489 with the principal
certified triple removed.  A patch has six degree-two ports and all remaining
vertices degree three.  Every exact Hamiltonian path-cover state of the source
and patch is enumerated.  Each color-compatible terminal bijection is tested.
A zero-compatible gluing that is simple, cubic, bipartite, planar, and
3-connected is sent immediately to proof-producing whole-graph SAT.

Input patch graphs are graph6 records, normally generated canonically by
plantri as bipartite 2-connected planar graphs with the required order and edge
count.  Graphs with any degree sequence other than six degree-two vertices and
all remaining vertices degree three are rejected.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

from sat_verify_face_constraints import graph_validation, solve_case

Edge = tuple[int, int]


def ce(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def all_pairings(items: Iterable[int]) -> Iterable[tuple[tuple[int, int], ...]]:
    values = tuple(items)
    if not values:
        yield ()
        return
    first = values[0]
    for position in range(1, len(values)):
        second = values[position]
        remainder = values[1:position] + values[position + 1 :]
        for tail in all_pairings(remainder):
            yield ((first, second),) + tail


def validate_path_cover(
    graph: nx.Graph,
    selected_edges: list[Edge],
    ports: list[int],
    active_indices: tuple[int, ...],
    pairing_indices: tuple[tuple[int, int], ...],
) -> None:
    active = {ports[index] for index in active_indices}
    expected_pairing = {
        frozenset((ports[left], ports[right]))
        for left, right in pairing_indices
    }
    selected = {ce(*edge) for edge in selected_edges}
    if len(selected) != len(selected_edges):
        raise ValueError("duplicate selected edge")
    if not selected <= {ce(*edge) for edge in graph.edges()}:
        raise ValueError("selected edge outside graph")
    cover = nx.Graph()
    cover.add_nodes_from(graph.nodes())
    cover.add_edges_from(selected)
    for vertex in graph:
        expected_degree = 1 if vertex in active else 2
        if cover.degree(vertex) != expected_degree:
            raise ValueError(
                f"degree mismatch at {vertex}: {cover.degree(vertex)} != {expected_degree}"
            )
    components = list(nx.connected_components(cover))
    observed_pairing = {
        frozenset(vertex for vertex in component if vertex in active)
        for component in components
    }
    if len(components) != len(expected_pairing) or observed_pairing != expected_pairing:
        raise ValueError(
            f"component pairing mismatch: {observed_pairing} != {expected_pairing}"
        )


def exact_path_cover_state(
    graph: nx.Graph,
    ports: list[int],
    active_indices: tuple[int, ...],
    pairing_indices: tuple[tuple[int, int], ...],
    call_budget: int,
) -> dict[str, Any]:
    active = {ports[index] for index in active_indices}
    wanted_pairs = {
        frozenset((ports[left], ports[right]))
        for left, right in pairing_indices
    }
    nodes = sorted(graph.nodes())
    edges = sorted({ce(*edge) for edge in graph.edges()})
    edge_index = {edge: index for index, edge in enumerate(edges)}
    incident = {
        vertex: [edge_index[ce(vertex, neighbor)] for neighbor in graph.neighbors(vertex)]
        for vertex in nodes
    }
    target_degree = {vertex: (1 if vertex in active else 2) for vertex in nodes}
    excluded_need = {
        vertex: graph.degree(vertex) - target_degree[vertex]
        for vertex in nodes
    }
    if any(value < 0 for value in excluded_need.values()):
        return {
            "active": list(active_indices),
            "pairing": [list(pair) for pair in pairing_indices],
            "classification": "exact_negative",
            "recursive_calls": 0,
            "reason": "target degree exceeds graph degree",
        }

    excluded: set[int] = set()
    selected: set[int] = set()
    excluded_degree = {vertex: 0 for vertex in nodes}
    selected_degree = {vertex: 0 for vertex in nodes}
    recursive_calls = 0
    closed_component_prunes = 0

    def assign(edge_id: int, excluded_value: bool, changed: list[tuple[int, bool]]) -> bool:
        target_set = excluded if excluded_value else selected
        opposite_set = selected if excluded_value else excluded
        if edge_id in target_set:
            return True
        if edge_id in opposite_set:
            return False
        target_set.add(edge_id)
        changed.append((edge_id, excluded_value))
        left, right = edges[edge_id]
        if excluded_value:
            excluded_degree[left] += 1
            excluded_degree[right] += 1
        else:
            selected_degree[left] += 1
            selected_degree[right] += 1
        return (
            excluded_degree[left] <= excluded_need[left]
            and excluded_degree[right] <= excluded_need[right]
            and selected_degree[left] <= target_degree[left]
            and selected_degree[right] <= target_degree[right]
        )

    def undo(changed: list[tuple[int, bool]]) -> None:
        for edge_id, excluded_value in reversed(changed):
            left, right = edges[edge_id]
            if excluded_value:
                excluded.remove(edge_id)
                excluded_degree[left] -= 1
                excluded_degree[right] -= 1
            else:
                selected.remove(edge_id)
                selected_degree[left] -= 1
                selected_degree[right] -= 1

    def propagate() -> tuple[bool, list[tuple[int, bool]]]:
        changed: list[tuple[int, bool]] = []
        while True:
            progressed = False
            for vertex in nodes:
                undecided = [
                    edge_id
                    for edge_id in incident[vertex]
                    if edge_id not in excluded and edge_id not in selected
                ]
                need_excluded = excluded_need[vertex] - excluded_degree[vertex]
                need_selected = target_degree[vertex] - selected_degree[vertex]
                if (
                    need_excluded < 0
                    or need_selected < 0
                    or need_excluded + need_selected != len(undecided)
                ):
                    return False, changed
                if undecided and (need_excluded == 0 or need_selected == 0):
                    excluded_value = need_selected == 0
                    for edge_id in undecided:
                        if not assign(edge_id, excluded_value, changed):
                            return False, changed
                    progressed = True
            if not progressed:
                return True, changed

    def has_invalid_closed_component() -> bool:
        nonlocal closed_component_prunes
        if not selected:
            return False
        adjacency = {vertex: [] for vertex in nodes}
        for edge_id in selected:
            left, right = edges[edge_id]
            adjacency[left].append(right)
            adjacency[right].append(left)
        seen: set[int] = set()
        for start in nodes:
            if start in seen or not adjacency[start]:
                continue
            component = {start}
            stack = [start]
            seen.add(start)
            while stack:
                vertex = stack.pop()
                for neighbor in adjacency[vertex]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        component.add(neighbor)
                        stack.append(neighbor)
            if all(selected_degree[vertex] == target_degree[vertex] for vertex in component):
                endpoints = frozenset(vertex for vertex in component if vertex in active)
                if len(endpoints) != 2 or endpoints not in wanted_pairs:
                    closed_component_prunes += 1
                    return True
        return False

    def recurse() -> list[Edge] | None:
        nonlocal recursive_calls
        recursive_calls += 1
        if recursive_calls > call_budget:
            raise RuntimeError("call budget exceeded")
        consistent, propagated = propagate()
        if not consistent:
            undo(propagated)
            return None
        if has_invalid_closed_component():
            undo(propagated)
            return None
        if len(excluded) + len(selected) == len(edges):
            witness = [edges[edge_id] for edge_id in sorted(selected)]
            try:
                validate_path_cover(
                    graph,
                    witness,
                    ports,
                    active_indices,
                    pairing_indices,
                )
            except ValueError:
                witness = None
            undo(propagated)
            return witness

        choice: tuple[int, int] | None = None
        for vertex in nodes:
            undecided = [
                edge_id
                for edge_id in incident[vertex]
                if edge_id not in excluded and edge_id not in selected
            ]
            if undecided and (choice is None or len(undecided) < choice[0]):
                choice = (len(undecided), undecided[0])
        if choice is None:
            undo(propagated)
            return None
        edge_id = choice[1]
        for excluded_value in (True, False):
            branch_changes: list[tuple[int, bool]] = []
            if assign(edge_id, excluded_value, branch_changes):
                witness = recurse()
                if witness is not None:
                    undo(branch_changes)
                    undo(propagated)
                    return witness
            undo(branch_changes)
        undo(propagated)
        return None

    started = time.time()
    try:
        witness = recurse()
    except RuntimeError:
        return {
            "active": list(active_indices),
            "pairing": [list(pair) for pair in pairing_indices],
            "classification": "unknown",
            "recursive_calls": recursive_calls,
            "closed_component_prunes": closed_component_prunes,
            "elapsed_s": time.time() - started,
            "reason": "call budget exceeded",
        }
    if witness is None:
        return {
            "active": list(active_indices),
            "pairing": [list(pair) for pair in pairing_indices],
            "classification": "exact_negative",
            "recursive_calls": recursive_calls,
            "closed_component_prunes": closed_component_prunes,
            "elapsed_s": time.time() - started,
        }
    return {
        "active": list(active_indices),
        "pairing": [list(pair) for pair in pairing_indices],
        "classification": "verified_positive",
        "recursive_calls": recursive_calls,
        "closed_component_prunes": closed_component_prunes,
        "elapsed_s": time.time() - started,
        "witness": [list(edge) for edge in witness],
    }


def exact_language(graph: nx.Graph, ports: list[int], call_budget: int) -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = []
    for active_size in (2, 4, 6):
        for active in itertools.combinations(range(6), active_size):
            for pairing in all_pairings(active):
                states.append(
                    exact_path_cover_state(
                        graph,
                        ports,
                        active,
                        pairing,
                        call_budget,
                    )
                )
    if len(states) != 75:
        raise ValueError(f"six-port state-space mismatch: {len(states)}")
    return states


def states_compatible(
    source_state: dict[str, Any],
    patch_state: dict[str, Any],
    source_to_patch: tuple[int, ...],
) -> bool:
    source_active = set(int(value) for value in source_state["active"])
    patch_active = set(int(value) for value in patch_state["active"])
    if {source_to_patch[index] for index in source_active} != patch_active:
        return False
    if len(source_active) == 2:
        return True
    inverse = {source_to_patch[index]: index for index in range(6)}
    adjacency = {index: set() for index in source_active}
    for left, right in source_state["pairing"]:
        adjacency[int(left)].add(int(right))
        adjacency[int(right)].add(int(left))
    for left, right in patch_state["pairing"]:
        source_left = inverse[int(left)]
        source_right = inverse[int(right)]
        adjacency[source_left].add(source_right)
        adjacency[source_right].add(source_left)
    start = next(iter(source_active))
    seen = {start}
    stack = [start]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return seen == source_active


def color_compatible_maps(source_colors: list[int], patch_colors: list[int]) -> list[tuple[int, ...]]:
    source_by_color = {
        color: [index for index, value in enumerate(source_colors) if value == color]
        for color in (0, 1)
    }
    patch_by_color = {
        color: [index for index, value in enumerate(patch_colors) if value == color]
        for color in (0, 1)
    }
    if len(source_by_color[0]) != len(patch_by_color[1]) or len(source_by_color[1]) != len(patch_by_color[0]):
        return []
    mappings: list[tuple[int, ...]] = []
    for targets_zero in itertools.permutations(patch_by_color[1]):
        for targets_one in itertools.permutations(patch_by_color[0]):
            mapping: list[int | None] = [None] * 6
            for source_index, patch_index in zip(source_by_color[0], targets_zero, strict=True):
                mapping[source_index] = patch_index
            for source_index, patch_index in zip(source_by_color[1], targets_one, strict=True):
                mapping[source_index] = patch_index
            mappings.append(tuple(int(value) for value in mapping))
    return mappings


def load_graph6_records(path: Path) -> list[str]:
    records: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="ascii").splitlines():
        record = line.strip()
        if not record or record.startswith(">>"):
            continue
        if record not in seen:
            seen.add(record)
            records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-input", type=Path, required=True)
    parser.add_argument("--patch-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-patch-order", type=int, required=True)
    parser.add_argument("--expected-patch-edges", type=int, required=True)
    parser.add_argument("--call-budget", type=int, default=10000000)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-rounds", type=int, default=100000)
    parser.add_argument("--proof-timeout", type=float, default=3600.0)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    source_raw = args.source_input.read_bytes()
    source_data = json.loads(source_raw)
    source_graph = nx.from_graph6_bytes(source_data["source"]["graph6"].encode("ascii"))
    source_checks = graph_validation(source_graph)
    if not source_checks["barnette_predicates"]:
        raise SystemExit(f"source failed Barnette predicates: {source_checks}")

    removed_edges = [ce(14, 18), ce(10, 17), ce(5, 11)]
    face_vertices = [int(value) for value in source_data["face"]["vertices_cyclic_order"]]
    terminal_set = {vertex for edge in removed_edges for vertex in edge}
    source_ports = [vertex for vertex in face_vertices if vertex in terminal_set]
    if len(source_ports) != 6:
        raise SystemExit(f"source terminal count mismatch: {source_ports}")
    source_core = source_graph.copy()
    source_core.remove_edges_from(removed_edges)
    source_language = exact_language(source_core, source_ports, args.call_budget)
    source_positive = [
        state for state in source_language if state["classification"] == "verified_positive"
    ]
    source_unknown = [state for state in source_language if state["classification"] == "unknown"]
    if source_unknown:
        raise SystemExit(f"source language contains unknown states: {len(source_unknown)}")
    if len(source_positive) != 26:
        raise SystemExit(f"source positive-state regression: {len(source_positive)} != 26")

    source_coloring = nx.bipartite.color(source_graph)
    source_port_colors = [int(source_coloring[vertex]) for vertex in source_ports]
    records = load_graph6_records(args.patch_input)
    started = time.time()
    patch_counts = Counter()
    compatibility_histogram = Counter()
    best_records: list[dict[str, Any]] = []
    zero_records: list[dict[str, Any]] = []
    valid_zero_candidates: list[dict[str, Any]] = []
    incomplete_records: list[dict[str, Any]] = []

    for record_index, graph6 in enumerate(records):
        patch_counts["input_records"] += 1
        try:
            patch = nx.from_graph6_bytes(graph6.encode("ascii"))
        except Exception as error:
            patch_counts["malformed_graph6"] += 1
            incomplete_records.append({"record_index": record_index, "reason": str(error)})
            continue
        if patch.number_of_nodes() != args.expected_patch_order or patch.number_of_edges() != args.expected_patch_edges:
            patch_counts["wrong_order_or_size"] += 1
            continue
        degrees = dict(patch.degree())
        ports = sorted(vertex for vertex, degree in degrees.items() if degree == 2)
        if len(ports) != 6 or any(degree not in (2, 3) for degree in degrees.values()) or sum(degree == 3 for degree in degrees.values()) != patch.number_of_nodes() - 6:
            patch_counts["wrong_degree_sequence"] += 1
            continue
        if not nx.is_connected(patch) or not nx.is_bipartite(patch) or not nx.check_planarity(patch, counterexample=False)[0]:
            patch_counts["failed_patch_predicates"] += 1
            continue
        patch_counts["accepted_patch_graphs"] += 1
        patch_coloring = nx.bipartite.color(patch)
        patch_port_colors = [int(patch_coloring[vertex]) for vertex in ports]
        mappings = color_compatible_maps(source_port_colors, patch_port_colors)
        if not mappings:
            patch_counts["color_incompatible"] += 1
            continue
        patch_language = exact_language(patch, ports, args.call_budget)
        patch_unknown = [state for state in patch_language if state["classification"] == "unknown"]
        if patch_unknown:
            patch_counts["unknown_patch_language"] += 1
            incomplete_records.append(
                {
                    "record_index": record_index,
                    "graph6": graph6,
                    "unknown_states": patch_unknown,
                }
            )
            continue
        patch_positive = [
            state for state in patch_language if state["classification"] == "verified_positive"
        ]
        patch_counts[f"language_size_{len(patch_positive)}"] += 1

        minimum_compatibility: int | None = None
        minimum_maps: list[tuple[int, ...]] = []
        for mapping in mappings:
            compatibility = sum(
                1
                for source_state in source_positive
                for patch_state in patch_positive
                if states_compatible(source_state, patch_state, mapping)
            )
            compatibility_histogram[str(compatibility)] += 1
            if minimum_compatibility is None or compatibility < minimum_compatibility:
                minimum_compatibility = compatibility
                minimum_maps = [mapping]
            elif compatibility == minimum_compatibility:
                minimum_maps.append(mapping)
            if compatibility != 0:
                continue
            zero_record = {
                "record_index": record_index,
                "patch_graph6": graph6,
                "patch_graph6_sha256": hashlib.sha256(graph6.encode("ascii")).hexdigest(),
                "patch_ports": ports,
                "patch_port_colors": patch_port_colors,
                "patch_language_size": len(patch_positive),
                "source_to_patch_mapping": list(mapping),
                "compatibility": 0,
            }
            zero_records.append(zero_record)

            offset = max(source_graph.nodes()) + 1
            relabel = {vertex: offset + vertex for vertex in patch.nodes()}
            assembled = source_core.copy()
            assembled.add_edges_from((relabel[left], relabel[right]) for left, right in patch.edges())
            glue_edges: list[Edge] = []
            for source_index, patch_index in enumerate(mapping):
                edge = ce(source_ports[source_index], relabel[ports[patch_index]])
                assembled.add_edge(*edge)
                glue_edges.append(edge)
            checks = graph_validation(assembled)
            candidate = {
                **zero_record,
                "glue_edges": [list(edge) for edge in sorted(glue_edges)],
                "graph_validation": checks,
            }
            if not checks["barnette_predicates"]:
                candidate["classification"] = "zero_language_non_barnette"
                continue

            candidate_graph6 = nx.to_graph6_bytes(assembled, header=False).decode("ascii").strip()
            candidate["candidate_graph6"] = candidate_graph6
            candidate["candidate_graph6_sha256"] = hashlib.sha256(
                candidate_graph6.encode("ascii")
            ).hexdigest()
            candidate_id = (
                f"six-port-n{args.expected_patch_order}-r{record_index:07d}-"
                f"{candidate['candidate_graph6_sha256'][:12]}"
            )
            candidate_dir = args.output_dir / candidate_id
            candidate_dir.mkdir(parents=True, exist_ok=True)
            proof_result = solve_case(
                assembled,
                {
                    "case_id": f"{candidate_id}-hamiltonicity",
                    "constraint_type": "whole_graph_hamiltonicity",
                    "include_edges": [],
                    "exclude_edges": [],
                },
                candidate_dir,
                args.solver,
                args.proof_solver,
                args.drat_trim,
                args.max_rounds,
                args.proof_timeout,
            )
            candidate["whole_graph_result"] = proof_result
            if proof_result["classification"] == "certified_negative" and proof_result.get(
                "proof_verification", {}
            ).get("verified", False):
                candidate["classification"] = "certified_counterexample_candidate"
            elif proof_result["classification"] == "verified_positive":
                candidate["classification"] = "language_composition_contradicted_by_witness"
            else:
                candidate["classification"] = "whole_graph_unknown"
                incomplete_records.append(candidate)
            valid_zero_candidates.append(candidate)

        if minimum_compatibility is None:
            raise SystemExit("no color-compatible mappings evaluated")
        best_records.append(
            {
                "record_index": record_index,
                "patch_graph6": graph6,
                "patch_graph6_sha256": hashlib.sha256(graph6.encode("ascii")).hexdigest(),
                "patch_language_size": len(patch_positive),
                "minimum_compatibility": minimum_compatibility,
                "minimum_maps": [list(mapping) for mapping in minimum_maps],
            }
        )
        if (record_index + 1) % 100 == 0:
            print(
                json.dumps(
                    {
                        "processed": record_index + 1,
                        "input_records": len(records),
                        "accepted_patch_graphs": patch_counts["accepted_patch_graphs"],
                        "current_best": min(
                            (item["minimum_compatibility"] for item in best_records),
                            default=None,
                        ),
                        "zero_maps": len(zero_records),
                    }
                ),
                flush=True,
            )

    best_records.sort(
        key=lambda item: (
            item["minimum_compatibility"],
            item["patch_language_size"],
            item["patch_graph6_sha256"],
        )
    )
    certified_candidates = [
        candidate
        for candidate in valid_zero_candidates
        if candidate.get("classification") == "certified_counterexample_candidate"
    ]
    summary = {
        "date_utc": "2026-08-03",
        "campaign": "canonical-six-port-closure-search",
        "source": {
            "graph6_sha256": hashlib.sha256(
                source_data["source"]["graph6"].encode("ascii")
            ).hexdigest(),
            "removed_edges": [list(edge) for edge in removed_edges],
            "ports": source_ports,
            "port_colors": source_port_colors,
            "positive_states": len(source_positive),
            "exact_negative_states": 75 - len(source_positive),
            "unknown_states": 0,
        },
        "patch_input": str(args.patch_input),
        "patch_input_sha256": hashlib.sha256(args.patch_input.read_bytes()).hexdigest(),
        "patch_order": args.expected_patch_order,
        "patch_edges": args.expected_patch_edges,
        "patch_counts": dict(patch_counts),
        "compatibility_histogram": dict(compatibility_histogram),
        "minimum_compatibility": min(
            (record["minimum_compatibility"] for record in best_records),
            default=None,
        ),
        "best_patches": best_records[:100],
        "zero_language_maps": zero_records,
        "zero_language_map_count": len(zero_records),
        "barnette_zero_candidates": valid_zero_candidates,
        "certified_counterexample_candidates": certified_candidates,
        "counterexample_found": bool(certified_candidates),
        "incomplete_records": incomplete_records,
        "complete_classification": not incomplete_records,
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
    }
    (args.output_dir / "campaign_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "patch_counts": dict(patch_counts),
                "minimum_compatibility": summary["minimum_compatibility"],
                "zero_language_map_count": len(zero_records),
                "barnette_zero_candidates": len(valid_zero_candidates),
                "certified_counterexample_candidates": len(certified_candidates),
                "incomplete_records": len(incomplete_records),
                "elapsed_s": summary["elapsed_s"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
