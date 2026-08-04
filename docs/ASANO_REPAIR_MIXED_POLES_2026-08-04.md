# Asano Repair and Mixed Four-Pole Search

**Date:** 2026-08-04 UTC  
**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Branch:** `agent/adversarial-search-v2`  
**Counterexample found:** No

## 1. Objective

The candidate-489 six-terminal source has an exact 26-state language and a proof-certified ternary obstruction, but ordinary four-terminal deletions expose the maximal six-state language. This campaign sought a more restrictive intermediate pole and a planar 3-connected composition capable of turning a local obstruction into a closed non-Hamiltonian Barnette graph.

The strongest alternative seed is the 26-vertex 2-connected cubic bipartite planar non-Hamiltonian graph traditionally associated with Asano. It can be reconstructed as three copies of a cube with one edge removed, joined between two degree-three hubs.

## 2. Exact reconstruction of the 26-vertex seed

The reconstructed graph has:

```text
vertices = 26
edges = 39
simple = true
cubic = true
bipartite = true
planar = true
vertex connectivity = 2
perfect matchings = 324
Hamiltonian cycles = 0
```

Graph6:

```text
YPH?gWW?{??@?AO???g?E?@_??{?????C??AO?????A_??E???W???B_
```

The Hamiltonicity check used the cubic-graph identity that the complement of a Hamiltonian cycle is a perfect matching. All 324 perfect matchings were enumerated; no complement was connected.

## 3. Connectivity-restoring three-edge permutation repair

One internal edge was deleted from each cube module. The three endpoints in one bipartition class were reconnected to the three endpoints in the opposite class by each of the six permutations.

Across all edge triples and permutations:

| Classification | Count |
|---|---:|
| Total repairs | 7,986 |
| Nonplanar | 5,999 |
| Planar, connectivity 2 | 1,859 |
| Planar, 3-connected Barnette graphs | 128 |
| Barnette graphs with explicit Hamiltonian cycle | 128 |

The 128 Barnette graphs reduce to two nonisomorphic graphs. Each has 48 Hamiltonian cycles.

```text
YOSr?]?CA@???A?C??g?E?@_??w@GC?????A?C????A_??E???W???B_
YOSr?]?CA@???A?C??g?E?@_??w@????C??A_C???GA???E???W???B_
```

Only the two three-cycles on the module endpoints succeed, and only when each removed module edge is one of the four hub-adjacent types:

```text
L-A, L-E, R-B, R-F
```

## 4. New exact five-state pole

Each repaired graph has nine cofacial edge pairs that cannot both be avoided by a Hamiltonian cycle. Deleting either pair produces a four-terminal pole with terminal colors

```text
1, 1, 0, 0
```

and exact language

```text
A = {P02, P03, P12, P13, Q01_23}.
```

Thus the pole realizes every cross-color Hamiltonian spanning path but only one of the three four-terminal path-pairing states.

All 18 such poles have this same five-state language. There are no unknown states.

Direct two-pole composition is not enough:

```text
maps tested = 1,296
minimum compatibility = 4
zero maps = 0
planar maps = 1,296
vertex connectivity = 2 for all maps
```

## 5. Restrictive order-10 pole classes

The complete labeled bipartite degree class with ten vertices, four degree-two terminals, and six degree-three internal vertices contains 1,486 matrices. Exact path-cover enumeration gives:

| Exact language size | Count |
|---:|---:|
| 4 | 36 |
| 5 | 9 |
| 6 | 720 |
| 7 | 504 |
| Invalid, nonplanar, or disconnected | 217 |

The four restrictive four-state relation types are:

```text
B0 = {P02, P03, Q02_13, Q03_12}
B1 = {P02, P12, Q02_13, Q03_12}
B2 = {P03, P13, Q02_13, Q03_12}
B3 = {P12, P13, Q02_13, Q03_12}
```

Representative graph6 records are:

```text
B0: I?@bCqWM?
B1: I??uEOwM?
B2: I?B@eOwM?
B3: I?AdApWM?
```

## 6. Mixed finite-state synthesis

### 6.1 Four poles: K4 interaction skeleton

Every color-valid terminal matching whose underlying simple interaction graph has vertex connectivity at least three was tested.

```text
terminal matchings = 3,072
zero-language matchings = 1,536
zero relation assignments = 3,072
```

