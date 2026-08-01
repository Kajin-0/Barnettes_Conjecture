# Canonical Structural Search for a Barnette Counterexample

**Date:** 2026-08-01  
**Result:** No counterexample found.

## 1. Search objective

This campaign replaced expansion-history sampling with canonical generation at the first order beyond the published exhaustive frontier and attacked Hamiltonicity through four-terminal separator states.

The target was a pair or sequence of planar bipartite cubic patches whose Hamiltonian boundary states are incompatible. Such an incompatibility would prove non-Hamiltonicity compositionally before a whole-graph SAT calculation.

## 2. Canonical 92-vertex input

Official plantri 5.8 was compiled from the ANU distribution.

```text
plantri archive SHA-256:
e78a944116fec9f2c9f5e484206276cc2b0043bae803e9815f4b2683614629b8

generation form:
plantri -bc4dg 92d RES/10000
```

Eight disjoint `res/mod` classes were sampled, taking the first 300 graph6 outputs from each class.

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

A cyclic 4-edge cut exposes four terminals on each side. Its Hamiltonian boundary signature contains:

- six possible one-path labels `Pij`;
- three possible two-path labels `Qij_kl`.

For a planar bipartite four-terminal patch, only six of the nine labels can be structurally feasible:

- four `P` states survive bipartition parity;
- two `Q` states survive noncrossing planarity.

A six-state signature is therefore maximal.

## 4. Clean CI result: every natural cut side was maximal

Separating 4-cycles were enumerated in the planar dual. Each corresponds to a cyclic 4-edge cut in the primal graph. A clean GitHub Actions rerun used SciPy 1.18.0 and validated every feasible state by an explicit selected-edge witness.

| Quantity | Result |
|---|---:|
| Cyclic 4-edge cuts | 647 |
| Cut sides tested | 1,294 |
| Complete signatures | 1,294 |
| Maximal six-state signatures | 1,294 |
| Restrictive signatures | 0 |
| Unresolved signatures | 0 |

Across all planar, bipartition-preserving dihedral gluings:

| Compatible state-pair count | Number of patch-map pairs |
|---:|---:|
| 6 | 1,283,456 |
| 0–5 | 0 |

Thus every one of the **1,283,456** patch-map comparisons had all six structurally possible compatible state pairs.

The CI artifact SHA-256 is:

```text
fd22be4b51b1d950391f8349697d5842e59b5b58f60b246aef9d08a57f5d104d
```

## 5. Solver discrepancy and retraction

An earlier local run under SciPy 1.17.0 reported two apparent five-state patches. Those negative decisions were incorrect.

The clean SciPy 1.18.0 rerun produced explicit spanning-path witnesses for both supposedly missing states:

- patch `c156-s0`, state `P23`;
- patch `c446-s1`, state `P01`.

Each witness was independently checked to satisfy:

1. every selected edge belongs to the patch;
2. exactly `n-1` edges are selected;
3. the selected subgraph is connected;
4. the requested two terminals have degree one;
5. every other patch vertex has degree two.

Therefore the earlier `HiGHS Status 8: Infeasible` results were false infeasibility reports. The restrictive-patch claim and certificates were retracted.

This changes the validation policy:

> A single MILP solver's infeasibility status is not accepted as mathematical evidence. Any future negative boundary state must be confirmed by an independent formulation or a proof-producing SAT solver.

Positive witnesses remain conclusive because they can be checked directly without trusting the solver's status code.

## 6. Edge-deletion four-poles

Deleting the endpoints of each of the strongest graph's 138 edges produced 138 four-terminal patches. All 138 had explicit witnesses for all six structurally possible states.

This reinforces the conclusion that adjacent-vertex deletion is too flexible to supply a counterexample gadget in this sample.

## 7. Partial and annular composition

The previously tested partial compositions all had positive witnesses for maximal six-state signatures. That positive conclusion is unaffected by the false-negative issue.

For nested-cut annuli, 200 conservative 9-by-9 transfer relations were constructed from positively witnessed entries. Even under this potentially strict under-approximation:

- every relation contained 26 witnessed entries;
- 12 labelled relation patterns occurred;
- no product of two tested relations was empty;
- the smallest product contained 43 witnessed entries.

Because false negatives can only omit true entries, non-emptiness of these conservative products is robust. The exact cardinalities should not be treated as proof-complete until negative entries are independently certified.

## 8. Interpretation

The strongest conclusion is negative for this construction route:

1. Every natural cyclic-4-cut side of the leading canonical 92-vertex graph was maximally Hamiltonian-flexible.
2. Every planar gluing retained all six compatible boundary states.
3. Edge-deletion four-poles were also maximal.
4. Conservative annular relations remained nonempty under composition.

This strongly disfavors a counterexample assembled from ordinary cyclic-4-cut pieces of this graph. It does not exclude restrictive patches in other canonical graphs or at larger orders.

## 9. Highest-value next experiment

The next search should move to orders 94, 96, 98 and 100 and optimize directly for missing noncrossing `Q` states or sparse annular transfer relations.

Recommended pipeline:

1. Generate canonical cyclically 4-connected Barnette graphs with plantri shards.
2. Enumerate natural cyclic 4-cut sides.
3. Search the two noncrossing `Q` states first.
4. Validate every positive state by an explicit edge witness.
5. Treat every apparent negative state as provisional.
6. Re-encode provisional negatives with an independent SAT formulation.
7. Require an independently checked UNSAT proof before retaining a missing-state gadget.
8. Build exact annular transfer relations only from verified state decisions.
9. Search the Boolean transfer semigroup for an empty product.
10. If a full graph is produced, verify the Barnette predicates and whole-graph Hamiltonicity with proof logging.

The primary progress metric is:

```text
number of independently certified missing noncrossing Q states
```

At present that number is **zero**.

## 10. Reproducibility

The repository branch includes:

- canonical plantri preparation;
- natural cyclic-cut enumeration;
- boundary-state witness generation;
- the solver-discrepancy regression record;
- the successful GitHub Actions workflow and artifact manifest.

No current counterexample or certified restrictive four-pole is claimed.
