# Complete Minimal Multi-Face Expansion Campaign

**Date:** 2026-08-04 UTC  
**Source family:** deterministic hard tail from the complete order-110/order-112 one-face dual-substitution campaigns  
**Counterexample found:** No

## Result

Every minimum nontrivial degree-4, degree-6, and degree-8 second-face replacement was applied to 157 hard one-face closures under every dihedral boundary map.

```text
hard bases = 157
raw valid closure constructions = 69,126
exact duplicate labeled graphs removed = 34,692
distinct graph encodings = 34,434
verified Hamiltonian = 34,434
negative = 0
unknown = 0
invalid witnesses = 0
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

## Construction

The base set consists of all 157 closures that reached the deterministic 5,000-branch cutoff during the complete order-110 and order-112 one-face campaigns. Solver hardness was used only for prioritization.

For each dual vertex of degree 4, 6, or 8, the smallest nontrivial parity-valid triangulated disk was inserted under every dihedral map:

| Replaced degree | Disk internal vertices | Maps | Primal order increment |
|---:|---:|---:|---:|
| 4 | 3 | 8 | 4 |
| 6 | 2 | 12 | 2 |
| 8 | 2 | 16 | 2 |

A result was retained only when the assembled triangle complex was a connected even sphere triangulation, every edge had two incident triangles, every vertex link was one cycle, no nonfacial triangle remained, and the dual was 4-connected. The derived primal graph was independently checked to be connected, cubic, and bipartite.

## Hamiltonicity verification

Four reproducible exact perfect-matching-complement branch orders were used with a 5,000-call cutoff.

| Seed | Positive | Cutoff cases |
|---:|---:|---:|
| 1 | 27,135 | 7,299 |
| 2 | 27,116 | 7,318 |
| 3 | 27,129 | 7,305 |
| 4 | 27,046 | 7,388 |

The portfolio union produced explicit Hamiltonian cycles for 34,340 graphs. Exactly 94 graphs reached the cutoff under all four branch orders.

All 94 were passed to an independent binary 2-factor MILP with iterative subtour cuts:

```text
verified positive = 94
negative = 0
unknown = 0
subtour rounds = 4 to 45
mean rounds = 22.851
aggregate solve time = 102.413 seconds
```

Every one of the 34,434 final witnesses was independently revalidated for graph-edge membership, exactly `n` distinct edges, degree two at every vertex, and connectedness. All 94 stored MILP witness hashes reproduced exactly.

MILP was used only to produce positive witnesses. No infeasibility status was interpreted as non-Hamiltonicity.

## Interpretation

This completely closes the minimum two-face extension of the hard order-110/order-112 one-face family. Adding a second local replacement substantially increases geometric diversity—most constructions occur on genuinely separate outside faces—but the entire bounded family remains Hamiltonian.

The result rules out a natural low-cost escape from the one-face order-112 bound. The next strategy must optimize the exact boundary language or deepen selected second-face disks beyond their minimum sizes rather than applying uniform minimal replacements blindly.

## Evidence

- `results/2026-08-04/minimal_multiface_complete_summary.json`
- `results/2026-08-04/minimal_multiface_structural_summary.json`
- task SHA-256 `9768d19341991b456f9493e3921d5c0167a94826d00c0b64474627117141ae1a`
- metadata SHA-256 `30b1d595c9cdb0feb0ab5d055e269aab447756e76ff97a16dbe59a1f1265b766`
