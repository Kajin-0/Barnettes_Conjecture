# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative pull request:** PR #1  
**Snapshot timestamp:** 2026-08-04 01:20 UTC  
**Counterexample found:** No

This is the single canonical mutable snapshot. `docs/RESEARCH_LOG.md` and dated files under `docs/research-log/` preserve chronology.

## 1. Objective and proof standard

Barnette's conjecture states:

> Every simple cubic 3-connected bipartite planar graph is Hamiltonian.

A counterexample claim requires all of the following:

1. independent checks of simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three;
2. exact whole-graph non-Hamiltonicity;
3. a machine-checkable CaDiCaL DRAT/LRAT proof accepted by an independent checker;
4. a second independent Hamiltonian encoding or transparent exact decomposition check;
5. graph6, edge list, embedding data, construction manifest, hashes, software versions, commands, and clean workflow reproduction.

Timeouts, iteration caps, interrupted runs, sampled misses, and single-solver infeasibility statuses are always `unknown`.

## 2. Primary strategy: geometry-first six-port amplification

The strongest current construction route is:

```text
candidate 489 exact 26-state six-terminal source pole
    -> canonical planar bipartite six-port patch generation
    -> exact 75-state patch language
    -> test every color-compatible terminal map
    -> require empty exact composition and 3-connected Barnette assembly
    -> whole-graph CaDiCaL proof plus independent DRAT check
```

The active complete search begins at internal patch order 16:

```text
plantri -bp -c2 -m2 -e21 -g 16 RES/64
```

Workflow:

```text
.github/workflows/canonical-six-port-order16.yml
```

Initial run:

```text
30868419278
```

Commit introducing the workflow:

```text
3ee903a12d3cad62f0638adf87d3408112b5429a
```

### Why geometry-first is primary

Exact empty finite-state products are now abundant on abstract planar 3-connected interaction skeletons. The obstruction repeatedly disappears when actual pole embeddings are imposed because every concretely tested empty product requires nonplanar terminal routing.

The missing object is therefore not merely a restrictive language. It is a restrictive language with a realizable planar terminal rotation and enough distributed attachment to preserve 3-connectivity.

## 3. Strongest certified source: candidate 489

Candidate 489 is a verified simple cubic bipartite planar 3-connected graph with 100 vertices and 150 edges.

On face 2, with cyclic vertex order

```text
5, 10, 17, 25, 35, 48, 40, 30, 22, 14, 18, 11
```

the principal certified obstruction is

```text
x = (14,18)
y = (10,17)
z = (5,11)
```

No Hamiltonian cycle contains `x` while avoiding both `y` and `z`.

Six source cases were solved UNSAT by CaDiCaL 3.0.1 and their textual DRAT proofs were accepted by `drat-trim`.

Evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- `search/sat_verify_face_constraints.py`
- `.github/workflows/face-three-edge-proof.yml`
- workflow run `30750008325`
- artifact `8834131003`
- artifact SHA-256 `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`

Deleting the three obstruction edges produces an exact six-terminal pole with:

```text
positive states = 26
exact negative states = 49
unknown states = 0
```

## 4. Completed theorem-aligned scans

### Consecutive facial ternary condition

Every consecutive facial three-edge path was tested with outer edges excluded and the middle edge included.

| Graph set | Cases | Hamiltonian witnesses | Certified negatives | Unknown |
|---|---:|---:|---:|---:|
| Candidate 489 | 300 | 300 | 0 | 0 |
| 12 order-96 Grand-v3 parents | 3,456 | 3,456 | 0 | 0 |
| 12 order-100 Grand-v3 parents | 3,600 | 3,600 | 0 | 0 |
| **Total** | **7,356** | **7,356** | **0** | **0** |

The consecutive facial route is closed for these 25 graphs.

### Grand Q-first v3

Workflow run `30810878974` completed:

| Order | Parents | Patch sides | Q states | Positive | Missing | Unknown |
|---|---:|---:|---:|---:|---:|---:|
| 96 | 12 | 16,852 | 33,704 | 33,704 | 0 | 0 |
| 100 | 12 | 18,892 | 37,784 | 37,784 | 0 | 0 |
| **Total** | **24** | **35,744** | **71,488** | **71,488** | **0** | **0** |

