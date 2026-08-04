# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative research PR:** PR #1, temporarily closed and unmerged to stop obsolete workflow fan-out  
**Snapshot timestamp:** 2026-08-04 02:40 UTC  
**Counterexample found:** No

This is the single canonical mutable snapshot. Dated files under `docs/research-log/` preserve chronology. A mathematical result is not incorporated until its code, machine-readable evidence, proof policy, workflow state, hashes, and interpretation are committed.

## 1. Objective and proof standard

Barnette's conjecture states:

> Every simple cubic 3-connected bipartite planar graph is Hamiltonian.

A counterexample claim requires:

1. independent verification of simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three;
2. exact whole-graph non-Hamiltonicity in the primal selected-edge formulation;
3. exact nonexistence of a two-induced-tree coloring in the dual formulation;
4. machine-checkable CaDiCaL proof certificates accepted by `drat-trim` or an equivalently independent checker;
5. graph6, edge list, rotation system, construction manifest, source hashes, commands, software versions, and clean workflow reproduction.

Timeouts, sampled misses, solver iteration limits, provisional infeasibility, malformed cases, and queued or interrupted jobs are always `unknown`.

## 2. Primary strategy: embedded dual substitution around a mandatory large face

The strongest current route is:

```text
candidate 489 certified facial obstruction
    -> dualize to an even plane triangulation
    -> remove the degree-12 dual vertex corresponding to the obstructed face
    -> insert every canonical parity-valid 12-boundary triangulated disk
    -> require the closed dual to be even and 4-connected
    -> dualize back to a cubic bipartite planar brace
    -> test Hamiltonicity exactly
    -> prove every provisional negative independently in primal and dual encodings
```

This supersedes abstract pole multiplication because exact empty abstract products are already abundant, while every fully instantiated four- and five-pole empty product tested so far is nonplanar. The remaining bottleneck is a realizable cyclic boundary rotation. In the dual disk model, the embedding is part of the generated object.

A recent theorem proves Hamiltonicity when every face has size at most eight. Therefore any counterexample must contain a face of size at least ten. The same theorem succeeds through exact embedded graph substitutions and exhaustive open-end state checking, strongly supporting this route.

Barnette's conjecture also reduces to cubic planar braces. Requiring dual vertex connectivity at least four targets the cyclically 4-connected/brace core rather than creating another connectivity-two near-counterexample.

## 3. Strongest certified source: candidate 489

Candidate 489 is a verified simple cubic bipartite planar 3-connected graph with:

```text
vertices = 100
edges = 150
large face sizes = 12, 30, 30
```

The distinguished 12-face has cyclic vertex order

```text
5, 10, 17, 25, 35, 48, 40, 30, 22, 14, 18, 11
```

and principal certified obstruction

```text
(14,18) included
(10,17) excluded
(5,11) excluded
```

No Hamiltonian cycle satisfies that pattern.

Six source cases were solved UNSAT by CaDiCaL and their textual DRAT proofs were accepted by `drat-trim`.

Evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- `search/sat_verify_face_constraints.py`
- workflow run `30750008325`
- artifact `8834131003`
- artifact SHA-256 `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`

Deleting the three principal edges produces an exact six-terminal source pole:

```text
positive states = 26
exact negative states = 49
unknown states = 0
```

The complete 12-face mask exploration found:

```text
all Boolean masks = 4096
locally degree-feasible masks = 322
Hamiltonian-positive masks = 100
exact negative masks = 222
```

Eight unavoidable cofacial edge pairs have independent checked proofs. A fresh width-three scan is active because the older aggregate prime-cube width distribution must be independently reproduced before it is used for substitution synthesis.

## 4. Candidate 489 dual

The reconstructed dual is a simple even plane triangulation with:

```text
vertices = 52
edges = 150
all degrees even = true
vertex connectivity = 4
```

The distinguished 12-face becomes a degree-12 dual vertex. Its cyclic neighbor order after removal is

```text
3, 6, 10, 18, 26, 29, 21, 16, 9, 5, 11, 0
```

The principal obstruction becomes one bichromatic and two monochromatic incident dual edges:

```text
(14,18): bichromatic
(10,17): monochromatic
(5,11): monochromatic
```

For a cubic plane graph, a Hamiltonian cycle is the cut of a binary face coloring whose selected edges form a connected spanning 2-factor; equivalently, the two dual color classes induce trees.

## 5. Independent dual proof and large-face relation mining

### Independent dual proof

Script:

```text
search/dual_face_cut_obstruction.py
```

Workflow:

```text
.github/workflows/dual-face-cut-obstruction.yml
```

It tests all eight patterns on the principal triple and independently re-proves all six source obstructions. A positive must validate both an explicit primal Hamiltonian cycle and two induced dual trees. A negative requires a checked CaDiCaL proof.

Active isolated run:

```text
30871499944
```

### Large-face prime-implicate scan

Script:

```text
search/dual_face_implicate_scan.py
```

Workflow:

```text
.github/workflows/dual-face-implicate-scan.yml
```

It classifies every width-1, width-2, and width-3 include/exclude assignment on candidate 489's 12-, 30-, and 30-faces, extracts prime forbidden patterns with cyclic positions and gap signatures, and proof-escalates 32 compact ternary clauses.

Active isolated run:

```text
30871499947
```

Temporary execution PR #8 contains only trigger changes and must not be merged.

## 6. Complete low-order dual 12-disk substitution campaign

Removing the degree-12 dual vertex leaves a 12-cycle boundary. Let a candidate disk triangulation be glued to this boundary.

### Exact Eulerian parity criterion

Each outside boundary vertex loses one incident radial edge, so its outside degree is odd. In the closed triangulation:

```text
all 12 boundary degrees in the disk must be odd;
all internal disk degrees must be even.
```

