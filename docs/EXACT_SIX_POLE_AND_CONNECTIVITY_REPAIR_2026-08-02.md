# Exact Six-Pole Languages and Connectivity-Repair Search

**Date:** 2026-08-02  
**Status:** certified ternary obstruction; first complete connectivity-repair family eliminated  
**Counterexample found:** no

## Central result retained

Canonical order-100 candidate 489 is a Barnette graph with proof-certified cofacial triples `(x,y,z)` for which no Hamiltonian cycle contains `x` while avoiding both `y` and `z`.

For the principal triple:

```text
x = (14,18)
y = (10,17)
z = (5,11)
```

The negative decision was independently reproduced by CaDiCaL and its DRAT proof was accepted by `drat-trim`. Six such triples were certified.

The construction goal remains to convert this ternary condition

```text
x => y or z
```

into a cofacial binary obstruction `X => e`, after which the standard Kelmans amplification would yield a non-Hamiltonian Barnette graph.

## Exact six-pole language correction

Three certified triples supplied six-terminal poles `A`, `B`, and `C`. Earlier composition work used positive underapproximations of their path-cover languages. This was not sufficient for a negative composition claim.

Every pole was therefore re-evaluated over the complete 75-state boundary space using a separate exhaustive perfect-matching recursion with closed-subtour pruning and a 100,000,000-call budget per state.

| Pole | Positive states | Exact negative states | Unknown |
|---|---:|---:|---:|
| A | 26 | 49 | 0 |
| B | 26 | 49 | 0 |
| C | 26 | 49 | 0 |

The exact result exposed one previously omitted positive state in pole `C`:

```text
mask = 63
pairing = (0,1)(2,5)(3,4)
```

All finite-state composition calculations were regenerated after this correction. The correction prevented a false language-zero interpretation of a Hamiltonian five-pole graph.

Exact-language result SHA-256:

```text
4c167dd746a9afb4ecee982fd989dc141d5b577df0921f3e503d478b1a856863
```

## Exact five-pole near-counterexamples

Using the corrected `AABCC` pole languages, 100,000 terminal permutations were screened for a fixed target glue condition `X+e-`.

- 9,818 had exact zero target language;
- 2,597 were legal and copy-connected;
- 122 were planar;
- 65 had `X` and `e` cofacial;
- every planar zero-language graph had vertex connectivity exactly two.

These 65 graphs satisfy the desired Hamiltonian trace obstruction at the exact pole-language level and fail the Barnette class only through a two-vertex separator.

## Separator-crossing C4 repair

One cofacial near-counterexample was selected:

```text
source index = 2
separator = (17,400)
component sizes = 99 and 399
X = (5,110)
e = (11,105)
```

The standard bipartite facial `C4` expansion was applied with correct directed face-edge orientation. An earlier generator that sorted edge endpoints was rejected because it did not preserve the required bipartite orientation.

The corrected generator produced 655 repairs. All 655 independently passed:

- simplicity;
- cubicity;
- bipartiteness;
- planarity;
- 3-connectivity.

Thus every repaired graph is a 504-vertex Barnette graph.

## Exact contraction strategy

The full 504-vertex problem was decomposed by the two graph edges replaced by the `C4` expansion.

Unmodified poles were contracted using their exact 26-state boundary languages. The resulting problem was reduced to a spanning path or augmented Hamiltonian-cycle search on the affected two- or three-pole supercomponent.

Positive decisions were retained only with explicit selected-edge witnesses.

## Complete repair result

| Affected region | Repairs | Result |
|---|---:|---|
| `C3-C4` internal edges | 359 | 359 positive |
| `B2-C4` internal edges | 126 | 126 positive |
| `A0-C4` internal edges | 52 | 52 positive |
| `A1-C4` internal edges | 87 | 87 positive |
| `C4` plus glue `B2-C3` | 14 | 14 positive |
| `C4` plus glue `A0-B2` | 14 | 14 positive |
| glue `A1-C3` plus `C4` | 3 | 3 positive |
| **Total** | **655** | **655 positive** |

### `C3-C4`

The three untouched poles allowed only seven state tuples, all inducing the same closure. Each repair reduced to one spanning-path problem on a 204-vertex supercomponent.

All 359 paths were explicitly witnessed and independently validated.

Result SHA-256:

```text
3ae1b9a35a08e8527eb86aa8d49c129b4014e572085e02064045acc399c81a5b
```

### `B2-C4`

Four exact outside closures were available. The simplest closure alone yielded an augmented Hamiltonian cycle for all 126 repairs through exhaustive complement-matching search.

Result SHA-256:

```text
59959cb6c466c1096ff58c635d7d1883c06ebc50ccbcc4b42f14b9c69ba3c7ca
```

### `A0-C4`

The outside state system induced one spanning-path closure. Five cases completed through exhaustive recursion; the other 47 produced explicit validated paths through an independent selected-edge flow MILP.

```text
exact prefix SHA-256:
05aea490f290d857962be8eb7802ac157c2bc91de0a22207592f8144f678f204

MILP remainder SHA-256:
1bd38d71cbcf5a4173319b9ec0f5a46a5cbf0512435622539c9192c5b73ee396
```

### `A1-C4`

Fourteen exact outside closures were tested exhaustively.

- 42 repairs were positive under six closures;
- 45 repairs were positive under nine closures;
- no repair was negative under every closure.

### Glue-edge classes

The final 31 repairs coupled three poles. Every class had four exact outside closures.

- all 14 `C4 + B2-C3` repairs were positive under at least one closure;
- all 14 `C4 + A0-B2` repairs were positive under at least one closure;
- all 3 `A1-C3 + C4` repairs were positive under at least one closure.

## Interpretation

This is a complete elimination of one separator geometry, not a failure of the ternary-obstruction program.

The significant facts are:

1. a proof-certified ternary Hamiltonian obstruction exists in a Barnette graph;
2. exact six-pole languages can produce planar cofacial `H+-` obstructions that fail only 3-connectivity;
3. a minimal separator-crossing `C4` repair can restore every Barnette predicate;
4. in the first fully analyzed family, every one of the 655 repairs also restores the forbidden Hamiltonian trace.

The first repair family therefore cannot disprove Barnette's conjecture.

## Next exact attack

The search now moves across the remaining 64 cofacial five-pole near-counterexamples.

For each graph:

1. enumerate every two-vertex separator;
2. generate correctly oriented separator-crossing `C4` repairs;
3. reject any graph failing a Barnette predicate;
4. contract untouched poles using the exact 26-state languages;
5. rank repair families by number of compatible outside closures;
6. solve the sparsest affected supercomponents first;
7. send any repair with no compatible closure to proof-producing whole-graph SAT;
8. if `H+-` is certified, apply Kelmans amplification and independently prove the resulting Barnette graph non-Hamiltonian.

No counterexample is claimed.
