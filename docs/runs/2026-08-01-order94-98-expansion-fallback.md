# Order-94/98 Pure-C4 Expansion Fallback

**Date:** 2026-08-01  
**Status:** active  
**Counterexample found at start:** no

## Motivation

Canonical plantri shards at orders 94 and 98 exhibit much higher first-output latency than the corresponding order-96 and order-100 shards. The search must not leave those orders untested while waiting for sparse canonical residue classes.

This campaign supplies an independent, noncanonical population at exactly 94 and 98 vertices through pure facial C4 expansions.

## Seeds

Generate every canonical cyclically 4-connected bipartite cubic planar graph at orders:

```text
18, 22, 26, 30
```

using official plantri 5.8:

```text
plantri -bc4dg ORDERd
```

All target differences are divisible by four, so the target orders can be reached using only C4 expansions.

## Population

For each target order:

- generate 480 independent expansion histories;
- sample seeds uniformly from the complete small-order seed library;
- choose among six expansion biases: `uniform`, `large-main`, `large-sides`, `cluster`, `balanced`, and `four-face`;
- deduplicate exact graph6 encodings;
- independently validate cubicity, bipartiteness, planarity, simplicity, and 3-connectivity;
- retain graphs escaping both implemented face-based sufficient-condition filters;
- evaluate 256 randomized perfect-matching complements per eligible graph;
- retain the 12 strongest matching-fragmentation candidates.

Matching fragmentation is a ranking heuristic only.

## Exact tests

For every retained parent graph:

1. exact whole-graph Hamiltonicity with an independently validated cycle witness;
2. collision-safe natural cyclic-4-cut enumeration;
3. up to 320 cut-side patches per graph;
4. exact testing of both noncrossing Q states;
5. independent SAT and DRAT escalation for every nonpositive Q result.

## Evidence policy

- positive Hamiltonian or Q-state claims require explicit independently checked edge witnesses;
- MILP infeasibility is provisional only;
- a negative Q state requires a final-CNF CaDiCaL UNSAT proof accepted by drat-trim;
- a whole-graph counterexample requires independent Barnette-predicate validation and proof-checked non-Hamiltonicity;
- timeout and solver failure remain unknown.

## Limitations

This is not canonical enumeration at orders 94 or 98. Different histories may yield isomorphic graphs despite graph6 deduplication. The campaign is an adversarial population search intended to cover those exact orders while canonical generation proceeds separately.
