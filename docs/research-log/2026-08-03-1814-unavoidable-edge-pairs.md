# 2026-08-03 18:14 UTC — Unavoidable cofacial edge-pair breakthrough

**Status:** `verified` for all proof-certified relations  
**Counterexample found:** No

## Objective

Continue the direct face-amplifier program from the proof-certified candidate-489 ternary obstruction, beginning with the cheapest theorem-complete consecutive facial path test and escalating to the complete face-edge relation.

## Consecutive path campaign

A deterministic generator enumerated one canonical planar embedding of each 3-connected source graph and emitted every facial path of three consecutive edges as the constraint:

```text
exclude outer-left
include middle
exclude outer-right
```

Every positive result retained an independently validated Hamiltonian-cycle edge witness. Every nonpositive case was configured for CaDiCaL plus `drat-trim` escalation.

Results:

- candidate 489: `300 / 300` verified positive;
- 12 retained Grand-v3 order-96 parents: `3,456 / 3,456` verified positive;
- 12 retained Grand-v3 order-100 parents: `3,600 / 3,600` verified positive;
- combined: `7,356 / 7,356` verified positive;
- certified negative: `0`;
- unknown or provisional: `0`.

Interpretation:

The consecutive-three-edge facial failure mechanism is absent in candidate 489 and all 24 retained Grand-v3 parents. This closes the cheapest direct Hertel-style route for the tested parents.

## Exact candidate-489 face projection

The 12-edge face containing the original ternary obstruction has `4096` Boolean edge masks. Local degree constraints leave `322` masks.

A complete finite complement-perfect-matching recursion classified the locally feasible masks:

```text
100 Hamiltonian-positive
222 exact-negative
0 unknown
maximum recursive calls for any mask: 3124
```

The existing certified ternary assignment supplied an independent consistency check: its 21 locally feasible completions were all negative, matching the prior CaDiCaL/DRAT result.

Prime forbidden partial assignments within the local mask domain had widths:

```text
width 2:  8
width 3:  9
width 4: 14
width 7:  3
width 12: 1
```

## Independent proof certification of the width-two relations

The eight width-two cases were re-materialized without relying on the finite-enumeration negative classification and sent through the established proof-producing whole-graph constraint encoder.

Each case asks whether candidate 489 has a Hamiltonian cycle avoiding both designated cofacial edges.

Workflow result:

- run: `30840232014`;
- artifact: `8866489362`;
- artifact SHA-256: `5494440bb3e69f82df40e99729dd23460856ca79bd960ff8f934ca6668289a1a`;
- certified negative: `8 / 8`;
- positive contradictions: `0`;
- incomplete: `0`;
- all textual DRAT proofs accepted by `drat-trim`.

The exact new relation is:

```text
For each certified pair {a,b}, every Hamiltonian cycle contains a or b.
```

The pairs are:

```text
(5,10)  or (14,18)
(10,17) or (14,22)
(17,25) or (22,30)
(17,25) or (14,18)
(17,25) or (5,11)
(25,35) or (30,40)
(35,48) or (22,30)
(14,22) or (5,11)
```

## Strategic pivot

The original ternary primitive

```text
x => y or z
```

is superseded for construction purposes by the simpler monotone binary primitive

```text
a or b.
```

This is an `H^{--}` failure, not yet an `H^{-}` or `H^{+-}` failure. It does not by itself disprove Barnette's conjecture.

The immediate task is polarity conversion:

1. turn the unavoidable pair into a forced edge;
2. or produce a cofacial `H^{+-}` obstruction;
3. or synthesize a direct zero-compatible closure.

A forced edge is especially valuable because deleting an appropriate endpoint produces a three-terminal required-edge fragment, and three color-compatible copies can be assembled into a closed non-Hamiltonian candidate.

## Active experiment

All connected planar bipartite patch matrices on 6, 8, and 10 vertices with four degree-two ports were glued over certified pair `(5,10)/(14,18)` under every color-preserving port permutation.

After exact Barnette-predicate filtering and graph6 deduplication:

```text
4 valid expansions at patch order 6
0 valid expansions at patch order 8
432 valid expansions at patch order 10
436 total valid nonisomorphic expansions
```

Every newly introduced patch/glue edge is being tested for forced-edge status:

```text
7,388 exact edge-avoidance cases
```

Active workflow run:

```text
30842075897
```

## Evidence paths

- `search/generate_consecutive_face_cases.py`
- `search/run_consecutive_face_campaign.py`
- `search/generate_two_edge_avoidance_cases.py`
- `search/screen_small_patch_forced_edges.py`
- `.github/workflows/consecutive-facial-ternary-scan.yml`
- `.github/workflows/grand-v3-consecutive-facial-scan.yml`
- `.github/workflows/two-edge-avoidance-proof.yml`
- `.github/workflows/small-patch-forced-edge-screen.yml`
- `results/2026-08-03/facial_relation_breakthrough_summary.json`
- `docs/UNAVOIDABLE_EDGE_PAIRS_2026-08-03.md`

## Next action

Inspect all four forced-edge shards. If a checked negative appears, immediately construct and proof-check the required-edge fragment assembly. If all cases are positive, compute the exact four-terminal source language and synthesize a polarity inverter at relation level.
