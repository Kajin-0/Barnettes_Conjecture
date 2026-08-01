# Perfect-Matching Reduction and Order-92 Q-State Campaign

**Date:** 2026-08-01  
**Status:** verified positive witnesses; no counterexample found

## Main reduction

Let `P` be one side of a natural cyclic 4-edge cut. Every internal vertex of `P` has degree three, while its four boundary terminals have degree two. In a two-path boundary state `Q`, internal vertices have selected degree two and terminals have selected degree one. Consequently every vertex is incident to exactly one omitted edge.

Therefore the omitted edges form a perfect matching `M`, and the selected two-path cover is exactly `P - M`. Conversely, a perfect matching complement realizes a requested `Q` state precisely when it has two connected components whose terminal pairs match that state.

This converts Q-state screening into randomized perfect-matching generation followed by a linear-time component and terminal-pairing test. The reduction is exact; only the randomized sampling is heuristic.

## Broad order-92 screen

The search used all eight retained canonical order-92 parent graphs and all 10,192 natural cyclic-4-cut sides. Up to 64 randomized perfect matchings were sampled per patch.

| Quantity | Result |
|---|---:|
| Natural cut-side patches | 10,192 |
| `Q01_23` witnessed | 3,661 |
| `Q03_12` witnessed | 2,546 |
| Both Q states witnessed | 2,357 |
| Exactly one witnessed | 1,493 |
| Zero sampled Q witnesses | 6,342 |
| Elapsed time | 23.62 s |

A sampled witness is conclusive after combinatorial validation. A zero-hit patch is not negative evidence; the matching distribution is nonuniform and the probability of sampling a particular boundary pairing decreases sharply with patch size.

## Deep matching escalation

The 200 hardest zero-hit patches were retested with up to 4,096 randomized perfect matchings each.

| Outcome | Patches |
|---|---:|
| Both Q states sampled | 13 |
| Exactly one Q state sampled | 116 |
| Still zero-hit | 71 |

The leading zero-hit case, `g6-c633-s0`, has 86 vertices. None of its 4,096 matching complements realized either target Q state, and its best sampled complement still had four components.

## Exact escalation of the entire zero-hit tail

All 71 remaining patches were then solved exactly for both noncrossing Q states.

| Quantity | Result |
|---|---:|
| Patches | 71 |
| Exact Q-state instances | 142 |
| Feasible | **142** |
| Independently validated witnesses | **142** |
| Invalid witnesses | **0** |
| Maximum patch order | 86 |
| Exact batch elapsed time | 16.80 s |

For every witness, an independent checker confirmed:

1. all selected edges belong to the patch;
2. no selected edge is duplicated;
3. exactly `|V(P)| - 2` edges are selected;
4. all four terminals have degree one;
5. every internal vertex has degree two;
6. there are exactly two connected components;
7. the components induce the requested terminal pairing.

The strongest sampler near-miss was not structurally restrictive:

- `g6-c633-s0`, `Q01_23`: exact witness in 0.655 s;
- `g6-c633-s0`, `Q03_12`: exact witness in 0.023 s.

## Interpretation

Perfect-matching complement rarity is a strong and inexpensive prioritization metric, but it is not a proximity measure to nonexistence. In this campaign the 71 hardest matching-sampler failures all admitted both target Q states under exact solution.

The reduction should remain in the higher-order pipeline as the first screening layer. Only the zero-hit extreme tail should be escalated to exact MILP and proof-producing SAT. The current number of independently certified missing noncrossing Q states remains zero.

## Evidence

- `search/matching_q_screen.py`
- `search/matching_q_deep.py`
- `results/2026-08-01/order92_matching_q_summary.json`
- `results/2026-08-01/order92_q_hardest71_validation.json`
- `results/2026-08-01/order92_q_strongest_near_miss_witnesses.json.gz.b64`

The full 142-witness local result had SHA-256:

```text
706496b3461df3deb580615cf656235da6b6e109af11a411820aa755a8a69b91
```

The repository includes the two exact witnesses for the strongest sampler near-miss. Reconstruct them with:

```bash
base64 --decode results/2026-08-01/order92_q_strongest_near_miss_witnesses.json.gz.b64 | gzip --decompress > order92_q_strongest_near_miss_witnesses.json
```

Expected uncompressed SHA-256:

```text
67174b4503c67aaac791be242fffb51641d4d72bd4e28283bbb6bcfcf4d961d7
```
