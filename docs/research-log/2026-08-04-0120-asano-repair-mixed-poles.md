# Research checkpoint: Asano repair and mixed poles

**Timestamp:** 2026-08-04 01:20 UTC  
**Counterexample found:** No

## Material results

1. Reconstructed the 26-vertex 2-connected cubic bipartite planar non-Hamiltonian graph as three edge-deleted cubes joined between two hubs. Exhaustive perfect-matching enumeration produced 324 matchings and zero Hamiltonian complements.
2. Exhausted the color-preserving three-edge permutation repair family: 7,986 graphs, including 128 3-connected Barnette graphs. Every one of the 128 has an explicit Hamiltonian cycle. They reduce to two nonisomorphic graphs, each with 48 Hamiltonian cycles.
3. Each repaired graph has nine unavoidable cofacial edge pairs. Deleting any one produces the same exact five-state four-terminal language `A = {P02,P03,P12,P13,Q01_23}`.
4. Completed the ten-vertex four-pole degree class and found four restrictive four-state relation types `B0` through `B3`.
5. Mixed `A/B` state synthesis found abstract zero-language compositions on planar 3-connected interaction skeletons:
   - four-pole `K4`: 3,072 zero relation assignments;
   - five-pole doubled-wheel: 43,008 zero relation assignments;
   - five remaining six-pole multigraph skeleton classes: zero assignments found in every class, including 92-vertex abstract candidates.
6. Complete concrete geometry checks closed the four- and five-pole mixed routes:
   - 12,800 four-pole assemblies, all nonplanar;
   - 39,168 five-pole assemblies, all nonplanar.
7. Completed the octahedral six-pole relation class exactly: 608,000,000 matching/relation combinations and zero empty products.
8. Generated 100,000 distinct exact 92-vertex abstract zero assignments on the other six-pole skeletons; all representative concrete embeddings were nonplanar. This geometry screen is not exhaustive over all terminal-labeled repaired-Asano poles.
9. Reconciled candidate-489 relation-first CEGIS workflow `30864152943`: ten jobs, 200,000 SAT topologies, no zero selector, best compatibility 14 at order 18. Every job ended at the iteration cap, so no bounded nonexistence claim is made.
10. Started complete canonical order-16 geometry-first search, workflow `30868419278`, using 64 plantri residues.

## Strategic pivot

The limiting resource is no longer discovery of an empty finite-state product. Such products are abundant. The limiting resource is a planar terminal routing that preserves the empty language while producing a 3-connected cubic bipartite graph.

Primary route:

```text
canonical planar six-port generation
    -> exact 75-state language
    -> composition with candidate 489's exact 26-state pole
    -> immediate whole-graph SAT/DRAT proof for any Barnette zero
```

Abstract mixed-pole multiplication remains a relation laboratory, not the primary construction engine.

## Evidence

- `docs/ASANO_REPAIR_MIXED_POLES_2026-08-04.md`
- `results/2026-08-04/asano_repair_mixed_pole_summary.json`
- `.github/workflows/canonical-six-port-order16.yml`
