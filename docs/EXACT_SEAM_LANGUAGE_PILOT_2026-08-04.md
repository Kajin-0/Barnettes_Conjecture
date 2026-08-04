# Exact Original-Seam Boundary Languages

**Date:** 2026-08-04 UTC  
**Counterexample found:** No

## Objective

The one-face and minimal two-face campaigns show that graph order and solver hardness alone are weak obstruction metrics. The next invariant fixes the binary coloring of the original 12-vertex dual seam and asks whether the full substituted graph has a Hamiltonian cycle compatible with that coloring.

A complement-normalized 12-bit coloring gives 2,048 cases. Adjacent XOR values fix the selected/unselected status of the twelve corresponding primal seam edges.

## Independent exact formulation

For each coloring, the primal cubic graph is solved through exhaustive perfect-matching-complement recursion:

- a selected seam edge is forbidden from the complementary perfect matching;
- an unselected seam edge is forced into that perfect matching;
- recursion enumerates every compatible perfect matching;
- a positive requires the matching complement to be one connected spanning cycle;
- a negative is retained only after exhaustive completion with no budget exhaustion.

A corrected dual-color/XOR 2-factor MILP was run independently. MILP infeasibility is used only as a cross-check, not as proof.

## Exact result

| Base closure | Positive seam colorings | Exact negative | Unknown |
|---|---:|---:|---:|
| `421_32_6` | **118** | 1,930 | 0 |
| `511_530_1` | 127 | 1,921 | 0 |
| `511_552_6` | 127 | 1,921 | 0 |

For all three bases, the corrected MILP and exact recursion agree on the complete positive mask set, with symmetric difference zero. Every positive cycle witness passed independent validation.

The current exact boundary-language leader is therefore:

```text
421_32_6: 118 / 2,048 complement-normalized seam colorings
```

## Required correction

An initial MILP scan incorrectly reported 112 positive masks for `421_32_6`.

Root cause:

```text
the assembled dual retained a noncontiguous vertex-label gap;
one face-color variable index overlapped the first edge variable index.
```

The contaminated scans were deleted. The dual graph is now relabeled contiguously before variable allocation. The corrected MILP returns 118 positives and agrees mask-for-mask with the independent perfect-matching recursion.

This defect affected only the newly written boundary-mask MILP scans. It did not affect the earlier primal Hamiltonicity campaigns or their witnesses.

## Strategic consequence

The 118-mask language is an exact semantic target for multi-hole synthesis. A second embedded gadget need not suppress all Hamiltonian behavior abstractly; it needs to eliminate this finite set of 118 seam colorings while preserving even triangulation and dual 4-connectivity.

The next high-leverage experiment is to compute the exact joint relation between the original 12-seam and a selected second face, then synthesize a replacement whose boundary language has empty composition with that relation.

## Evidence

- `results/2026-08-04/exact_seam_language_pilot_summary.json`
- exact summary SHA-256 `576137ed9a47e7dc55630f45c8f0940052c1e1c93a65522b47e3e961884d01ab`
