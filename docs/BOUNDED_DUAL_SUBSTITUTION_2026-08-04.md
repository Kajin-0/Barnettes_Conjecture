# Bounded Dual Substitution Breakthrough

**Date:** 2026-08-04 UTC  
**Source:** candidate 489, distinguished 12-face  
**Counterexample found:** No

## 1. Result

The degree-12 vertex corresponding to candidate 489's certified obstructed face was removed from the 52-vertex even dual triangulation. Parity-valid triangulated 12-disks were inserted under every dihedral boundary map.

The substitution class is now completely classified for at most four inserted disk vertices, corresponding to primal orders 100, 102, 104, and 106.

Two major color classes at five inserted vertices, corresponding to primal order 108, are also complete.

| Scope | Disk types | Boundary maps | Even 4-connected closures | Hamiltonian | Negative | Unknown |
|---|---:|---:|---:|---:|---:|---:|
| Complete `k <= 4` | 60 | 1,440 | 804 | 804 | 0 | 0 |
| `k=5`, colors `(5,0,0)` | 10 | 240 | 49 | 49 | 0 | 0 |
| `k=5`, colors `(4,1,0)` | 115 | 2,760 | 1,333 | 1,333 | 0 | 0 |
| **Completed total** | **185** | **4,440** | **2,186** | **2,186** | **0** | **0** |

Every positive has an explicit spanning connected degree-two edge witness. All stored witnesses in the complete `k <= 4` class were independently revalidated.

## 2. Structural reduction

Adding the removed dual vertex back to a candidate disk produces an even plane triangulation. Such a triangulation has a proper three-coloring. Fix the removed vertex as color 0; the 12 boundary vertices alternate colors 1 and 2.

For a disk with `k` internal vertices:

```text
internal triangular faces = 10 + 2k
E01 = 5 + k
E02 = 5 + k
E12 = 11 + k
```

Every internal face is rainbow. Neighbor colors alternate around every vertex, so internal degrees are even and boundary disk degrees are odd.

These equations sharply restrict the possible internal color counts and degrees. Through `k=4`, all possibilities reduce to finite polygonal constructions:

- noncrossing bichromatic chord dissections with one color-0 center per cell;
- degree-4, degree-6, or degree-8 boundary-colored vertices with alternating center/boundary neighborhoods;
- independently triangulated residual rainbow polygons.

This eliminates the need to enumerate parity-invalid planar disks.

## 3. Complete low-order classifications

### `k=1`, primal order 100

A complete neighbor-set and pocket-triangulation enumeration considered 89,402 raw constructions. The parity filter leaves one dihedral class: the original 12-wheel disk. All 24 maps reconstruct candidate 489.

### `k=2`, primal order 102

No parity-valid disk contains the edge between the two internal vertices. Every valid disk is separated by one boundary chord into two one-center pieces.

```text
disk types = 2
maps = 48
4-connected closures = 32
nonisomorphic reduced primal graphs = 16
Hamiltonian = 32
```

### `k=3`, primal order 104

Two color distributions are possible:

```text
three color-0 vertices
two color-0 vertices plus one boundary-colored vertex
```

```text
disk types = 14
maps = 336
4-connected closures = 192
Hamiltonian = 192
```

All consecutive three-edge paths on the two genuinely new faces of each reduced graph were also tested. All 224 cases had explicit compatible Hamiltonian cycles.

### `k=4`, primal order 106

All three feasible color distributions were completed:

| Distribution | Disk types | Maps | 4-connected | Hamiltonian |
|---|---:|---:|---:|---:|
| `(4,0,0)` | 17 | 408 | 120 | 120 |
| `(3,1,0)` | 23 | 552 | 388 | 388 |
| `(2,1,1)` | 3 | 72 | 48 | 48 |

For the final distribution, both nonzero-color vertices are forced to degree four and adjacent to both color-0 vertices. A valid completion exists only when the two nonzero-color vertices are adjacent.

## 4. Order-108 progress

### Five color-0 vertices

The complete class consists of four noncrossing bichromatic chords separating the boundary into five even cells, each filled by a center-star.

```text
disk types = 10
maps = 240
4-connected closures = 49
Hamiltonian = 49
```

### Four color-0 vertices plus one boundary-colored vertex

The boundary-colored vertex is forced to degree 4, 6, or 8. Remaining color-0 centers are distributed among residual polygons and completed by exact noncrossing center-star dissections.

```text
disk types = 115
maps = 2,760
4-connected closures = 1,333
Hamiltonian = 1,333
```

The compiled exact perfect-matching-complement solver found 900 witnesses. One map, `84_1_0`, exceeded 100 million branches. An independent mixed-integer 2-factor formulation with lazy subtour cuts found and validated a Hamiltonian cycle after 11 rounds in 0.074 seconds. The same independent formulation produced witnesses for the remaining 432 maps.

MILP was used only to generate positive witnesses. No infeasibility result was interpreted as proof.

## 5. Remaining order-108 classes

The unclassified internal color distributions are:

```text
(3,1,1)
(3,2,0)
(2,2,1)
```

The attempted `(3,2,0)` forced-core enumeration is larger because different degree-four quadrilateral neighborhoods can share color-0 centers and leave multiple residual embedding regions. It requires a geometry-canonical core generator rather than relying on one embedding returned by a generic planarity routine.

## 6. Interpretation

This is a significant bounded construction result, not a Barnette counterexample.

The dual embedded-substitution framework successfully resolves the geometric defect that invalidated the earlier abstract mixed-pole products. It generated 2,186 reduced 4-connected candidate closures through completed classes, all of which were exactly Hamiltonian.

The strongest next target is not blind growth in disk order. It is a canonical embedding-aware generator for the three remaining `k=5` color distributions, prioritizing overlapping degree-four quadrilateral cores. Those are the first unclassified local structures at primal order 108.

## 7. Evidence

Machine-readable summaries:

- `results/2026-08-04/bounded_dual_substitution_summary.json`
- `results/2026-08-04/order108_partial_dual_substitution_summary.json`

Local evidence archive SHA-256:

```text
f64a5ed2e6b736559a71c6e6cce7fb5f69a6a0827e64c8f239e8927f00edd465
```

Clean plantri/Actions reproduction remains pending because the repository Actions queue was saturated by obsolete workflows. No queued status is treated as mathematical evidence.
