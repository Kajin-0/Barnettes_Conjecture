# Dual Face-Substitution Attack

**Date:** 2026-08-04 UTC  
**Counterexample found:** No

## Strategic conclusion

The strongest next analytical route is to move the obstruction search into the planar dual.

For a cubic plane graph, a Hamiltonian cycle separates the faces into two classes. A primal edge is in the cycle exactly when its two incident dual vertices have different colors. For a Hamiltonian cycle, each color class induces a tree in the dual. Thus Barnette's conjecture is equivalent to the statement that every simple even plane triangulation can be partitioned into two induced trees.

This representation directly addresses the current bottleneck:

```text
abstract empty boundary language exists
but every tested terminal realization is nonplanar.
```

In the dual, the cyclic embedding and the boundary rotation are part of the triangulation itself rather than metadata added after relation synthesis.

## Why this outranks another unrestricted patch search

1. Candidate 489's dual is a simple even plane triangulation with 52 vertices and vertex connectivity 4.
2. The certified principal obstruction on face 2 becomes three color-parity constraints around one degree-12 dual vertex:
   - `(14,18)` bichromatic;
   - `(10,17)` monochromatic;
   - `(5,11)` monochromatic.
3. Replacing that dual vertex by an even triangulated disk is equivalent to replacing the entire primal 12-face by an embedded 12-port cubic bipartite patch. Planarity is automatic.
4. A recent theorem proves Hamiltonicity when every primal face has size at most 8. Therefore a counterexample must contain a 10+-face, and local neighborhoods of large faces are the correct search domain.
5. The 2025-2026 face-size proof itself uses exact embedded graph substitutions and exhaustive open-end Hamiltonian-state checking. This strongly supports a substitution-language search rather than nonembedded pole multiplication.

## Phase 0: independent dual proof encoding

`search/dual_face_cut_obstruction.py` implements an independent Hamiltonicity formulation.

Variables:

- one color bit per dual vertex;
- one selected-edge bit per primal edge;
- selected edge iff its incident dual faces have different colors.

Constraints:

- exactly two selected edges at every primal vertex;
- requested include/exclude edge conditions;
- lazy globally valid two-edge cut clauses until the selected 2-factor is connected.

A positive result must independently validate:

- the selected primal edges form a Hamiltonian cycle;
- the edge set equals the dual color cut;
- each dual color class induces a tree;
- all requested edge conditions hold.

A negative is certified only after CaDiCaL produces textual DRAT and `drat-trim` accepts it.

The campaign tests all eight patterns on the principal triple and independently re-proves all six existing certified obstructions.

Workflow:

```text
.github/workflows/dual-face-cut-obstruction.yml
```

## Phase 1: prime-implicate mining on mandatory large faces

`search/dual_face_implicate_scan.py` scans every partial boundary assignment of widths one, two, and three on every candidate-489 face of size at least 10.

Candidate 489 has large-face sizes:

```text
12, 30, 30.
```

For each face, the scanner:

1. classifies every include/exclude pattern of widths 1-3 using an incremental exact SAT oracle;
2. validates every positive with a Hamiltonian-cycle witness;
3. extracts prime forbidden patterns not implied by a smaller forbidden assignment;
4. ranks ternary clauses by cyclic span and gap signature;
5. escalates the 32 most compact prime ternary clauses to independent CaDiCaL/DRAT proofs.

Workflow:

```text
.github/workflows/dual-face-implicate-scan.yml
```

## Phase 2: rotation-aware substitution synthesis

The output of Phase 1 will define a small Boolean obstruction kernel on each large face. The next generator will enumerate embedded cubic bipartite disk substitutions, preserving the cyclic order of open ends, and compute their exact open-end path-cover language.

The synthesis objective is not merely an empty abstract product. It is:

```text
embedded patch language
    subset of a proof-certified forbidden large-face boundary relation
and
resulting closed graph is simple, cubic, bipartite, planar, and 3-connected.
```

The most promising special case is replacement of candidate 489's degree-12 dual vertex by a simple even triangulated disk whose every valid two-tree boundary state projects to the principal forbidden parity pattern.

## Acceptance standard

A full breakthrough requires:

1. a concrete graph6 and embedded construction;
2. independent Barnette-predicate checks;
3. whole-graph non-Hamiltonicity in the primal edge encoding;
4. whole-graph non-two-tree-colorability in the dual face-cut encoding;
5. independently checked proof certificates for both formulations;
6. clean workflow reproduction with complete hashes and provenance.

## Current status

The dual proof engine and large-face scanner are committed. No result from their Actions campaigns is interpreted until the artifacts are complete and independently checked.
