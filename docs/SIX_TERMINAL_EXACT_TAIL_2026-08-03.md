# Exact Six-Terminal Tail and Common Compatibility Kernel

**Date:** 2026-08-03  
**Status:** exact enumeration on the strongest pilot near-misses  
**Counterexample found:** no

## Objective

Determine whether the six-terminal cyclic-cut pilot's zero-hit patches are genuinely sparse Hamiltonian interfaces capable of incompatible planar gluing.

The pilot had sampled 4,594 cut-side patches and produced 106 patches with zero observed states. It also produced many zero observed-compatibility maps. Those were explicitly provisional because randomized perfect-matching sampling can miss rare states.

## Exact method

For each selected zero-hit patch and every bipartite-parity-feasible exposed-terminal set:

1. enumerate every perfect matching of the remaining bipartite patch;
2. take the complement of the matching;
3. compute its spanning path components;
4. retain the induced six-terminal boundary state only after exact degree, component-count, and terminal-pairing validation;
5. compare complete signatures under all twelve dihedral boundary maps.

This is finite exhaustive enumeration. No solver infeasibility status is used.

## Result

Nine of the smallest and strongest zero-hit patches were completed exactly.

| Patch | Order | Perfect matchings enumerated | Exact states |
|---|---:|---:|---:|
| `g5-c111-s0` | 44 | 58,556 | 23 |
| `g5-c78-s0` | 44 | 56,230 | 24 |
| `g5-c246-s0` | 46 | 87,521 | 24 |
| `g5-c80-s0` | 46 | 90,649 | 24 |
| `g1-c140-s0` | 48 | 144,261 | 23 |
| `g1-c82-s0` | 48 | 137,706 | 24 |
| `g5-c179-s0` | 48 | 146,816 | 24 |
| `g1-c174-s0` | 50 | 233,064 | 24 |
| `g2-c140-s0` | 50 | 240,078 | 23 |

Thus every sampled zero was a severe false negative. The exact signatures contain 23 or 24 of the 50 nominal planar path-cover states.

Across all 540 exact patch-pair/dihedral-map comparisons:

```text
minimum compatibility = 9
zero compatibility = 0
```

## Common nine-state kernel

All nine exact signatures contain the following states:

```text
U012345_01_23_45
U012345_05_12_34
U0123_01_23
U0123_03_12
U0145_01_45
U01_01
U2345_23_45
U23_23
U45_45
```

This common kernel explains the observed compatibility floor. Under the sparsest tested alignment, exactly nine compatible Hamiltonian traces remain.

The kernel is an empirical exact result for these nine patches, not a theorem for every cyclic six-cut patch. It does show that randomized matching rarity is not a reliable distance-to-obstruction metric at six terminals, just as it was not reliable for four-terminal Q states.

## Interpretation

The six-terminal pilot did not locate a counterexample mechanism. Its strongest apparent zero signatures are highly flexible under exact completion.

The appropriate pivot is not to increase the number of matching samples. A useful six-terminal search must optimize an exact property capable of destroying the common kernel—for example:

- forced-in/forced-out facial constraints;
- exact absence of one of the nine kernel states;
- annular transfer relations rather than one-boundary disk signatures;
- proof-oriented synthesis from the certified ternary `H^{+--}` poles.

The immediate constructive priority remains the source-57 one-closure repair family, because a negative there would already be a global cofacial `H^{+-}` obstruction.

## Evidence

Machine-readable summary:

```text
results/2026-08-03/six_terminal_exact_tail_summary.json
```

Summary SHA-256:

```text
5a83c3b453b81be1e4327d7dd94f00918f43eb3c267aad69f18f034833fc3689
```

No counterexample is claimed.
