#!/usr/bin/env python3
"""Corrected entry point for expansion_order_fallback.

This wrapper replaces two pre-run schema errors in the original module:

- randomized matching fragmentation uses `best_components`;
- hamiltonian_flow_milp must receive `time_limit` and `seed` by keyword because
  its first positional arguments are forced-edge constraints.

No result from the uncorrected entry point is valid or retained.
"""
from __future__ import annotations

import networkx as nx

import expansion_order_fallback as base


def ranking_key_fixed(record):
    fragmentation = record["fragmentation"]
    metrics = record["face_metrics"]
    return (
        -fragmentation["hamiltonian_hits"],
        fragmentation["best_components"],
        fragmentation["q05_components"],
        fragmentation["median_components"],
        fragmentation["mean_components"],
        metrics["sum_big_neighbor_excess"],
        metrics["max_face"],
    )


def exact_test_fixed(payload):
    record, time_limit, seed = payload
    graph = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
    result = base.evo.hamiltonian_flow_milp(
        graph,
        time_limit=time_limit,
        seed=seed,
    )
    result_dict = result.__dict__.copy()
    result_dict["cycle_validation"] = (
        base.cycle_validation(graph, result.cycle_edges)
        if result.cycle_edges
        else None
    )
    return {"pool_index": record["pool_index"], "hamiltonicity": result_dict}


base.ranking_key = ranking_key_fixed
base.exact_test = exact_test_fixed

if __name__ == "__main__":
    base.main()
