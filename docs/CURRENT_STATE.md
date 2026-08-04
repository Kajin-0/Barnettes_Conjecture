# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative pull request:** PR #1  
**Snapshot timestamp:** 2026-08-04 02:20 UTC  
**Counterexample found:** No

This is the single canonical mutable snapshot. Dated files under `docs/research-log/` preserve chronology. A mathematical result is not incorporated until its evidence, code, run specification, workflow state, hashes, and interpretation are committed.

## 1. Objective and proof standard

Barnette's conjecture states:

> Every simple cubic 3-connected bipartite planar graph is Hamiltonian.

A counterexample claim requires:

1. independent verification of simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three;
2. exact whole-graph non-Hamiltonicity in the primal edge formulation;
3. exact nonexistence of a two-induced-tree coloring in the dual formulation;
4. machine-checkable proof certificates accepted by independent checkers;
5. graph6, edge list, rotation system, construction manifest, hashes, commands, software versions, and clean workflow reproduction.

Timeouts, sampled misses, solver iteration limits, provisional infeasibility, malformed cases, and interrupted jobs are always `unknown`.

## 2. Primary strategy: dual embedded substitution around mandatory large faces

The strongest current route is now:

```text
certified large-face obstruction in candidate 489
    -> translate Hamiltonicity into a dual face-color cut
    -> mine compact prime forbidden boundary clauses on 10+-faces
    -> synthesize an even triangulated disk with the same cyclic boundary
    -> require its exact boundary language to lie inside a certified forbidden relation
    -> dualize to a simple cubic bipartite planar 3-connected graph
    -> prove non-Hamiltonicity independently in primal and dual encodings
```

### Why this supersedes abstract pole multiplication

Exact empty finite-state products are already abundant on abstract planar 3-connected interaction skeletons. Every fully instantiated four- and five-pole empty product tested so far is nonplanar. The missing resource is therefore not another abstract obstruction; it is an obstruction whose cyclic terminal order is geometrically realizable.

The dual formulation makes the embedding intrinsic. A primal face of length `d` is a degree-`d` dual vertex. Replacing that vertex by an even triangulated disk is the geometry-native analogue of replacing the entire primal face by a cubic bipartite disk patch.

Recent work proves that Barnette graphs whose faces all have size at most eight are Hamiltonian. A counterexample must therefore contain a face of size at least ten. The same work succeeds through exact embedded graph substitutions and exhaustive open-end Hamiltonian-state checks, strongly supporting the present route.

### Dual equivalence used

For a cubic plane graph `G` with dual `G*`:

- assign one binary color to every face of `G`, equivalently every vertex of `G*`;
- select a primal edge exactly when its two incident faces have different colors;
- a valid Hamiltonian cycle is such a cut whose selected edges form a connected spanning 2-factor;
- equivalently, the two dual color classes induce trees.

Barnette's conjecture is therefore equivalent to partitioning every simple even plane triangulation into two induced trees.

## 3. Strongest certified source: candidate 489

Candidate 489 is a verified simple cubic bipartite planar 3-connected graph with 100 vertices and 150 edges.

Its face-size multiset contains exactly three faces of size at least ten:

```text
12, 30, 30
```

The distinguished 12-face has cyclic vertex order

```text
5, 10, 17, 25, 35, 48, 40, 30, 22, 14, 18, 11
```

and principal certified obstruction

```text
x = (14,18) must be included
y = (10,17) must be excluded
z = (5,11) must be excluded
```

No Hamiltonian cycle satisfies that pattern.

Six source cases were independently solved UNSAT by CaDiCaL 3.0.1 and their textual DRAT proofs were accepted by `drat-trim`.

Evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- `search/sat_verify_face_constraints.py`
- `.github/workflows/face-three-edge-proof.yml`
- workflow run `30750008325`
- artifact `8834131003`
- artifact SHA-256 `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`

Deleting the three principal edges yields an exact six-terminal source pole:

```text
positive states = 26
exact negative states = 49
unknown states = 0
```

### Candidate 489 dual

The reconstructed dual has:

```text
vertices = 52
edges = 150
simple = true
planar = true
all degrees even = true
vertex connectivity = 4
```

The distinguished 12-face becomes a degree-12 dual vertex. The principal obstruction becomes three local color-parity conditions incident to that vertex:

