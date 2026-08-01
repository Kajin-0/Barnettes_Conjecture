# Canonical Structural Search for a Barnette Counterexample

**Date:** 2026-08-01  
**Result:** No counterexample found.

## 1. Search objective

This campaign replaced expansion-history sampling with canonical generation at the first order beyond the published exhaustive frontier and then attacked Hamiltonicity through exact separator-state calculations.

The structural target was a pair or sequence of planar bipartite cubic patches whose Hamiltonian boundary states are incompatible. Such an incompatibility would prove non-Hamiltonicity compositionally, before a whole-graph SAT or MILP calculation.

All negative state decisions reported here are solver-proven infeasibility decisions. Timeouts were classified as unknown and rerun at a longer budget.

## 2. Canonical 92-vertex input

Official plantri 5.8 was compiled from the ANU distribution.

```text
plantri archive SHA-256:
e78a944116fec9f2c9f5e484206276cc2b0043bae803e9815f4b2683614629b8

generation form:
plantri -bc4dg 92d RES/10000
```

The run sampled eight disjoint `res/mod` classes and retained the first 300 graph6 outputs from each class:

| Quantity | Result |
|---|---:|
| Canonical non-isomorphic graphs read | 2,400 |
| Correct 92-vertex cubic bipartite planar inputs | 2,400 |
| Rejected because every face has size at most 8 | 0 |
| Rejected because every face has at most 4 big-face neighbours | 58 |
| Graphs escaping both filters | 2,342 |
| Highest-ranked graphs retained | 8 |

This is a distributed canonical sample, not an exhaustive enumeration and not a statistically uniform random sample.

The eight retained graphs produced no Hamiltonian complement in 128 randomized perfect-matching trials each. Their best sampled complementary 2-factors had eight components. These statistics were used only for ranking.

## 3. Four-terminal state model

A cyclic 4-edge cut exposes four terminals on each side. The Hamiltonian boundary signature contains:

- six possible one-path labels `Pij`;
- three possible two-path labels `Qij_kl`.

For a planar bipartite patch with four boundary terminals, at most six of the nine labels are structurally possible:

- four `P` states survive bipartition parity;
- two `Q` states survive noncrossing planarity.

A six-state signature is therefore maximal.

Each state was solved with an exact mixed-integer formulation enforcing the required terminal degrees and either one connected spanning path or two connected spanning paths with the specified pairing.

## 4. Edge-deletion four-poles

For the strongest canonical graph, deleting the endpoints of each of its 138 edges gives a four-terminal patch.

| Quantity | Result |
|---|---:|
| Edge-deletion patches | 138 |
| Complete exact signatures | 138 |
| Maximal six-state signatures | 138 |
| Restrictive signatures | 0 |

This establishes that adjacent-vertex deletion is too flexible on this graph and is not a promising gadget source.

## 5. Natural cyclic 4-edge-cut patches

Separating 4-cycles were enumerated in the planar dual. Each corresponds to a cyclic 4-edge cut in the primal graph.

| Quantity | Result |
|---|---:|
| Cyclic 4-edge cuts | 647 |
| Cut sides tested | 1,294 |
| Complete exact signatures after retry | 1,294 |
| Maximal six-state signatures | 1,292 |
| Exact five-state signatures | 2 |
| Missing two-path `Q` states | 0 |

Across all planar, bipartition-preserving dihedral gluings:

| Compatible state-pair count | Number of patch-map pairs |
|---:|---:|
| 6 | 1,278,132 |
| 5 | 5,315 |
| 4 | 9 |
| 0 | **0** |

Thus all **1,283,456** exact patch-map comparisons had a Hamiltonian-compatible state pair.

### 5.1 Restrictive patch `c156-s0`

This 40-vertex patch has exact signature

```text
P01, P03, P12, Q01_23, Q03_12
```

The otherwise allowed state `P23` is infeasible. The MILP returned solver status 2 (`infeasible`), not a timeout.

### 5.2 Restrictive patch `c446-s1`

This 40-vertex patch has exact signature

```text
P03, P12, P23, Q01_23, Q03_12
```

The otherwise allowed state `P01` is infeasible, again with solver status 2.

These are the first exact local Hamiltonian restrictions found in the project. They are genuine structural obstructions, but they are not sufficient to form a counterexample because both patches retain both noncrossing `Q` states.

## 6. Partial composition of restrictive patches

The two restrictive four-poles were partially composed by joining two boundary terminals from each patch and leaving four terminals exposed. All adjacent boundary arcs, both orientations, and all ordered parent choices were attempted.

| Quantity | Result |
|---|---:|
| Composition parameter combinations | 128 |
| Valid planar bipartite four-poles | 10 |
| Complete exact signatures | 10 |
| Maximal six-state signatures | 10 |
| Incompatible final gluings | 0 |

The two missing path states did not compound. Every valid partial composition restored the maximal signature.

## 7. Two-interface annular transfer relations

Nested cyclic 4-cuts define annular patches with an inner and outer four-terminal boundary. These patches can contain correlations that are invisible in either one-boundary marginal.

For each annulus, every pair of boundary states was represented by forced virtual cap edges and tested by an exact connected degree-2 MILP. This produces a Boolean 9-by-9 transfer relation.

| Quantity | Result |
|---|---:|
| Candidate annuli in strongest graph | 2,084 |
| Diverse annuli exact-tested | 200 |
| Complete relations | 200 |
| True entries per relation | 26 for every annulus |
| Distinct labelled relation patterns | 12 |
| Empty two-annulus products | 0 |
| Minimum true entries in a two-annulus product | 43 |

Rather than shrinking, pairwise composition expanded the reachable relation from 26 entries to at least 43. No two-interface obstruction appeared in this sample.

## 8. Interpretation

The search found a real local phenomenon but not a viable counterexample mechanism:

1. Almost every natural four-pole was maximally Hamiltonian-flexible.
2. The two restrictive four-poles each lost only one path state.
3. Every two-path state remained feasible.
4. Partial composition erased, rather than amplified, the restrictions.
5. The tested annular transfer relations were nonempty and compositionally expansive.

This strongly disfavors a counterexample assembled from ordinary cyclic-4-cut pieces at order 92. It does not prove that no such construction exists outside the sample or at larger order.

## 9. Highest-value next experiment

The next search should optimize directly for **missing `Q` states** and sparse annular relations.

Recommended pipeline:

1. Generate canonical cyclically 4-connected Barnette graphs at orders 94, 96, 98, and 100 with plantri shards.
2. Enumerate natural cyclic 4-cut sides.
3. Solve the two noncrossing `Q` states first; discard patches where both are feasible.
4. Retain any patch with a solver-proven missing `Q` state.
5. Compute full signatures only for that extreme tail.
6. Build exact annular transfer relations around nested restrictive cuts.
7. Search the Boolean transfer semigroup for an empty product.
8. Construct the resulting graph and verify cubicity, bipartiteness, planarity, and 3-connectivity.
9. Encode whole-graph Hamiltonicity with proof logging and independently check an LRAT or DRAT UNSAT certificate.

The primary progress metric is no longer graph order or MILP runtime. It is

```text
number of exact patches missing a noncrossing Q state
```

because a one-cut incompatibility is effectively impossible while both patches retain both `Q` states.

## 10. Reproducibility

The repository branch includes:

- canonical plantri preparation;
- exact cyclic-cut patch enumeration;
- exact boundary-state MILPs;
- restrictive patch certificates;
- compact annular transfer summaries;
- the GitHub Actions workflow and artifact manifests.

No timeout is represented as an infeasibility result.
