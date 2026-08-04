# Nested Order-114 Adversarial Result

**Date:** 2026-08-04 UTC  
**Counterexample found:** No

## Construction

A completed parity-valid 12-disk was used as an outer disk. Whenever it contained an internal degree-12 vertex, that vertex was removed and replaced by a second completed 12-disk under a dihedral map of its 12-cycle link.

For outer and inner disk sizes `k1` and `k2`, the composed disk has

```text
k = k1 - 1 + k2.
```

The first new family has `k=8`, corresponding to primal order 114. It is obtained from

```text
(3,6), (4,5), (5,4), (6,3), (7,2).
```

## Relative-orientation population

| Pair | Eligible outer-vertex / inner-disk pairs |
|---|---:|
| `3+6` | 778 |
| `4+5` | 206 |
| `5+4` | 660 |
| `6+3` | 308 |
| `7+2` | 340 |
| **Total** | **2,292** |

All 24 relative inner orientations were generated:

```text
relative-orientation constructions = 55,008
```

## Fixed absolute source orientation

Using one fixed absolute identification with candidate 489's outer 12-boundary:

```text
valid 4-connected closures = 26,290
distinct labeled graph encodings = 21,702
primary exact-matching positives = 21,598
matching cutoffs = 104
independent MILP/subtour positives = 104
negative = 0
unknown = 0
```

The hard tail was not distributed uniformly. Most high-branch cases came from the unique degree-12 outer disk at `k1=3` combined with order-6 inner disks.

## All absolute orientations of the hard tail

Every one of the 104 Stage-1 hard disks was reconstructed and tested under all 24 absolute source-boundary maps.

```text
maps attempted = 2,496
valid 4-connected closures = 1,514
distinct labeled graph encodings = 1,466
primary exact-matching positives = 1,273
matching cutoffs = 193
independent MILP/subtour positives = 193
negative = 0
unknown = 0
```

This closes the complete orientation class of every disk selected by the adversarial Stage-1 cutoff criterion. It does not yet classify all absolute orientations of all 55,008 nested constructions.

## Kelmans-type test on the hardest closure

The hardest independent positive was

```text
n8_3_0_13_6_417_16_o17
```

with 114 vertices and 171 edges. Every ordered pair of distinct cofacial edges `(x,y)` was tested for a Hamiltonian cycle satisfying

```text
x included
y excluded.
```

Result:

```text
faces = 59
ordered cofacial pairs = 3,038
verified positive = 3,038
negative = 0
unknown = 0
maximum subtour rounds = 78
```

Therefore the hardest nested graph does not violate the cofacial `H^{+-}` property.

## Interpretation

Nested substitution is a geometry-preserving way to enter the first unresolved order-114 regime and to compose two exact disk mechanisms. The adversarial population remains Hamiltonian, including every orientation of every initially hard disk.

The result does not justify abandoning nested composition. It shows that solver hardness alone is not a reliable obstruction metric. The next ranking quantity must be the exact two-tree boundary language and its compatibility with the outside language of candidate 489.

## Evidence

- `results/2026-08-04/nested_order114_and_cofacial_summary.json`
- `docs/NESTED_DUAL_AND_BOUNDARY_LANGUAGE_ATTACK_2026-08-04.md`

Key hashes:

```text
stage1 tasks       c7ee66bb64e399c0ee24329c88db9211c5e31f52a25de5d08817323f23e23cfc
hard all-map tasks 80fe2a5833b2467662fbdc9d9cb2a2a08007d76b8e42c1d9d977f84870655184
cofacial scan      fe8ffed7ea8ed46daa0e0c8d0c2172893bbf77be7feaf0066e52b9149bda44e8
summary            aa62b858d59096643c8d86c01ba0b85eea17ab69adb8fbfdb2db13bb9b5ce972
```