```text
(14,18): bichromatic dual edge
(10,17): monochromatic dual edge
(5,11): monochromatic dual edge
```

## 4. Implemented dual campaigns

### 4.1 Independent dual face-cut proof

Script:

```text
search/dual_face_cut_obstruction.py
```

Workflow:

```text
.github/workflows/dual-face-cut-obstruction.yml
```

The formulation uses face-color variables as primary variables and primal edge variables constrained by XOR. It tests:

- all eight inclusion patterns on the principal triple;
- all six previously certified source obstructions.

A positive must independently validate:

- an explicit primal Hamiltonian cycle;
- equality between the selected primal edges and the dual color cut;
- two induced dual trees;
- all requested include/exclude conditions.

A negative is certified only when external CaDiCaL produces textual DRAT and `drat-trim` accepts it.

### 4.2 Large-face prime-implicate scan

Script:

```text
search/dual_face_implicate_scan.py
```

Workflow:

```text
.github/workflows/dual-face-implicate-scan.yml
```

It scans every partial boundary assignment of widths one, two, and three on the 12-, 30-, and 30-faces. For each face it:

1. classifies every include/exclude pattern with an incremental exact SAT oracle;
2. validates every positive by an explicit cycle;
3. extracts prime forbidden patterns not implied by a smaller negative assignment;
4. retains cyclic positions, spans, and gap signatures;
5. escalates the 32 most compact prime ternary clauses to CaDiCaL/DRAT proof.

The scanner deliberately labels internal solver negatives `solver_negative_unproved` until independent proof escalation.

### 4.3 Isolated execution

Temporary execution PR:

```text
PR #8
agent/dual-execution-20260804 -> agent/dual-base-20260804
```

The PR changes only the two workflow triggers and must not be merged. Checked artifacts will be reconciled into PR #1.

Design and provenance:

- `docs/DUAL_FACE_SUBSTITUTION_ATTACK_2026-08-04.md`
- `docs/runs/2026-08-04-dual-face-substitution.md`
- `results/2026-08-04/dual_face_substitution_plan.json`
- `docs/research-log/2026-08-04-0204-dual-face-substitution.md`
- `docs/research-log/2026-08-04-0210-dual-run-launch.md`

## 5. Parallel complete canonical order-16 patch search

The previous geometry-first six-port route remains active in parallel, but is now secondary to the dual substitution route.

Canonical generation:

```text
plantri -bp -c2 -m2 -e21 -g 16 RES/30
```

Isolated workflow run:

```text
30869004046
```

Temporary PR:

```text
PR #7
```

The 30 exact residues cover the complete canonical order-16 class. At this snapshot all jobs remain queued; no positive or negative mathematical inference is made.

## 6. Completed theorem-aligned scans

### Consecutive facial ternary condition

| Graph set | Cases | Hamiltonian witnesses | Certified negatives | Unknown |
|---|---:|---:|---:|---:|
| Candidate 489 | 300 | 300 | 0 | 0 |
| 12 order-96 parents | 3,456 | 3,456 | 0 | 0 |
| 12 order-100 parents | 3,600 | 3,600 | 0 | 0 |
| **Total** | **7,356** | **7,356** | **0** | **0** |

The consecutive facial route is closed for these 25 graphs.

### Grand Q-first v3

| Order | Parents | Patch sides | Q states | Positive | Missing | Unknown |
|---|---:|---:|---:|---:|---:|---:|
| 96 | 12 | 16,852 | 33,704 | 33,704 | 0 | 0 |
| 100 | 12 | 18,892 | 37,784 | 37,784 | 0 | 0 |
| **Total** | **24** | **35,744** | **71,488** | **71,488** | **0** | **0** |

Ordinary natural four-terminal missing-Q search is retired for those parent sets.

## 7. Small-patch and CEGIS closures

Bounded families already closed:

| Family | Exact result |
|---|---:|
| Small forced-edge expansions | 7,388/7,388 avoidance witnesses |
| Two-copy unavoidable-pair assemblies | 72/72 Hamiltonian |
| Candidate-489 cofacial two-edge-deletion poles | 54/54 maximal six-state languages |
| Six-port patches, orders 6-10 | minimum compatibility 14, zero maps 0 |
| Complete order-12 degree class | 98,484 matrices, minimum compatibility 9, zero maps 0 |
| Complete canonical order-14 class | minimum compatibility 14, zero maps 0 |

