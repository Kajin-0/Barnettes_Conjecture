# Face-Internal Ternary Amplifier: Direct Route to a Barnette Counterexample

**Date:** 2026-08-03  
**Status:** strategic direction; no counterexample yet  
**Primary objective:** convert the existing proof-certified cofacial `H^{+--}` obstruction directly into a closed non-Hamiltonian Barnette graph.

## Decision

The strongest next analytical direction is **face-internal ternary amplification**.

Do not make the remaining 64 connectivity-two five-pole near-counterexamples the primary program. They remain a fallback library, but the source-2 campaign showed that repairing a two-vertex separator after assembly can restore the forbidden Hamiltonian trace even when every Barnette-class predicate is repaired.

Instead, retain the original 3-connected order-100 Barnette graph and insert a planar bipartite cubic selector network inside the face containing the certified ternary obstruction. The selector must force every Hamiltonian cycle of the expanded graph to restrict to the already certified impossible trace in the source graph.

The target is therefore a graph `G*` with:

1. `G*` simple, cubic, bipartite, planar, and 3-connected;
2. the original order-100 graph embedded as the outside component of one face replacement;
3. every Hamiltonian cycle of `G*`, if one existed, inducing a Hamiltonian cycle of the source graph that contains `x` and avoids both `y` and `z`;
4. a checked whole-graph UNSAT proof for Hamiltonicity.

If these conditions hold, `G*` itself is the counterexample. No later connectivity repair and no separate binary `H^{+-}` amplification are required.

## Certified source obstruction

The source is canonical order-100 candidate 489. It is independently verified to be simple, cubic, bipartite, planar, and 3-connected.

On face 2, with cyclic boundary

```text
5, 10, 17, 25, 35, 48, 40, 30, 22, 14, 18, 11
```

the principal certified triple is

```text
x = (14,18)
y = (10,17)
z = (5,11)
```

No Hamiltonian cycle contains `x` while avoiding both `y` and `z`. CaDiCaL produced a textual DRAT proof and `drat-trim` accepted it. Five additional cofacial triples in the same graph are also proof-certified.

Evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- `.github/workflows/face-three-edge-proof.yml`
- workflow run `30750008325`
- artifact `8834131003`
- artifact SHA-256 `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`

## Why this route is theorem-complete

Kelmans proved that Barnette's conjecture is equivalent to the cofacial `H^{+-}` property. Hertel subsequently gave another equivalent strengthening: for every three-edge path on a face, there must be a Hamiltonian cycle containing the middle edge and avoiding the two outer edges.

The historical computational note by Aldred, Brinkmann, and McKay explicitly suggested that a condition involving three or more edges could be the practical route to a counterexample because it should fail at smaller order than the binary condition.

The repository has now found a proof-certified three-edge failure. The missing step is not another statistical search. It is an explicit planar amplifier that converts the nonconsecutive cofacial relation into a closed contradiction while preserving 3-connectivity.

## Formal synthesis problem

Let `H` be the source graph and `F` the designated face. Let `T` be an ordered set of attachment terminals created by subdividing selected edges of `F` in bipartition-preserving pairs. Let `L_H(T)` be the exact Hamiltonian boundary language of the outside graph after the interior of `F` is opened, and let `L_P(T)` be the exact boundary language of a candidate face patch `P`.

Search for `P` such that

```text
L_H(T) compose L_P(T) = empty
```

while the glued graph

```text
G* = H[F <- P]
```

is simple, cubic, bipartite, planar, and 3-connected.

The empty composition must be exact. Positive underapproximations cannot support the claim.

A stronger guided condition is preferred when available:

```text
Every globally compatible trace forces x=1, y=0, z=0 in H.
```

The existing DRAT certificate for the source obstruction then explains the contradiction locally, while a new whole-graph DRAT proof certifies the final graph independently.

## Phase 0: consecutive-triple scan

Before synthesizing a patch, run the cheapest theorem-complete test:

1. enumerate every three-consecutive-edge facial path in candidate 489;
2. test the condition `middle included, outer two excluded`;
3. expand to all existing order-96 and order-100 leaders;
4. proof-certify every nonpositive result.

A certified consecutive triple immediately supplies the exact local failure used in Hertel's equivalent formulation and should be passed through the explicit face construction from that proof to obtain a closed counterexample candidate.

This scan must be exhaustive over the retained parent graphs, not heuristic.

## Phase 1: exact source-face trace language

Compute the exact Hamiltonian trace language on the 12-edge boundary of face 2.

For each feasible boundary pattern, retain:

- selected face edges;
- complementary perfect matching;
- connected Hamiltonian witness;
- induced terminal pairing after the face is opened;
- canonical state identifier.

For each infeasible state needed by synthesis, use proof-producing SAT and retain the checked proof.

The first projection should record all `2^12` edge-inclusion masks. A refined language should additionally distinguish connectivity pairings of boundary path segments, since identical masks can compose differently.

## Phase 2: candidate patch generation

Generate planar bipartite subcubic patches in increasing internal order.

Required patch constraints:

- terminals appear on the outer face in the prescribed cyclic order;
- terminal colors match the source subdivisions;
- internal vertices have degree three;
- terminals have the exact residual degree required by gluing;
- no loops or parallel edges after gluing;
- every internal face has even length;
- the glued graph is 3-connected.

Use two complementary generators:

### A. Constructive patch grammar

Generate patches through operations that preserve planarity and bipartiteness:

- paired edge subdivision;
- facial `C4` insertion;
- quadrangulated ladder insertion;
- two-terminal and four-terminal brace substitution;
- face splitting with parity-preserving paths.

