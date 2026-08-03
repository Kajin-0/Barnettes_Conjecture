# Annular Swap Relation and Semigroup Checkpoint

**Date:** 2026-08-03  
**Status:** provenance-incomplete checkpoint reconstructed from authoritative PR #1 body  
**Counterexample found:** no

## Why this file exists

The authoritative PR body contained an exact annular-transfer result that was not represented by a dedicated tracked report or machine-readable result file. This checkpoint preserves the claim and its strategic consequence while explicitly marking the missing underlying provenance.

This file is not a substitute for the original raw scan, exact enumerator output, or semigroup calculation. Those artifacts must be recovered or reproduced before this checkpoint is treated as independently verified evidence.

## Reported order-100 scan

A 300-annulus order-100 scan reportedly found six cardinality-two `Q -> Q` blocks.

The six blocks were identified as three 8-cycle rings viewed in both directions.

Their exact two-state relation was:

```text
Q01_23 -> Q03_12
Q03_12 -> Q01_23
```

The diagonal transitions were exactly impossible:

```text
Q01_23 -> Q01_23
Q03_12 -> Q03_12
```

The reported structural explanation was:

1. degree constraints on the 8-cycle ring leave its two alternating perfect matchings;
2. off-diagonal boundary pairing joins the selected structure into one spanning cycle;
3. diagonal boundary pairing produces two disjoint cycles;
4. therefore the `Q -> Q` block is a swap permutation, not a restrictive annihilator.

## Full six-state relation

The full exact six-state transfer relation reportedly had:

| Power | Transition count |
|---|---:|
| `R` | 14 |
| `R^2` | 28 |
| `R^3` | 36 |

Thus the third power reaches the complete `6 x 6` transition domain.

Interpretation:

```text
Repeated composition of the exact ring increases boundary flexibility.
```

The ring therefore cannot produce an empty transfer product through repetition.

## Broader Boolean semigroup

Across the broader annular relation set, the PR body reported:

- 14 distinct positively witnessed relation patterns;
- 834 relations in the Boolean semigroup closure;
- stabilization by composition depth six;
- no empty product;
- minimum generated relation cardinality 13;
- some products equal to the complete 36-transition relation.

This eliminates the tested natural-annulus semigroup as an immediate non-Hamiltonicity construction route.

## Strategic consequence

The exact 8-cycle ring is mathematically informative because it proves that sparse annular marginals can encode nontrivial correlations. However, its relation is bijective and its powers become more permissive.

The remaining high-value annular target is therefore narrower:

```text
Find an exact Q block with:
- zero transitions;
- one transition; or
- two transitions that are not bijective and therefore contain a zero row or column.
```

This annular search remains secondary to the certified ternary-obstruction connectivity-repair program, where a single negative repair could directly produce a cofacial `H^{+-}` obstruction.

## Provenance gap

At this checkpoint, the following were not located as dedicated tracked artifacts:

- the original 300-annulus scan output;
- identifiers for the six cardinality-two annuli;
- the exact 8-cycle enumeration output;
- the 14-transition full relation;
- the relation powers;
- the 834-element semigroup closure output;
- commands, software versions, elapsed times, and file hashes.

The claims above were recovered from the authoritative PR #1 body. They must not be silently upgraded to independently verified repository evidence.

## Required recovery action

1. Search auxiliary branches and workflow artifacts for the original files.
2. If absent, reconstruct the relevant order-100 parent and three 8-cycle annuli.
3. Re-run exact relation completion.
4. Re-run Boolean semigroup closure.
5. Publish the full result, commands, software versions, and SHA-256 manifest.
6. Update `docs/CURRENT_STATE.md` and this report with the recovered evidence paths.

## Machine-readable checkpoint

```text
results/2026-08-03/annular_swap_semigroup_checkpoint.json
```