Relation-first candidate-489 CEGIS proposed 200,000 topologies at orders 16-24 and found no zero selector. Every job reached its 20,000-iteration cap, so this is not an exhaustive nonexistence result. Best compatibility was 14 at order 18.

## 8. Asano repair and restrictive four-pole languages

The 26-vertex 2-connected cubic bipartite planar non-Hamiltonian graph was reconstructed as three edge-deleted cubes joined between two hubs. It has 324 perfect matchings and no Hamiltonian cycle.

A complete 7,986-case three-edge permutation repair produced 128 Barnette graphs; all 128 are Hamiltonian and reduce to two nonisomorphic graphs.

Each repaired graph contains unavoidable cofacial pairs yielding the exact five-state pole

```text
A = {P02, P03, P12, P13, Q01_23}.
```

The complete order-10 four-pole degree class produced four restrictive relations:

```text
B0 = {P02, P03, Q02_13, Q03_12}
B1 = {P02, P12, Q02_13, Q03_12}
B2 = {P03, P13, Q02_13, Q03_12}
B3 = {P12, P13, Q02_13, Q03_12}
```

## 9. Mixed-pole exact synthesis and its geometric failure

### Four-pole K4

```text
zero abstract relation assignments = 3,072
complete concrete assemblies tested = 12,800
planar concrete assemblies = 0
```

### Five-pole doubled wheel

```text
zero abstract relation assignments = 43,008
complete concrete assemblies tested = 39,168
planar concrete assemblies = 0
```

### Six-pole octahedron

```text
total exact matching/relation combinations = 608,000,000
zero combinations = 0
```

Five other six-pole planar 3-connected multigraph skeleton classes admit abstract empty products. Four reach abstract order 92. A pool of 100,000 representative concrete order-92 assemblies was entirely nonplanar, but that last geometry screen is not exhaustive over every terminal-labeled `A` pole.

This body of evidence is the central reason for moving to dual embedded substitution.

## 10. Connectivity-two near-counterexamples

Corrected exact `AABCC` synthesis over 100,000 permutations produced:

| Stage | Count |
|---|---:|
| Exact zero languages | 9,818 |
| Legal and copy-connected | 2,597 |
| Planar | 122 |
| Planar with target edges cofacial | 65 |
| 3-connected | 0 |

All 65 near-counterexamples have connectivity two. Generic separator-crossing `C4` repair produced 655 valid 3-connected Barnette graphs, but every one regained the forbidden-compatible Hamiltonian trace.

## 11. Immediate execution sequence

1. Complete the independent dual proof campaign and correct any discrepancy before using the dual scanner.
2. Complete the width-1/2/3 scans on all three mandatory large faces.
3. Add every checked prime ternary clause to a machine-readable embedded obstruction library.
4. Select the smallest cyclic obstruction kernel with no width-1 or width-2 explanation.
5. Enumerate even triangulated disk substitutions with that exact cyclic boundary.
6. Compute exact open-end two-tree/path-cover languages before whole-graph assembly.
7. Reject substitutions that do not preserve dual 4-connectivity or primal 3-connectivity.
8. For any zero composition, immediately generate both primal and dual whole-graph proof packages.
9. Reconcile the parallel complete order-16 canonical patch search when Actions capacity permits.

## 12. Permanent warnings

1. A positive underapproximation cannot establish a negative language composition.
2. Terminal order and embedding orientation are mathematical data.
3. Abstract interaction-skeleton planarity does not imply planarity after pole instantiation.
4. Connectivity must be designed into the substitution, not repaired afterward.
5. SciPy/HiGHS infeasibility is not proof.
6. A SAT solver's incremental UNSAT return is discovery evidence until reproduced with a checked certificate.
7. PR prose, chat output, queued workflows, and sampled searches are not mathematical evidence.

## 13. Current assessment

No counterexample has been found.

The most important conceptual advance is that the search target is now localized in the correct category. The missing object is not simply a sparse boundary relation. It is:

```text
an even triangulated disk with a realizable cyclic boundary whose exact
two-tree language lies inside a proof-certified forbidden relation and whose
dual closure remains 4-connected.
```

That object would dualize directly to the planar 3-connected cubic bipartite selector that the earlier abstract language searches could not realize.
