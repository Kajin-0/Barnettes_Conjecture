# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative research PR:** PR #1, temporarily closed and unmerged  
**Snapshot timestamp:** 2026-08-04 17:20 UTC  
**Counterexample found:** No

This is the canonical mutable snapshot. Dated reports and `docs/research-log/` preserve chronology. A counterexample claim remains prohibited without independent Barnette checks, exact primal and dual non-Hamiltonicity, and checked proof certificates.

## 1. Objective and acceptance standard

Barnette's conjecture states that every simple cubic 3-connected bipartite planar graph is Hamiltonian.

A counterexample requires:

1. simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three checked independently;
2. exact whole-graph non-Hamiltonicity in a primal selected-edge formulation;
3. exact failure of the dual two-induced-tree formulation;
4. checked CaDiCaL DRAT/LRAT certificates or comparably transparent exhaustive certificates;
5. graph6, edge list, construction manifest, software versions, commands, and hashes.

Timeouts, solver cutoffs, sampled misses, provisional infeasibility, malformed cases, and queued jobs are `unknown`.

## 2. Strongest source: candidate 489

Candidate 489 is a verified 100-vertex simple cubic bipartite planar 3-connected graph. Its distinguished 12-face has cyclic order

```text
5, 10, 17, 25, 35, 48, 40, 30, 22, 14, 18, 11
```

The principal certified facial obstruction is

```text
(14,18) included
(10,17) excluded
(5,11) excluded
```

No Hamiltonian cycle satisfies this pattern. Six source cases have CaDiCaL textual DRAT proofs accepted by `drat-trim`.

Evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- workflow `30750008325`
- artifact `8834131003`
- artifact SHA-256 `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`

Its dual is a simple even 4-connected plane triangulation with 52 vertices and 150 edges. Removing the degree-12 vertex corresponding to the distinguished face leaves boundary order

```text
3, 6, 10, 18, 26, 29, 21, 16, 9, 5, 11, 0
```

## 3. Uniform dual-substitution theorem through order 112

The earlier order-specific disk generators have been superseded by one exact link-cycle generator:

```text
search/uniform_dual_cycle_disk_generator.py
```

Restore the removed dual vertex as a color-0 apex. For a disk with `k` internal vertices, the augmented even sphere triangulation has `13+k` vertices. Every face is rainbow, so

```text
E01 = E02 = E12 = 11 + k
```

The color-1/color-2 graph therefore consists of the fixed 12-cycle plus exactly `k-1` extra edges. Internal color-0 vertex links form simple alternating cycles such that:

```text
boundary H12 edges have multiplicity 1
extra H12 edges have multiplicity 2
```

A candidate is retained only when its rainbow triangles form a connected closed complex with Euler characteristic two and every vertex link is one cycle. This is an exact combinatorial sphere certificate.

### Complete result

Every parity-valid triangulated 12-disk with one through seven internal vertices was generated, quotienting by exact colored boundary isomorphism, and glued under all 24 dihedral boundary maps. Only even 4-connected dual closures were retained.

| Primal order | k | Disk classes | Boundary maps | Valid closures | Tested encodings | Hamiltonian | Negative | Unknown |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 1 | 1 | 24 | 24 | 24 | 24 | 0 | 0 |
| 102 | 2 | 2 | 48 | 32 | 32 | 32 | 0 | 0 |
| 104 | 3 | 14 | 336 | 192 | 192 | 192 | 0 | 0 |
| 106 | 4 | 44 | 1,056 | 568 | 568 | 568 | 0 | 0 |
| 108 | 5 | 206 | 4,944 | 2,564 | 2,564 | 2,564 | 0 | 0 |
| 110 | 6 | 778 | 18,672 | 8,802 | 8,709 | 8,709 | 0 | 0 |
| 112 | 7 | 3,198 | 76,752 | 34,490 | 34,020 | 34,020 | 0 | 0 |
| **Total** | **1-7** | **4,243** | **101,832** | **46,672** | **46,109** | **46,109** | **0** | **0** |