The zero assignments typically use two `A` poles and two restrictive `B` poles. This is the first abstract zero relation found on a 3-connected interaction skeleton.

However, after quotienting by pole permutation, all 128 geometric configurations were instantiated against all ten terminal-labeled repaired-Asano pole classes in both `A` positions:

```text
concrete assemblies = 12,800
planar = 0
nonplanar = 12,800
```

### 6.2 Five poles: wheel with two doubled rim edges

The complete planar 3-connected 4-regular interaction class on five vertices is a wheel with two opposite rim edges doubled.

```text
Eulerian orientations = 26
terminal matchings = 6,656
relation assignments per matching = 3,125
total abstract combinations = 20,800,000
zero-language matchings = 2,560
zero relation assignments = 43,008
```

After quotienting by independent same-color terminal swaps, 96 mixed configurations remain. The repaired-Asano poles have 12 terminal-labeled classes after those swaps.

```text
concrete assemblies = 39,168
planar = 0
nonplanar = 39,168
```

### 6.3 Six poles: octahedron

For the simple 4-regular planar 4-connected octahedral skeleton:

```text
Eulerian orientations = 38
terminal matchings = 38,912
relation assignments per matching = 15,625
total exact combinations = 608,000,000
zero-language combinations = 0
```

This is a complete finite-state closure, not sampling.

### 6.4 Other planar 3-connected six-pole multigraph skeletons

There are five remaining loopless 4-regular planar 3-connected multigraph skeleton classes on six vertices. Exact random relation testing found a zero-language assignment in every class, frequently within the first few dozen trials.

Four classes admit abstract candidates with exactly two `A` poles and four order-10 poles:

```text
abstract candidate order = 2*26 + 4*10 = 92.
```

A pool of 100,000 distinct 92-vertex zero-language assignments was generated from 8,775,756 exact random tests. Under the representative pole embeddings:

```text
concrete assemblies tested = 100,000
planar = 0
nonplanar = 100,000
```

This 100,000-case geometry screen is large but not exhaustive over all terminal-labeled repaired-Asano pole choices.

## 7. Relation-first candidate-489 CEGIS result

Workflow run `30864152943` tested orders 16, 18, 20, 22, and 24 with two phase seeds each.

Each job proposed 20,000 SAT topologies. Every job reached the iteration cap, so this is not a bounded nonexistence result.

| Patch order | Best compatibility | Structurally valid topologies across the two runs |
|---:|---:|---:|
| 16 | 17 | 16 |
| 18 | 14 | 4 |
| 20 | 17 | 2 |
| 22 | 22 | 2 |
| 24 | none reached | 0 |

No zero-language selector or whole-graph candidate appeared.

The unrestricted `K_{q,q}` topology host spends most proposals on nonplanar graphs. It remains useful as a relation-first pilot, but it is not the strongest sole generator.

## 8. Structural interpretation

The finite-state obstruction is no longer scarce. Mixed `A/B` relations produce thousands of empty products on abstract planar 3-connected interaction skeletons.

The bottleneck is now geometric:

```text
empty exact language  +  planar terminal routing  +  3-connectivity.
```

Every concretely tested mixed zero through five pole copies is nonplanar. The octahedral six-pole class is logically too permissive. Other six-pole multigraph classes have logical zeros but have not yet produced a planar concrete realization.

This changes the primary strategy from abstract relation multiplication to geometry-first canonical patch generation.

## 9. Active campaign

The next complete campaign is canonical order-16 six-port generation:

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

Every accepted patch receives:

1. exact classification of all 75 six-terminal states;
2. all color-compatible maps against candidate 489's exact 26-state pole;
3. Barnette-predicate validation for every zero composition;
4. whole-graph CaDiCaL proof generation;
5. independent `drat-trim` verification.

## 10. Current conclusion

No counterexample has been found.

The strongest positive development is that exact zero-language compositions now appear abundantly at abstract orders corresponding to 92 vertices. The strongest negative development is that all fully instantiated mixed zero classes through five poles require nonplanar terminal routing.

The immediate breakthrough target is therefore:

```text
one canonical planar order-16-or-larger six-port patch whose exact language
is disjoint from candidate 489's 26-state source language and whose glued
graph is 3-connected.
```

Machine-readable summary:

- `results/2026-08-04/asano_repair_mixed_pole_summary.json`