### B. SAT/CP topology synthesis

For a fixed number of internal vertices, solve directly for:

- adjacency variables;
- bipartition colors;
- outer-face rotation;
- degree constraints;
- connectivity constraints;
- forbidden boundary-language compatibility.

Use symmetry breaking under dihedral automorphisms of the source face and terminal-equivalent patch relabelings.

## Phase 3: counterexample-guided relation synthesis

Use CEGIS rather than enumerate complete languages for every patch.

1. Propose a patch satisfying graph-class constraints.
2. Ask for a Hamiltonian cycle in the glued graph.
3. If SAT, extract its source and patch boundary trace.
4. Add a blocking constraint excluding that trace family.
5. Repeat until either:
   - the topology becomes impossible; or
   - the glued graph is UNSAT for Hamiltonicity.
6. For an UNSAT candidate, rebuild the final CNF independently and generate a checked DRAT/LRAT proof.

This turns each Hamiltonian cycle into a useful counterexample to the current patch design instead of restarting the search.

## Phase 4: connectivity-first acceptance

The source graph is already 3-connected. A face patch should attach through at least three independently distributed boundary regions. Nevertheless, 3-connectivity must be checked exactly after every gluing.

Reject a topology before Hamiltonian analysis if it has:

- a cut vertex;
- a two-vertex separator;
- an attachment pair through which all patch-to-source paths pass;
- a trivial tight-cut decomposition that recreates the five-pole failure mode.

Prefer patches whose attachment incidence graph is internally 3-connected relative to the boundary.

Also test whether the final graph is a cubic planar brace. Barnette's conjecture reduces to cubic planar braces, so a non-brace candidate may contain avoidable decomposition structure even when it is formally 3-connected.

## Phase 5: complete proof package

A result is not a counterexample until the repository contains all of the following:

1. canonical graph6 encoding and sorted edge list;
2. planar rotation system and designated face data;
3. independent checks of simplicity, cubicity, bipartiteness, planarity, and 3-connectivity;
4. construction manifest linking every source edge, subdivision, patch vertex, and glue edge;
5. SHA-256 hashes of every source and generated artifact;
6. a whole-graph Hamiltonian CNF produced by an independently reviewed encoder;
7. CaDiCaL UNSAT output with textual DRAT or LRAT proof;
8. successful independent proof checking;
9. a second independent non-Hamiltonicity formulation or transparent exact decomposition check;
10. a clean GitHub Actions reproduction from committed inputs.

Only after all ten gates pass may the repository state `counterexample_found: true`.

## Search order

Use this order:

1. consecutive-triple scan on candidate 489;
2. consecutive-triple scan on existing retained order-96/order-100 parents;
3. exact 12-edge face language for candidate 489;
4. face patches with 4, 6, 8, ... internal vertices;
5. CEGIS synthesis through 24 internal vertices;
6. relation-first SAT synthesis with larger patches;
7. only then return to source-57 state-selective connectivity repair.

## Fallback: 3-connected multi-copy relation synthesis

If no face patch exists within the bounded campaign, use the exact 26-state six-pole languages to synthesize a multi-copy composition whose skeleton is 3-connected before instantiation.

This fallback differs from the previous `AABCC` search:

- 3-connectivity is a hard synthesis constraint, not repaired afterward;
- target-language emptiness and topology are solved jointly;
- the composition skeleton must have no two-vertex separator;
- every surviving assembly goes directly to whole-graph proof-producing SAT.

## Why the previous primary direction is demoted

The completed source-2 family produced 655 simple cubic bipartite planar 3-connected graphs, but all 655 regained the forbidden Hamiltonian trace. Generic separator-crossing `C4` repair is therefore too permissive.

The remaining one-closure source-57 family is still valuable, but it begins from an assembly that has already lost 3-connectivity. The face-amplifier route begins from a certified 3-connected graph and modifies one face through multiple attachments, which is structurally more favorable.

## Grand Q-first v3 closure

The completed broad campaign further supports this pivot:

| Order | Parents | Patch sides | Q states | Positive | Missing | Unknown |
|---|---:|---:|---:|---:|---:|---:|
| 96 | 12 | 16,852 | 33,704 | 33,704 | 0 | 0 |
| 100 | 12 | 18,892 | 37,784 | 37,784 | 0 | 0 |
| **Total** | **24** | **35,744** | **71,488** | **71,488** | **0** | **0** |

Ordinary natural four-terminal missing-`Q` search is now retired as an active breakthrough route for these parent sets.

Artifacts:

- workflow run `30810878974`
- order-96 artifact `8859456435`, SHA-256 `dc0db45b6e862437a04d1a4b2f8b192bc7d905682b4ece86d772e6f10bb73bb3`
- order-100 artifact `8860190315`, SHA-256 `be7d0927c32594829115354db2788c5992bf69c720c41ff9e7641ee99d30514f`

## Immediate implementation checkpoint

The next committed executable work must contain:

1. `search/consecutive_face_ternary_scan.py`;
2. a proof workflow for all nonpositive consecutive triples;
3. `search/exact_face_trace_language.py` for candidate 489 face 2;
4. a machine-readable source-face specification;
5. a minimal face-patch generator;
6. a composition checker with witness validation;
7. a run specification fixing search bounds, solver versions, proof policy, and output paths.

The first binary milestone is:

```text
Either certify a consecutive facial H^{+--} obstruction,
or publish the complete exact face-2 trace language needed for amplifier synthesis.
```

No counterexample is currently claimed.