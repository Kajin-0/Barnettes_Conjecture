# Research checkpoint: exact dual 12-disk substitution search

**Timestamp:** 2026-08-04 02:30 UTC  
**Counterexample found:** No

## New complete low-order construction campaign

Plantri 5.8 directly generates triangulations of a disk with a distinguished outer face. The search now replaces candidate 489's degree-12 dual vertex by every canonical chordless 12-boundary disk triangulation at total disk orders 13 through 18.

These disk orders produce closed dual orders 52 through 57 and primal cubic orders 100 through 110.

## Exact parity criterion

After removing the degree-12 dual vertex, each boundary vertex has odd outside degree. A disk closes to an even triangulation exactly when:

```text
all 12 boundary degrees in the disk are odd;
all internal disk degrees are even.
```

The filter is therefore exact, not heuristic.

## Search transaction

For every parity-valid canonical disk:

1. test all 24 dihedral boundary maps;
2. deduplicate assembled dual graphs;
3. require planarity, triangulation edge count, all-even degrees, and vertex connectivity at least four;
4. dualize and independently verify every Barnette predicate;
5. screen Hamiltonicity with an exact lazy-cut SAT oracle;
6. escalate every provisional negative to both the primal edge encoding and the dual face-color/two-tree encoding;
7. accept a counterexample only if both CaDiCaL DRAT proofs are accepted by `drat-trim`.

## Implementation and execution

- script: `search/dual_disk_substitution_search.py`
- workflow: `.github/workflows/dual-disk-substitution-search.yml`
- temporary execution PR: #9
- workflow run: `30871892938`

## Structural source-recovery regression

The order-13 star disk—one internal vertex adjacent to the entire 12-cycle—was assembled locally under all 24 dihedral maps.

```text
24/24 closures isomorphic to candidate 489's 52-vertex dual;
dual connectivity = 4;
all dual degrees even;
dualization returns a 100-vertex cubic bipartite graph isomorphic to candidate 489.
```

This validates the boundary identification and gluing geometry. It does not replace the order-13 Actions SAT/proof regression.

Evidence:

- `results/2026-08-04/dual_disk_source_recovery_regression.json`
