# Proof-Certified Unavoidable Cofacial Edge Pairs

**Date:** 2026-08-03  
**Status:** verified exact relation; no counterexample yet  
**Source:** canonical order-100 candidate 489

## Result

The complete consecutive-three-edge route was tested first.

Across candidate 489 and the 24 retained Grand-v3 order-96/order-100 parents:

| Parent set | Parents | Consecutive facial paths | Verified positive | Certified negative | Unknown |
|---|---:|---:|---:|---:|---:|
| Candidate 489 | 1 | 300 | 300 | 0 | 0 |
| Grand-v3 order 96 | 12 | 3,456 | 3,456 | 0 | 0 |
| Grand-v3 order 100 | 12 | 3,600 | 3,600 | 0 | 0 |
| **Total** | **25** | **7,356** | **7,356** | **0** | **0** |

Thus the theorem-complete consecutive path condition

```text
outer-left absent, middle present, outer-right absent
```

has an explicit independently validated Hamiltonian-cycle witness in every tested case.

The face-internal program then examined the full Boolean edge-mask projection of candidate 489's 12-edge face 2. A finite complement-perfect-matching enumeration classified all 322 masks surviving local degree constraints:

```text
100 Hamiltonian-positive masks
222 exact-negative masks
0 unknown masks
```

The smallest prime forbidden partial assignments had width two. Eight cofacial edge pairs were found for which no Hamiltonian cycle avoids both edges.

Every one of these eight cases was independently re-encoded by the existing lazy-connectivity Hamiltonicity SAT encoder. CaDiCaL solved the final CNF UNSAT and `drat-trim` accepted the textual proof in all eight cases.

Therefore candidate 489 has eight exact relations of the form

```text
for every Hamiltonian cycle C: a in C or b in C
```

or equivalently

```text
no Hamiltonian cycle avoids both a and b.
```

## Certified pairs

Face 2 has cyclic edge order:

| Index | Edge |
|---:|---|
| 0 | `(5,10)` |
| 1 | `(10,17)` |
| 2 | `(17,25)` |
| 3 | `(25,35)` |
| 4 | `(35,48)` |
| 5 | `(40,48)` |
| 6 | `(30,40)` |
| 7 | `(22,30)` |
| 8 | `(14,22)` |
| 9 | `(14,18)` |
| 10 | `(11,18)` |
| 11 | `(5,11)` |

The certified unavoidable pairs are:

```text
(0,9)   (5,10)  or (14,18)
(1,8)   (10,17) or (14,22)
(2,7)   (17,25) or (22,30)
(2,9)   (17,25) or (14,18)
(2,11)  (17,25) or (5,11)
(3,6)   (25,35) or (30,40)
(4,7)   (35,48) or (22,30)
(8,11)  (14,22) or (5,11)
```

Each pair admits at least 21 locally degree-feasible face-mask completions. The impossibility is therefore global and not a trivial adjacent-edge degree contradiction.

Proof evidence:

- workflow run `30840232014`;
- artifact ID `8866489362`;
- artifact SHA-256 `5494440bb3e69f82df40e99729dd23460856ca79bd960ff8f934ca6668289a1a`;
- eight final CNFs and eight checked DRAT proofs;
- no positive contradiction;
- no timeout, malformed case, provisional result, or unknown classification.

Machine-readable proof hashes are recorded in:

```text
results/2026-08-03/facial_relation_breakthrough_summary.json
```

## Why this is stronger than the previous ternary primitive

The previous principal obstruction was

```text
x => y or z
```

which forbids one three-edge assignment.

The new relation is a monotone width-two clause:

```text
a or b
```

It imposes no required included edge in its statement and has only two designated facial edges. This significantly reduces the selector complexity required for amplification.

It is not, by itself, a Barnette counterexample. The relation has the wrong polarity for the standard Kelmans `H^{+-}` amplification: it forbids `a- b-`, whereas Kelmans uses a failure of `x+ y-`.

## Required polarity conversion

The immediate construction problem is now:

> Build a simple cubic bipartite planar 3-connected local network that transforms the certified clause `a or b` into one of the following:
>
> 1. a forced edge in a Hamiltonian Barnette graph;
> 2. a cofacial `H^{+-}` obstruction;
> 3. a closed Barnette graph whose exact Hamiltonian boundary-language composition is empty.

The forced-edge target is particularly attractive. Deleting the opposite endpoint of a forced edge gives a three-terminal required-edge fragment. Three correctly colored copies can then be assembled in the standard Tutte/Horton pattern, after which the final graph is sent to whole-graph proof-producing SAT.

The required-edge-fragment route is also independently motivated in the literature: a cubic, 3-connected, bipartite, planar required-edge fragment would immediately supply standard non-Hamiltonian assemblies and would imply NP-completeness of Hamiltonicity in the Barnette class if the conjecture is false.

## Completed local negative information

Two naive converter families have already been eliminated analytically or exactly:

1. **Single `C4` replacement.** For these odd-separation facial pairs, the orientation preserving bipartiteness is nonplanar, while the planar orientation is nonbipartite.
2. **Small direct closure patches over pair `(0,9)`.** Every simple cubic bipartite planar 3-connected expansion obtained from all connected planar 6-, 8-, and 10-vertex bipartite patch matrices was Hamiltonian under exact search. This family contains 436 nonisomorphic valid expanded graphs.

The second fact does not eliminate the family as a source of a forced edge. A Hamiltonian graph may still contain an edge present in every Hamiltonian cycle.

## Active exact campaign

The current workflow enumerates the complete 436-graph small-patch family over pair `(0,9)`:

```text
patch order 6:   4 valid nonisomorphic expansions
patch order 8:   0 valid expansions
patch order 10: 432 valid nonisomorphic expansions
```

Every newly introduced patch or glue edge is tested for an avoiding Hamiltonian cycle:

```text
7,388 exact edge-avoidance cases
```

Positive classifications require explicit independently checked cycles. Any nonpositive case is escalated to CaDiCaL and accepted as forced only if `drat-trim` verifies the proof.

Active workflow:

```text
30842075897
```

## Decision tree

1. **A forced edge is found.**
   - materialize the exact graph and construction;
   - convert it into a three-terminal required-edge fragment;
   - assemble three color-compatible copies;
   - verify every Barnette predicate;
   - generate and independently check a whole-graph UNSAT proof.
2. **All 7,388 cases are positive.**
   - compute the exact four-terminal language of the cut source pair;
   - synthesize a relation-level polarity inverter rather than testing whole patches blindly;
   - enlarge patch order only under exact language incompatibility objectives.
3. **Any case is unknown.**
   - preserve it as unknown;
   - rerun with an independent encoding and increased proof budget;
   - make no negative claim.

No counterexample is claimed at this checkpoint.