Ordinary natural four-terminal missing-Q search is retired for these parent sets.

## 5. Exact face relations and small-patch closures

Candidate 489's 12-edge face has 322 locally feasible inclusion masks; 100 extend to Hamiltonian cycles and 222 do not.

Eight minimal cofacial edge-pair relations are proof-certified:

```text
for every Hamiltonian cycle C, a in C or b in C.
```

All eight double-avoidance cases were independently encoded, solved UNSAT by CaDiCaL, and accepted by `drat-trim`.

Bounded families closed:

| Family | Exact result |
|---|---:|
| Small forced-edge expansions | 7,388/7,388 avoidance witnesses |
| Two-copy unavoidable-pair assemblies | 72/72 Hamiltonian |
| Candidate-489 cofacial two-edge-deletion poles | 54/54 maximal six-state languages |
| Six-port patches, orders 6-10 | minimum compatibility 14, zero maps 0 |
| Complete order-12 degree class | 98,484 matrices, minimum compatibility 9, zero maps 0 |
| Complete canonical order-14 class | minimum compatibility 14, zero maps 0 |

The first unresolved complete canonical patch order is 16.

## 6. Relation-first candidate-489 CEGIS

Workflow run `30864152943` searched unrestricted bipartite degree-constrained topology hosts at patch orders 16, 18, 20, 22, and 24 with two phase seeds each.

```text
SAT topologies proposed = 200,000
zero selectors = 0
whole-graph candidates = 0
```

Every job reached the 20,000-iteration cap. This is not an exhaustive nonexistence result.

| Patch order | Best compatibility |
|---:|---:|
| 16 | 17 |
| 18 | 14 |
| 20 | 17 |
| 22 | 22 |
| 24 | no structurally valid topology reached |

The unrestricted host spends most proposals on nonplanar graphs. It is retained as a secondary relation-first engine, not the primary generator.

## 7. Asano reconstruction and connectivity repair

The 26-vertex 2-connected cubic bipartite planar non-Hamiltonian graph was reconstructed as three edge-deleted cubes joined between two degree-three hubs.

```text
vertices = 26
edges = 39
vertex connectivity = 2
perfect matchings = 324
Hamiltonian cycles = 0
```

Graph6:

```text
YPH?gWW?{??@?AO???g?E?@_??{?????C??AO?????A_??E???W???B_
```

A color-preserving three-edge permutation repair was exhausted:

| Classification | Count |
|---|---:|
| Total | 7,986 |
| Nonplanar | 5,999 |
| Planar, connectivity 2 | 1,859 |
| 3-connected Barnette graphs | 128 |
| Barnette graphs with explicit Hamiltonian cycle | 128 |

The 128 graphs reduce to two nonisomorphic graphs, each with 48 Hamiltonian cycles.

The hub-deleted three-module core cannot yield a 3-connected graph through any external six-port connector: each cube module has only two attachment vertices, and deleting their two connector neighbors isolates the module. This route is permanently retired.

## 8. New restrictive four-terminal pole languages

Each repaired 26-vertex graph has nine unavoidable cofacial edge pairs. Deleting any one gives an exact five-state pole

```text
A = {P02, P03, P12, P13, Q01_23}.
```

All 18 poles have the same language and no unknown states.

The complete order-10 four-pole degree class produced four restrictive relations:

```text
B0 = {P02, P03, Q02_13, Q03_12}
B1 = {P02, P12, Q02_13, Q03_12}
B2 = {P03, P13, Q02_13, Q03_12}
B3 = {P12, P13, Q02_13, Q03_12}
```

Representative graph6 records:

```text
B0: I?@bCqWM?
B1: I??uEOwM?
B2: I?B@eOwM?
B3: I?AdApWM?
```

## 9. Mixed-pole exact synthesis

### Four-pole K4 skeleton

```text
color-valid 3-connected interaction matchings = 3,072
zero-language matchings = 1,536
zero relation assignments = 3,072
concrete assemblies tested = 12,800
planar concrete assemblies = 0
```

### Five-pole doubled-wheel skeleton

