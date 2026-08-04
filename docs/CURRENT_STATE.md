# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative research PR:** PR #1, temporarily closed and unmerged  
**Snapshot timestamp:** 2026-08-04 19:20 UTC  
**Counterexample found:** No

This is the canonical mutable snapshot. Every material result must be committed as code or a reproducible specification, machine-readable evidence, a dated log, and an updated interpretation. Timeouts, branch cutoffs, sampled misses, provisional infeasibility, malformed cases, and queued jobs are always `unknown`.

## 1. Acceptance standard

A Barnette counterexample requires independent verification of simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three; exact primal non-Hamiltonicity; exact failure of the dual two-induced-tree formulation; checked proof certificates; and complete graph/construction provenance.

No solver infeasibility status alone is accepted as a counterexample.

## 2. Certified source

Candidate 489 is a 100-vertex simple cubic bipartite planar 3-connected graph. Its distinguished 12-face has cyclic order

```text
5, 10, 17, 25, 35, 48, 40, 30, 22, 14, 18, 11
```

and proof-certified obstruction

```text
(14,18) included
(10,17) excluded
(5,11) excluded.
```

Six source cases have CaDiCaL DRAT proofs accepted by `drat-trim`. The dual is an even 4-connected plane triangulation with 52 vertices and 150 edges.

Primary source evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- workflow `30750008325`
- artifact `8834131003`
- artifact SHA-256 `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`

## 3. Complete one-face substitution bound through order 112

The uniform link-cycle generator exhausts every parity-valid triangulated 12-disk with one through seven internal vertices.

```text
disk classes = 4,243
boundary maps = 101,832
valid 4-connected closure constructions = 46,672
tested graph encodings = 46,109
Hamiltonian = 46,109
negative = 0
unknown = 0
invalid witnesses = 0
```

Therefore any counterexample in the candidate-489 one-face substitution family needs at least eight inserted disk vertices, corresponding to primal order at least 114.

Evidence:

- `docs/UNIFORM_DUAL_SUBSTITUTION_THROUGH_ORDER112_2026-08-04.md`
- `results/2026-08-04/uniform_dual_substitution_k7_summary.json`
- `search/uniform_dual_cycle_disk_generator.py`

## 4. Complete minimum two-face extension

Every minimum nontrivial degree-4, degree-6, and degree-8 second-face replacement was applied to all 157 deterministic hard-tail order-110/order-112 closures under every dihedral map.

```text
raw valid constructions = 69,126
exact duplicate labeled graphs removed = 34,692
distinct graph encodings = 34,434
Hamiltonian = 34,434
negative = 0
unknown = 0
invalid witnesses = 0
```

The four-seed exact matching portfolio found 34,340 witnesses. The remaining 94 cases were all solved positively by an independent 2-factor MILP/subtour formulation, and every witness was revalidated.

Evidence:

- `docs/MINIMAL_MULTIFACE_COMPLETE_2026-08-04.md`
- `results/2026-08-04/minimal_multiface_complete_summary.json`
- `results/2026-08-04/minimal_multiface_structural_summary.json`

## 5. Signature-directed deeper two-face result

The exact local two-tree forest signature ranked disk class `421_32` as the smallest language among the hard-base disks:

```text
valid local colorings = 1,304
boundary color masks = 309
exact forest signatures = 380
```

Deepening its selected closure `421_32_6` through every degree-4/6/8 second-face disk with at most four internal vertices produced:

```text
distinct graphs = 1,055
orders = 114, 116, 118
Hamiltonian = 1,055
negative = 0
unknown = 0
```

The single graph unresolved by four exact branch orders was solved positively by independent MILP in 16 subtour rounds.

Evidence:

- `results/2026-08-04/signature_leader_deep_complete_summary.json`
- `docs/research-log/2026-08-04-1845-signature-leader-deep.md`

## 6. Exact original-seam boundary language

A complement-normalized 12-bit dual boundary coloring fixes the twelve primal seam-edge statuses. Exhaustive perfect-matching-complement recursion classified all 2,048 masks for three leading closures.

| Base | Positive | Exact negative | Unknown |
|---|---:|---:|---:|
| `421_32_6` | **118** | 1,930 | 0 |
| `511_530_1` | 127 | 1,921 | 0 |
| `511_552_6` | 127 | 1,921 | 0 |

A corrected independent dual-color/XOR MILP agrees mask-for-mask with the recursion.

An earlier 112-mask count is retracted. Its cause was a noncontiguous dual vertex labeling that made one color variable overlap the first edge variable. The contaminated scans were deleted and recomputed. This defect was confined to the newly written mask MILP and does not affect prior primal Hamiltonicity results.

Evidence:

- `docs/EXACT_SEAM_LANGUAGE_PILOT_2026-08-04.md`
- `results/2026-08-04/exact_seam_language_pilot_summary.json`

## 7. Strongest active strategy

Blind one-hole order growth and uniform minimal second-face replacement are now secondary. The active semantic target is the exact 118-mask language of `421_32_6`.

Execution sequence:

1. choose a second face by minimizing an observed and then exact joint relation with the original 12-seam;
2. compute the exact joint boundary language between the original seam and that face;
3. enumerate parity-valid embedded replacement disks for the selected face;
4. compose the replacement language against the exact joint relation;
5. require empty composition, an even sphere triangulation, and dual 4-connectivity simultaneously;
6. send every whole-graph nonpositive result to independent primal and dual proof-producing SAT.

The desired object is no longer merely a hard graph. It is a second embedded gadget that eliminates all 118 surviving seam colorings.

## 8. Secondary and retired findings

Still-valid negative results include:

- 7,356/7,356 consecutive facial ternary cases positive;
- Grand Q-first v3: 71,488/71,488 natural cut-side states positive;
- complete small six-port classes through canonical order 14: no empty composition;
- 12,800 four-pole and 39,168 five-pole abstract-zero concrete assemblies: all nonplanar;
- 65 planar five-pole near-counterexamples: all vertex connectivity two;
- 655 connectivity repairs: all regained compatible Hamiltonian traces.

PR #1 remains temporarily closed to prevent obsolete workflow fan-out. The branch remains authoritative.
