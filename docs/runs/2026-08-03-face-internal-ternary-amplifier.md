# Run Specification: Consecutive Ternary Scan and Face-Amplifier Synthesis

**Date:** 2026-08-03  
**Status:** committed specification; execution pending  
**Authoritative strategy:** `docs/FACE_INTERNAL_TERNARY_AMPLIFIER_2026-08-03.md`

## Objective

Produce a complete non-Hamiltonian Barnette graph by converting the proof-certified cofacial `H^{+--}` obstruction in canonical order-100 candidate 489 into a closed face replacement whose Hamiltonian boundary language is empty.

## Hypotheses

1. A consecutive three-edge facial `H^{+--}` obstruction may already exist in candidate 489 or the retained higher-order parent set.
2. If no direct consecutive obstruction exists, a small planar bipartite cubic patch inserted inside the certified face can force every global Hamiltonian trace into one of the source graph's certified forbidden states.
3. Because the source is already 3-connected and the patch can attach through multiple boundary regions, connectivity-first face insertion is more promising than repairing a two-vertex separator after multi-copy assembly.

## Source instance

```text
campaign: canonical order-100 search
source index: 489
vertices: 100
edges: 150
face index: 2
face length: 12
principal x: (14,18)
principal y: (10,17)
principal z: (5,11)
```

Canonical source and proof metadata are in:

```text
results/2026-08-02/three_edge_face_candidates.json
```

## Stage A: consecutive-triple scan

### Scope

1. all facial three-edge paths in candidate 489;
2. all facial three-edge paths in the 12 order-96 Grand-v3 parents;
3. all facial three-edge paths in the 12 order-100 Grand-v3 parents.

### Decision problem

For each oriented facial path `(a,b,c)`, decide whether a Hamiltonian cycle exists with:

```text
a excluded
b included
c excluded
```

### Classification

- `verified`: explicit Hamiltonian-cycle witness independently checked;
- `certified_negative`: CaDiCaL UNSAT with DRAT/LRAT accepted by an independent checker;
- `unknown`: timeout, malformed input, solver failure, or proof-check failure.

No single MILP infeasibility result is admissible.

### Acceptance

Any certified negative consecutive triple becomes the immediate counterexample-construction seed. Implement the explicit face construction associated with Hertel's equivalent strengthening, instantiate the resulting graph, and send it to whole-graph proof.

## Stage B: exact source-face language

If Stage A has no certified negative, complete the exact trace language of candidate 489 face 2.

### First layer

Enumerate all `2^12 = 4096` face-edge inclusion masks.

### Refined layer

For every feasible mask, classify the induced path connectivity among opened boundary terminals. Distinguish states with identical masks but different pairings.

### Required evidence

- explicit witness for every positive state;
- proof-producing SAT for every negative state used by synthesis;
- canonical state keys;
- independent witness checker;
- input graph and face hashes.

## Stage C: patch synthesis

### Terminal sets

Begin with the six terminals arising from cutting `x,y,z`. Then expand to 8, 10, or 12 terminals by paired subdivision of additional face edges when required for 3-connectivity or state control.

### Patch sizes

Search in increasing even internal order:

```text
4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24
```

### Hard graph constraints

- planar;
- bipartite;
- simple after gluing;
- internal degree three;
- correct terminal residual degrees;
- even internal faces;
- prescribed outer-face terminal order;
- glued graph cubic and 3-connected.

### Hamiltonian objective

Primary:

```text
exact composed boundary language is empty
```

Preferred explanatory form:

```text
all composed traces force x included and y,z excluded
```

### Search engine

Use counterexample-guided inductive synthesis:

1. solve for a legal patch topology;
2. ask for a Hamiltonian cycle in the glued graph;
3. validate and project any witness to a boundary trace;
4. block the trace family;
5. iterate;
6. on UNSAT, regenerate the whole-graph CNF independently and check the proof.

## Stage D: final certification

For every apparent counterexample:

1. canonicalize and deduplicate;
2. independently check simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three;
3. check the planar rotation system;
4. solve whole-graph Hamiltonicity with CaDiCaL;
5. retain textual DRAT/LRAT;
6. verify using an independent checker;
7. rerun through an independent Hamiltonian encoder;
8. publish graph6, edge list, embedding, CNFs, proof logs, checker logs, manifests, and hashes;
9. reproduce from clean GitHub Actions.

## Resource policy

- Stage A per case initial limit: 300 seconds;
- Stage B per state initial limit: 600 seconds, with deterministic escalation;
- patch synthesis per size: bounded workflow matrix with partial-output preservation;
- whole-graph proof: no final timeout classification other than `unknown`;
- all interrupted work must flush manifests and completed witnesses.

## Output paths

```text
results/2026-08-03/consecutive_face_ternary/
results/2026-08-03/face2_exact_language/
results/2026-08-03/face_amplifier/
```

## Stop conditions

Success:

```text
A simple cubic bipartite planar 3-connected graph has a checked whole-graph non-Hamiltonicity proof.
```

Bounded campaign failure:

```text
No counterexample patch through 24 internal vertices, with all tested topology classes and exact trace blockers published.
```

After bounded failure, switch to connectivity-first multi-copy six-pole relation synthesis. Do not return to random matching rarity or ordinary marginal Q search.