This criterion is exact, not heuristic.

### Canonical generation classes

Plantri partitions minimum-degree-three 12-disk triangulations into:

```text
-P12 -c3m3   no boundary chord, no degree-two boundary vertex
-P12 -c2x    at least one boundary chord, no degree-two boundary vertex
```

Together these classes cover every minimum-degree-three canonical 12-disk triangulation before the parity filter.

Disk orders 13 through 18 are being searched completely. A disk of order `n` produces:

```text
closed dual order = n + 39
primal cubic order = 2n + 74
```

Thus the current complete campaign covers primal orders 100 through 110.

### Search transaction

For every canonical disk and all 24 dihedral boundary maps:

1. validate the embedded disk and exact degree parity;
2. assemble and deduplicate the closed dual;
3. require planarity, triangulation edge count, all-even degrees, and dual connectivity at least four;
4. dualize and independently verify every Barnette predicate;
5. screen Hamiltonicity with an exact lazy-cut SAT oracle;
6. escalate every provisional negative to both the primal selected-edge proof and the dual face-color/two-tree proof;
7. accept a counterexample only if both proof certificates are independently checked.

Implementation:

```text
search/dual_disk_substitution_search.py
```

Chordless workflow and run:

```text
.github/workflows/dual-disk-substitution-search.yml
30871892938
PR #9
```

Chord-required complement and run:

```text
.github/workflows/dual-disk-chorded-substitution-search.yml
30872355766
PR #10
```

All jobs are currently queued. No mathematical inference is made from queue state.

## 7. Source-recovery regression

The order-13 star disk consists of a 12-cycle and one internal vertex adjacent to all boundary vertices. It satisfies the exact parity criterion.

A local structural regression tested all 24 dihedral maps:

```text
24/24 assembled duals are isomorphic to candidate 489's dual;
assembled dual order = 52;
assembled dual connectivity = 4;
dualization returns a 100-vertex graph isomorphic to candidate 489.
```

This validates boundary identification, cyclic gluing, order conversion, and primal reconstruction. It does not validate the SAT/proof implementation; the order-13 Actions job must supply that regression.

Evidence:

- `results/2026-08-04/dual_disk_source_recovery_regression.json`
- `docs/research-log/2026-08-04-0230-dual-disk-search.md`

## 8. Why prior major routes are secondary or retired

### Consecutive facial ternary condition

Across candidate 489 and 24 retained order-96/order-100 parents:

```text
cases = 7356
verified positives = 7356
certified negatives = 0
unknown = 0
```

### Grand Q-first v3

```text
parents = 24
patch sides = 35744
Q states = 71488
positive = 71488
missing = 0
unknown = 0
```

### Relation-first candidate-489 CEGIS

```text
SAT topologies proposed = 200000
zero selectors = 0
best compatibility = 14 at patch order 18
```

Every job ended at its iteration cap, so this is not an exhaustive nonexistence result.

### Complete small six-port classes

```text
orders 6-10: zero maps 0
order 12: 98484 matrices, zero maps 0
canonical order 14: zero maps 0
```

The order-16 canonical patch workflow remains committed but its temporary execution PR #7 was closed to release Actions capacity for the stronger dual campaigns.

### Mixed restrictive poles

Abstract exact zeros are abundant:

```text
four-pole K4 zero assignments = 3072
five-pole doubled-wheel zero assignments = 43008
```

But complete concrete tests found:

```text
12800/12800 four-pole assemblies nonplanar
39168/39168 five-pole assemblies nonplanar
```

The octahedral six-pole class was closed over 608,000,000 exact matching/relation combinations with no zero. Other six-pole multigraph skeletons admit abstract order-92 zeros, but 100,000 representative concrete assemblies were nonplanar.

### Connectivity-two near-counterexamples

Corrected `AABCC` synthesis found 65 planar zero-language assemblies with cofacial target edges, but all had vertex connectivity two. Generic `C4` repair produced 655 Barnette graphs and every one regained the forbidden-compatible Hamiltonian trace.

## 9. Repository and workflow control

PR #1 was temporarily closed, not merged or deleted, because every research commit was launching roughly twenty obsolete workflows and starving the isolated dual campaigns. The authoritative branch and complete history remain intact. PR #1 can be reopened after workflow triggers are consolidated.

Temporary execution PRs:

```text
PR #8  independent dual proof and large-face scan
PR #9  chordless 12-disk classes
PR #10 chord-required 12-disk complement
```

None is to be merged.

## 10. Immediate execution sequence

1. Complete independent dual proof run `30871499944` and reject the shared dual code if it fails to reproduce the six source certificates.
2. Complete large-face scan `30871499947`; reconcile the older prime-cube summary against the independently proof-certified ternary clauses.
3. Complete chordless run `30871892938` and require order 13 to reconstruct candidate 489 with an explicit Hamiltonian witness.
4. Complete chorded run `30872355766`.
5. Aggregate every order 13-18 disk from both plantri classes, deduplicate closed duals, and record the complete 100-110 vertex substitution frontier.
6. For any provisional negative, require both primal and dual checked proof packages before further interpretation.
7. If orders 13-18 close positively, extend disk order with exact sharding determined from observed plantri counts and rank hard positive instances by SAT connectivity rounds and facial obstruction density.
8. Reopen PR #1 only after obsolete trigger paths are consolidated.

## 11. Current assessment

No counterexample has been found.

The search is now aimed at a sharply defined construction object in the correct embedded category:

```text
an even triangulated 12-disk whose cyclic closure with candidate 489 remains
4-connected but admits no partition into two induced trees.
```

Such a disk dualizes directly to a simple cubic bipartite planar brace and bypasses the nonplanarity and connectivity-two failures that defeated the strongest previous obstruction compositions.
