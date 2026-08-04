# Boundary-Directed Degree-4 and Degree-6 Expansion

**Date:** 2026-08-04 UTC  
**Counterexample found:** No

## 1. Purpose

The complete one-face search through order 112 and the complete minimum second-face campaign showed that graph order and generic solver hardness are poor construction objectives. This campaign instead used the exact 118-mask original-seam language of `421_32_6` to rank second faces and then deepened only the strongest local interfaces.

## 2. Joint-seam correction

An initial two-seam experiment constrained the radial dual edges incident with the face vertex being replaced. That is not the boundary opened by a vertex substitution.

Removing a dual vertex exposes its neighbor link cycle. Therefore the correct second seam consists of edges between consecutive vertices in that link cycle.

The radial-edge relation was retracted before it was used for synthesis. The corrected exact joint relations use link-cycle edges.

### Correct degree-4 joint relation

For relabeled dual vertex 45:

```text
original seam masks = 118
second-seam masks per query = 16
exact positive pairs = 780
exact negative pairs = 1,108
unknown = 0
```

Every original seam mask has a positive pair. Depending on the original mask, the second seam has 2, 6, or 10 compatible colorings. The union is

```text
1, 2, 4, 5, 7, 8, 10, 11, 13, 14.
```

### Correct degree-6 joint relation

For relabeled dual vertex 40:

```text
original seam masks = 118
second-seam masks per query = 64
exact positive pairs = 1,020
exact negative pairs = 6,532
unknown = 0
```

Each original mask has 2, 6, or 16 compatible degree-6 seam colorings.

## 3. Degree-4 interface rigidity

Every parity-valid degree-4 disk generated for internal orders `k=3,...,8` was classified by exact binary forest-partition language.

```text
disk types = 65
exact signatures per disk = 6
languages identical for all 65 disks = true
```

The common complement-normalized signatures are:

```text
10:0,-1,0,-1:-1,1,-1,3
10:0,-1,2,-1:-1,1,-1,1
14:0,-1,-1,-1:-1,1,1,1
2:0,-1,0,0:-1,1,-1,-1
4:0,0,-1,0:-1,-1,2,-1
8:0,0,0,-1:-1,-1,-1,3
```

Thus increasing the degree-4 disk order through `k=8` did not change the interface language at all. This gives a structural explanation for the persistent positive closures and strongly deprioritizes further undirected degree-4 growth.

## 4. Targeted degree-4 closures

| Disk order | Disk types | Attempts | Valid closures | Tested encodings | Hamiltonian |
|---|---:|---:|---:|---:|---:|
| `k=5,6,7` | 27 | 216 | 128 | 120 | 120 |
| `k=8` | 36 | 288 | 80 | 80 | 80 |
| **Total** | **63** | **504** | **208** | **200** | **200** |

The four-seed exact portfolio resolved 197 graphs. Three cutoff cases were solved positively by independent 2-factor MILP/subtour search. Every witness was revalidated.

## 5. Targeted degree-6 closures

| Disk order | Disk types | Attempts | Valid closures | Tested encodings | Hamiltonian |
|---|---:|---:|---:|---:|---:|
| `k=5` | 9 | 108 | 72 | 60 | 60 |
| `k=6,7` | 91 | 1,092 | 548 | 524 | 524 |
| **Total** | **100** | **1,200** | **620** | **584** | **584** |

The four exact branch orders produced a positive witness for every graph; no MILP tail remained.

## 6. Aggregate result

```text
tested graph encodings = 784
verified Hamiltonian = 784
negative = 0
unknown = 0
invalid witnesses = 0
```

## 7. Strategic consequence

The degree-4 route is semantically rigid through all generated orders. Degree-6 languages vary, but the complete targeted class through `k=7` remains positive.

The next active interface is degree 8:

- the first twelve degree-8 disks already have language sizes from 46 to 83 states;
- their common exact signature kernel is smaller than for degree 6;
- several degree-8 faces lie on or near the original seam, creating stronger two-hole correlations.

The next experiment will rank degree-8 faces using corrected link-seam relations and synthesize from the smallest degree-8 disk language rather than increasing order uniformly.

## Evidence

- `results/2026-08-04/boundary_directed_degree4_degree6_summary.json`
- exact joint relation hashes:
  - degree 4: `e01938e9b791de2eb51670efdd2cc6b7c559fead22e310ba4e92b6aa2836a650`
  - degree 6: `b61d843d330aca435967cb959db1cfb4ecc6b9ae3fade4f638692cb8d3cc4d6e`
- aggregate summary SHA-256 `1d5ceecba94e406cd3e043d59878fe44ead0976c56726dfcd38129fe03f67d5a`
