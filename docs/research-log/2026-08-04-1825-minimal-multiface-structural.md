# Minimal multi-face structural campaign

**Timestamp:** 2026-08-04 18:25 UTC  
**Counterexample found:** No  
**Status:** structural generation complete; Hamiltonicity portfolio active

The complete one-face dual-substitution class through primal order 112 was positive. The next campaign therefore applies a second embedded replacement to every deterministic hard-tail graph from the order-110 and order-112 campaigns.

## Base family

The base set contains 157 graphs:

- one order-110 graph;
- 156 order-112 graphs;
- each had reached the deterministic 5,000-branch cutoff before being resolved positively by the independent formulation.

Solver hardness is used only for prioritization. It is not interpreted as evidence of non-Hamiltonicity.

## Complete minimum second-face replacements

For every base dual vertex of degree 4, 6, or 8, the minimum nontrivial parity-valid disk was inserted under every dihedral boundary map.

| Replaced dual degree | Disk internal vertices | Disk classes | Maps per face | Primal order increment |
|---:|---:|---:|---:|---:|
| 4 | 3 | 1 | 8 | 4 |
| 6 | 2 | 1 | 12 | 2 |
| 8 | 2 | 1 | 16 | 2 |

Nested replacements, seam-adjacent replacements, and replacements on genuinely distinct outside faces are all retained.

A closure is accepted only when its triangle complex is a connected sphere with Euler characteristic two, every edge lies in two triangles, every vertex link is one cycle, every dual degree is even, no nonfacial triangle exists, and the derived primal graph is connected, cubic, and bipartite.

## Structural result

```text
hard bases = 157
raw valid closure constructions = 69,126
exact duplicate labeled graphs removed = 34,692
distinct graph encodings entering Hamiltonicity = 34,434
```

By primal order:

```text
order 112 = 53
order 114 = 9,379
order 116 = 25,002
```

By replacement location:

```text
outside face = 24,655
seam-adjacent = 6,034
nested = 3,745
```

By replaced dual degree:

```text
degree 4 = 25,162
degree 6 = 5,385
degree 8 = 3,887
```

## First adversarial tail

The deterministic matcher reached its cutoff on

```text
511_42_21__v54_B8_nested_m2
```

An independent binary 2-factor MILP with iterative subtour cuts found and validated a Hamiltonian cycle in 40 rounds and 0.665 seconds.

Witness SHA-256:

```text
8509ace2da6739f0835e5eceddc2e6c5951b474becc74f1fc284d94cbae70166
```

This was a solver-order artifact, not a negative result.

## Active classification

A reproducible seeded exact matching portfolio is running over all 34,434 graphs. Every case not resolved positively by the portfolio will be sent to the independent subtour formulation. No cutoff, timeout, or MILP infeasibility status will be interpreted as non-Hamiltonicity.

Evidence:

- `results/2026-08-04/minimal_multiface_structural_summary.json`
- task SHA-256 `9768d19341991b456f9493e3921d5c0167a94826d00c0b64474627117141ae1a`
- metadata SHA-256 `30b1d595c9cdb0feb0ab5d055e269aab447756e76ff97a16dbe59a1f1265b766`
