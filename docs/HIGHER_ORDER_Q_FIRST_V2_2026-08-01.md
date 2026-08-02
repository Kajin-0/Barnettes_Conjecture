# Higher-Order Q-First Search v2

**Date:** 2026-08-01  
**Status:** verified positive witnesses; generation failures classified as unknown  
**Counterexample found:** no

## Objective

Search canonical Barnette graphs above the published 90-vertex exhaustive frontier for a natural cyclic-4-cut side with a missing noncrossing two-path boundary state.

The two tested states were:

```text
Q01_23
Q03_12
```

A proof-certified missing state would provide a restrictive four-pole suitable for targeted compositional synthesis.

## Corrected collision-safe driver

The v2 driver namespaces each patch as:

```text
g<graph-index>-c<cut-index>-s<side-index>
```

It asserts uniqueness before and after parallel execution. This corrects the earlier risk that independently numbered cuts from different parent graphs could overwrite one another.

## Workflow and proof policy

Workflow run:

```text
30702896816
```

Positive states were accepted only when an explicit selected-edge witness independently satisfied:

1. every selected edge belongs to the patch;
2. no selected edge is duplicated;
3. all four terminals have selected degree one;
4. every internal vertex has selected degree two;
5. the selected subgraph has exactly two components;
6. the components realize the requested terminal pairing;
7. the selected edge count equals `|V(P)| - 2`.

A MILP infeasibility status would remain provisional. Final negative certification requires a CaDiCaL proof log accepted independently by `drat-trim`. Timeouts and failures remain unknown.

## Verified orders 96 and 100

| Quantity | Order 96 | Order 100 | Combined |
|---|---:|---:|---:|
| Canonical graphs sampled | 4,800 | 4,800 | 9,600 |
| Escaped implemented sufficient-condition filters | 4,740 | 4,738 | 9,478 |
| Parent graphs exactly analyzed | 6 | 6 | 12 |
| Natural cut-side patches available in those graphs | 8,620 | 9,112 | 17,732 |
| Patch sides selected | 1,920 | 1,920 | 3,840 |
| Q states attempted | 3,840 | 3,840 | 7,680 |
| Verified positive Q states | 3,840 | 3,840 | 7,680 |
| Provisional negative Q states | 0 | 0 | 0 |
| Unknown Q states | 0 | 0 | 0 |
| Independently certified missing Q states | 0 | 0 | 0 |

All 7,680 attempted states had explicit independently validated positive witnesses.

Artifacts:

| Order | Artifact ID | Artifact SHA-256 |
|---:|---:|---|
| 96 | `8819552108` | `ac2e219a86811b11fc646b9d5b012eac55e0a2b1f2db5b89d693c62ff675d591` |
| 100 | `8819569587` | `0b4cfbab9b08c896dedc76404c01f56845597d404cc6fc2f3067f246aaad9188` |

## Orders 94 and 98

Orders 94 and 98 did not reach graph analysis.

Each job requested 12 sparse plantri classes of the form:

```text
plantri -bc4dg ORDERd RES/10000
```

Each class was terminated after 240 seconds. No graph6 record was flushed before the timeout, so the aggregate file was empty and the generation step failed closed.

This is a computational sampling failure, not mathematical evidence. Both orders remain completely unresolved by this campaign.

Failure artifacts:

| Order | Artifact ID | Artifact SHA-256 |
|---:|---:|---|
| 94 | `8819920926` | `3ae10ebade6ecf1bd9ce0b6d380a8e33824bccb1506f7491d90970ed4e835eb8` |
| 98 | `8819920196` | `9fdf81b989abfce74b989924bb72ddcd31495eae8e6c0808227df52476f809d5` |

The failure mode is consistent with sparse `RES/10000` startup latency combined with buffered graph6 output. The repair should use an output-flushing wrapper or minimal source patch, lower-modulus adaptive classes, per-class parallelism, and explicit preservation of partial output.

## Interpretation

The v2 campaign significantly strengthens the negative evidence against the simplest local-obstruction hypothesis:

> A counterexample can be exposed by finding an ordinary natural cyclic-4-cut side lacking one of the two noncrossing Q states.

That mechanism did not appear in 7,680 exact state tests across 12 high-ranked canonical graphs at orders 96 and 100.

This does not imply that every natural patch has both Q states. The campaign examined only 3,840 of 17,732 available cut sides in the selected parent graphs and only 12 parent graphs from 9,600 canonical samples.

The result does indicate that further work should not rely exclusively on marginal four-terminal signatures. Higher-value targets now include:

1. completion of all natural cut sides in a broader high-ranked parent set;
2. multi-interface annular transfer relations that preserve correlations hidden by full one-boundary marginals;
3. proof-oriented synthesis of patches or transfer products with missing states;
4. exact Hamiltonian-cycle scarcity metrics rather than nonuniform matching-fragmentation sampling alone.

## Next campaign

The next autonomous campaign should combine two tracks.

### Track A: complete and broaden Q-state coverage

- repair order-94 and order-98 generation;
- analyze all natural cut sides, not only 320 per graph, for the strongest order-96 and order-100 parents;
- expand the number of retained parents;
- retain explicit witnesses and pass every nonpositive case to independent SAT.

### Track B: search higher-order correlations

- construct exact or conservative two-interface transfer relations for nested cyclic 4-cuts;
- rank annuli by relation sparsity and failure to compose densely;
- independently certify every candidate missing relation entry;
- search the Boolean relation semigroup for an empty product;
- assemble and independently verify any resulting Barnette graph.

The primary certified progress metric remains:

```text
independently certified missing noncrossing Q states = 0
```

A second metric should now be tracked:

```text
minimum independently verified annular transfer-product cardinality
```

No counterexample is claimed.
