# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative research PR:** PR #1, temporarily closed and unmerged  
**Snapshot timestamp:** 2026-08-04, degree-8 semantic-descent checkpoint  
**Counterexample found:** No

This is the canonical mutable snapshot. Every material result must be committed as code or a reproducible specification, machine-readable evidence, a dated log, and an updated interpretation. Timeouts, branch cutoffs, sampled misses, provisional infeasibility, malformed cases, and queued jobs are always `unknown`.

## 1. Acceptance standard

A Barnette counterexample requires independent verification of simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three; exact primal non-Hamiltonicity; exact failure of the dual two-induced-tree formulation; checked proof certificates; and complete graph/construction provenance.

## 2. Certified source

Candidate 489 is a 100-vertex simple cubic bipartite planar 3-connected graph with a proof-certified same-face obstruction on its distinguished 12-face. Six source cases have CaDiCaL DRAT proofs accepted by `drat-trim`.

## 3. Complete one-face bound through order 112

```text
disk classes = 4,243
valid closure constructions = 46,672
tested encodings = 46,109
Hamiltonian = 46,109
negative = 0
unknown = 0
```

Any counterexample in that one-face family requires primal order at least 114.

## 4. Complete minimum two-face extension

```text
distinct graph encodings = 34,434
Hamiltonian = 34,434
negative = 0
unknown = 0
```

## 5. Boundary-directed degree-4/6 result

Degree-4 disk language is rigid through k=8. Targeted degree-4 and degree-6 higher-order closures gave 784/784 Hamiltonian.

## 6. Degree-8 semantic descent

The variable degree-8 interface produced the first repeated exact contractions of the original 12-seam language:

```text
421_32_6                      118 masks
first disjoint B8 replacement 111 masks
second disjoint B8 replacement 75 masks
```

The first replacement is a 116-vertex Barnette graph; the second is a 120-vertex Barnette graph. Both are Hamiltonian as whole graphs, but their seam languages were classified exactly over all 2,048 complement-normalized colorings with zero unknowns.

The complete first-face B8 k=2..5 bounded families contained 336 graphs, all Hamiltonian. The complete geometry-filtered second disjoint-face B8 k=2..6 family contained 1,136 graphs, all Hamiltonian.

Relabeled vertex 14 in the 111-mask source was rejected as a fixed-seam target because it belongs to the original seam. The descent used disjoint vertex 23.

Evidence:

- `docs/DEGREE8_SEMANTIC_DESCENT_2026-08-04.md`
- `results/2026-08-04/degree8_semantic_descent_summary.json`

## 7. Strongest active strategy

The active source is the exact 75-mask order-120 graph:

```text
421_32_6__v2_B8_k3_300_0_m3__v23_B8_k3_300_0_m5
```

Execution sequence:

1. rank only faces disjoint from the original 12-seam;
2. compute the complete exact seam/face relation for the best variable degree-8 face;
3. impose even-sphere and dual 4-connectivity before semantic ranking;
4. classify the original seam language of the strongest valid closures exactly;
5. repeat while language cardinality decreases;
6. if the descent stalls, move to the exact two-boundary forest-partition relation;
7. send every whole-graph nonpositive result to independent primal and dual proof-producing SAT.

The direct breakthrough target is a geometry-valid sequence reducing 75 masks to zero.

## 8. Permanent corrections

- An initial boundary-mask MILP had a variable-index collision from noncontiguous dual labels; contaminated results were deleted and recomputed.
- Initial two-seam queries used radial edges; the correct replacement boundary is the neighbor link cycle.
- A face lying on the original seam cannot be used for fixed-seam descent without changing the optimized boundary.

PR #1 remains temporarily closed to prevent obsolete workflow fan-out. The branch remains authoritative.
