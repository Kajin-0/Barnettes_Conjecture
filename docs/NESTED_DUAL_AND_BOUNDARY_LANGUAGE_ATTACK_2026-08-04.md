# Nested Dual and Boundary-Language Attack

**Date:** 2026-08-04 UTC  
**Source:** candidate 489, distinguished 12-face  
**Counterexample found:** No

## 1. Motivation

The uniform single-face substitution campaign completely classified every parity-valid 12-disk with at most seven inserted vertices. All 46,109 distinct tested graph encodings were Hamiltonian. Therefore blind continuation by disk order is no longer the strongest strategy.

The next attack combines two exact ideas:

1. **Nested embedded substitution.** Replace a degree-12 internal vertex of one completed disk by a second completed 12-disk. The operation preserves planarity, the outer 12-boundary rotation, degree parity, and the sphere-triangulation interpretation. It creates structured `k >= 8` disks whose interface behavior is a genuine composition of two independently classified mechanisms.
2. **Exact boundary-language mining.** Compute and rank two-tree interface states of the completed disk library, then use the most restrictive states as synthesis objectives for nested or multi-hole constructions.

This directly targets the remaining bottleneck: not local planarity or Hamiltonian proof infrastructure, but composition of embedded boundary relations without restoring a compatible two-tree state.

## 2. Nested order-114 family

Let an outer disk contain `k1` internal vertices and an internal degree-12 vertex `v`. Remove `v`; its link is a cyclic 12-boundary. Insert an inner disk with `k2` internal vertices under one of the 24 dihedral boundary maps.

The resulting disk has

```text
k = k1 - 1 + k2
```

internal vertices. The first new order is `k=8`, corresponding to primal order 114. It is obtained from:

```text
(k1,k2) = (3,6), (4,5), (5,4), (6,3), (7,2).
```

The completed `k <= 7` library contains the following degree-12 internal vertices:

| Outer disk order k1 | Degree-12 internal vertices |
|---:|---:|
| 1 | 1 |
| 2 | 0 |
| 3 | 1 |
| 4 | 1 |
| 5 | 15 |
| 6 | 22 |
| 7 | 170 |

The order-114 nested family is therefore finite and substantially smaller than the complete unrestricted `k=8` disk class.

## 3. Staged search policy

The nested family is searched in two stages.

### Stage 1: adversarial orientation screen

- enumerate every eligible outer degree-12 vertex;
- insert every compatible inner disk under all 24 inner dihedral maps;
- test one fixed absolute outer-boundary map against candidate 489;
- retain explicit Hamiltonian witnesses and rank high-branch or independently hard cases.

### Stage 2: exact orientation expansion

For every hard or structurally exceptional Stage-1 disk:

- test all 24 absolute outer-boundary maps;
- independently solve every cutoff case with the binary 2-factor/subtour formulation;
- send any nonpositive instance to both primal selected-edge SAT and dual two-induced-tree SAT;
- require checked proof certificates before any counterexample claim.

This staging changes only prioritization. No negative conclusion is drawn from an untested orientation or a solver cutoff.

## 4. Boundary-language program

For a triangulated disk, a global Hamiltonian cycle corresponds in the dual to a binary coloring whose two color classes induce trees. The exact disk interface state must therefore record:

1. the binary colors of the 12 boundary vertices;
2. the connectivity partition induced on same-colored boundary vertices by each disk forest;
3. whether each disk color class is acyclic;
4. the number of internal components that must be joined by the outside graph.

The completed disk library will be mined for Pareto-minimal exact languages. The primary synthesis objective is not minimum raw state count alone, but minimum compatibility with the exact outside language of candidate 489.

A zero-compatible embedded state composition would be a direct counterexample candidate. A nonzero but unusually small compatibility class becomes the next target for a second nested substitution or a two-hole construction.

## 5. Acceptance standard

A final counterexample requires:

- simple cubic bipartite planar primal graph;
- vertex connectivity at least three;
- exact primal non-Hamiltonicity;
- exact absence of a dual two-induced-tree coloring;
- CaDiCaL proof traces accepted by an independent checker;
- graph6, edge list, rotation system, construction manifest, hashes, and clean reproduction.

Positive results require explicit independently validated Hamiltonian-cycle witnesses. Timeouts, branch caps, incomplete boundary languages, and provisional infeasibility are `unknown`.

## 6. Documentation invariant

Every material result from this campaign must update:

- `docs/CURRENT_STATE.md`;
- a dated file under `docs/research-log/`;
- a machine-readable result under `results/2026-08-04/`;
- the authoritative PR checkpoint;
- code and evidence hashes.
