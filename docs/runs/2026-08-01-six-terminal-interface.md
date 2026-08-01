# Six-Terminal Cyclic-Cut Interface Campaign

**Date:** 2026-08-01  
**Status:** active pilot  
**Counterexample found at start:** no

## Motivation

Every tested natural cyclic-4-cut side in the leading order-92 graph was maximally flexible. A four-terminal marginal can miss correlations that persist across a larger separator.

A simple separating 6-cycle in the planar dual corresponds to a cyclic 6-edge cut in the cubic primal graph. Each side is a planar six-terminal patch.

## Boundary states

Let the terminals be ordered cyclically as `0,1,2,3,4,5`. A Hamiltonian cycle in a completed graph may use 2, 4, or 6 cut edges. Inside one patch this induces respectively:

- one spanning path with two terminal endpoints;
- two vertex-disjoint spanning paths with four terminal endpoints;
- three vertex-disjoint spanning paths with six terminal endpoints.

The endpoints must be paired noncrossingly. Across all endpoint subsets there are 50 nominal planar states before bipartite parity filtering.

## Matching-complement reduction

For a boundary state, every internal patch vertex has selected degree two. A terminal has selected internal degree one when its cut edge is used and degree two otherwise.

The omitted internal edges therefore form a matching that:

- saturates every internal vertex;
- saturates every terminal whose cut edge is used;
- leaves all other terminals exposed.

For a chosen exposed-terminal set `E`, such a matching is a perfect matching of `P - E`. Its complement is a valid state exactly when it contains no cycle component and its path components induce the requested terminal pairing.

This gives a fast positive-witness sampler. Sampling misses are heuristic only.

## Compatibility

Two patch states are compatible under a boundary map when:

1. they use the same mapped terminal subset; and
2. the union of their terminal pairings is one cycle rather than several disjoint cycles.

A nonempty compatible-state set is a robust positive result. A zero observed compatibility from sampled signatures is provisional and must be followed by exact signature completion.

## Pilot scope

- regenerate the established 2,400-graph canonical order-92 sample;
- retain the same eight theorem-escaping matching-fragmentation leaders;
- enumerate all natural cyclic 6-edge cuts in all eight leaders;
- screen every cut side with 64 matching-complement trials;
- deepen the 100 sparsest signatures with 4,096 trials;
- compare all distinct observed signature groups under all bipartition-preserving dihedral maps;
- publish zero-compatibility candidates and the minimum positive compatibility.

## Validation policy

- sampled states are positive heuristic witnesses and are independently checked for selected degree, component count, endpoint set, and terminal pairing;
- zero sampling hits are not negative evidence;
- zero observed patch-map compatibility is provisional;
- any retained incompatible candidate requires exact state decisions and proof-producing SAT for every missing state needed by the incompatibility argument;
- timeouts and failures remain unknown.

## Escalation

If an apparent incompatible six-terminal pair survives deep sampling:

1. complete both signatures exactly;
2. proof-check every required negative state;
3. glue the patches and validate cubicity, bipartiteness, planarity, simplicity, and 3-connectivity;
4. encode whole-graph Hamiltonicity and require an independently checked UNSAT proof.
