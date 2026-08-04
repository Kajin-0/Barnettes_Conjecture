# Exact seam-language pilot and MILP correction

**Timestamp:** 2026-08-04 19:20 UTC  
**Counterexample found:** No

All 2,048 complement-normalized colorings of the original 12-vertex dual seam were classified for three leading closures by exhaustive perfect-matching-complement recursion.

```text
421_32_6: 118 positive, 1,930 exact negative
511_530_1: 127 positive, 1,921 exact negative
511_552_6: 127 positive, 1,921 exact negative
unknown: 0
```

A corrected independent dual-color/XOR MILP agrees with every positive-mask set exactly.

An earlier 112-positive result for `421_32_6` is retracted. The dual graph had noncontiguous labels, causing a color variable to overlap the first edge variable. The graph is now relabeled contiguously before variable allocation; contaminated output was deleted and recomputed. The defect affected only the new mask MILP.

The exact active semantic target is now the 118-mask language of `421_32_6`.

Evidence:

- `docs/EXACT_SEAM_LANGUAGE_PILOT_2026-08-04.md`
- `results/2026-08-04/exact_seam_language_pilot_summary.json`