The difference between valid closures and tested encodings is 563 exact duplicate labeled graphs. Every tested positive has an independently checked spanning connected degree-two witness.

Primary evidence:

- `docs/UNIFORM_DUAL_SUBSTITUTION_THROUGH_ORDER112_2026-08-04.md`
- `results/2026-08-04/uniform_dual_substitution_k7_summary.json`
- `search/uniform_dual_cycle_disk_generator.py`

Hashes:

```text
generator  2caa76f131031df2c92e7877610d79ce89260bc05421594b9e96da2400766a99
summary    4596e3f3a7b7f9c760d110ee26ab3bf49f55ae0495cf7e1ad82cd24548caf19b
archive    d9a0686c6405478878ddf462f0f559db3caa745c7c4ccee0d1151ee677c5ad40
```

## 4. Corrections to previous completeness claims

The uniform generator found two omissions:

1. **Order 106:** 44 disk classes and 568 valid closures, not 43 and 556. One all-color-0 disk type and 12 valid closures were missing. All are Hamiltonian.
2. **Order 108:** 206 disk classes, not 193 in the prior completed accounting. Thirteen disk types were missing. The corrected 2,564 valid closures are all Hamiltonian.

No prior positive witness was invalidated. The corrected search strictly enlarges the tested classes.

## 5. Hamiltonicity verification

The primary solver is an exact perfect-matching-complement recursion with closed-subcycle pruning. A deliberately low branch cutoff separated easy positives from hard cases. Every cutoff case was solved independently by a binary selected-edge 2-factor MILP with iterative subtour cuts.

MILP was used only to produce positive witnesses. No infeasibility status was interpreted as proof.

Final witness audit:

```text
verified Hamiltonian encodings = 46,109
negative = 0
unknown = 0
invalid witnesses = 0
```

Each witness was checked for:

- graph-edge membership;
- exactly `n` distinct edges;
- degree two at every vertex;
- connectedness.

## 6. Consequence and strategic pivot

Within this source-and-face mechanism, any counterexample must use at least eight inserted disk vertices, corresponding to primal order at least 114, or must leave the one-face substitution framework.

The completed bound changes the strategic assessment. Blindly increasing disk order has already produced 46,672 valid closure constructions through order 112, all Hamiltonian. The primary next route is therefore not undirected order growth.

Priority sequence:

1. compute exact two-tree boundary languages of the strongest order-112 closures and rank them by relation restriction rather than solver difficulty;
2. synthesize a multi-face or multi-hole embedded composition whose topology is 4-connected before instantiation;
3. use the certified candidate-489 facial relation as a hard semantic objective;
4. retain order-114 single-face generation only as a controlled comparison or when relation-guided pruning is available;
5. escalate any nonpositive whole graph immediately to independent primal and dual proof-producing SAT.

## 7. Retired or secondary routes

The following remain valid negative search results but are not the primary route:

- 7,356/7,356 consecutive facial ternary cases positive;
- Grand Q-first v3: 71,488/71,488 natural cyclic-4-cut states positive;
- relation-first candidate-489 CEGIS: 200,000 proposals, zero selector, best compatibility 14, but iteration-capped rather than exhaustive;
- complete small six-port classes through canonical order 14: no zero map;
- 12,800 four-pole and 39,168 five-pole concrete empty-language assemblies: all nonplanar;
- 65 planar five-pole zero-language near-counterexamples: all connectivity two;
- 655 connectivity-restoring C4 repairs: all regained a compatible Hamiltonian trace.

## 8. Repository control

PR #1 remains temporarily closed and unmerged to prevent obsolete workflow fan-out. The authoritative branch and history remain intact. Temporary execution PRs #8-#10 are not to be merged.

The next repository operation should consolidate obsolete workflow triggers before reopening PR #1.