```text
Eulerian orientations = 26
terminal matchings = 6,656
abstract relation combinations = 20,800,000
zero relation assignments = 43,008
concrete assemblies tested = 39,168
planar concrete assemblies = 0
```

### Six-pole octahedral skeleton

```text
Eulerian orientations = 38
terminal matchings = 38,912
relation assignments per matching = 15,625
total exact combinations = 608,000,000
zero combinations = 0
```

### Other six-pole planar 3-connected multigraph skeletons

Five remaining skeleton classes all admit abstract empty products. Four classes have abstract order-92 compositions with two `A` poles and four order-10 poles.

A pool of 100,000 distinct exact order-92 empty products was generated from 8,775,756 random exact tests. Every representative concrete embedding was nonplanar.

This 100,000-case geometry screen is large but not an exhaustive classification over all terminal-labeled `A` poles.

Detailed evidence:

- `docs/ASANO_REPAIR_MIXED_POLES_2026-08-04.md`
- `results/2026-08-04/asano_repair_mixed_pole_summary.json`
- `docs/research-log/2026-08-04-0120-asano-repair-mixed-poles.md`

## 10. Exact six-pole and connectivity-two near-counterexamples

The original certified ternary poles `A`, `B`, and `C` each have:

```text
positive = 26
exact negative = 49
unknown = 0
```

Corrected exact `AABCC` synthesis over 100,000 permutations produced:

| Stage | Count |
|---|---:|
| Exact zero languages | 9,818 |
| Legal and copy-connected | 2,597 |
| Planar | 122 |
| Planar with target edges cofacial | 65 |
| 3-connected | 0 |

All 65 near-counterexamples have connectivity two. Generic separator-crossing `C4` repair produced 655 valid 3-connected Barnette graphs, but every one regained the forbidden-compatible Hamiltonian trace.

This remains a fallback library, not the primary route.

## 11. Permanent warnings

1. A positive underapproximation cannot establish a negative language composition.
2. SciPy/HiGHS infeasibility is not proof; earlier false negatives were retracted after witnesses were found.
3. Matching rarity is not exact language sparsity.
4. Terminal order and embedding orientation are mathematical data, not formatting details.
5. 3-connectivity must be imposed during synthesis, not repaired after an obstruction is assembled.
6. Abstract interaction-skeleton planarity does not imply planarity of the instantiated pole composition.
7. PR prose, chat output, and interrupted workflows are not reproducible evidence.

## 12. Retired or strongly deprioritized routes

Do not restart without a new mathematical reason:

1. random perfect-matching fragmentation as evidence of non-Hamiltonicity;
2. ordinary four-terminal missing-Q search on the retained order-96/order-100 parents;
3. candidate-489 cofacial two-edge deletion as a restrictive four-pole source;
4. small forced-edge expansion through the completed 7,388-case family;
5. direct two-copy unavoidable-pair closure;
6. hub-deleted Asano-core connector synthesis;
7. homogeneous five-state pole composition through six copies;
8. mixed four-pole K4 and five-pole doubled-wheel closure—the complete concrete classes are nonplanar;
9. generic post hoc connectivity repair;
10. blind growth without an exact boundary-language objective.

## 13. Immediate execution sequence

1. Complete workflow `30868419278` across all 64 order-16 plantri residues.
2. Aggregate input counts, accepted patch counts, exact language sizes, global minimum compatibility, zero maps, and incomplete states.
3. If any zero map yields a Barnette graph, produce the full proof bundle immediately.
4. If order 16 closes positively, extend the same canonical geometry-first campaign to order 18 with sharding determined from the observed order-16 population.
5. Continue geometry-aware relation synthesis using terminal rotations extracted from canonical planar patches, rather than abstract pole languages alone.

## 14. Current assessment

No counterexample has been found.

The project has moved beyond searching for any local obstruction. It now has multiple exact obstruction languages, abundant abstract empty products, a proof-producing whole-graph pipeline, and a sharply isolated missing object:

```text
one planar six-terminal selector with empty exact composition and a
3-connected glued graph.
```

The active order-16 canonical campaign is the strongest current attempt to produce that object.
