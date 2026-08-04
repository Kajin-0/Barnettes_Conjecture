# Boundary-directed degree-4 and degree-6 campaign

**Timestamp:** 2026-08-04 20:00 UTC  
**Counterexample found:** No

A two-seam indexing error was corrected: a vertex replacement exposes the neighbor link cycle, so the second seam consists of link-cycle edges, not radial edges incident with the removed vertex. The contaminated radial relations were retracted before synthesis.

Correct exact relations for base `421_32_6`:

```text
degree-4 face: 780 positive pairs, 1,108 exact negative, 0 unknown
degree-6 face: 1,020 positive pairs, 6,532 exact negative, 0 unknown
```

All 65 parity-valid degree-4 disks through `k=8` have exactly the same six-state forest-partition language. This explains the failure of undirected degree-4 growth.

Targeted closure result:

```text
degree-4 k=5..8 tested = 200, Hamiltonian = 200
degree-6 k=5..7 tested = 584, Hamiltonian = 584
aggregate = 784/784 positive
```

The next active interface is degree 8, where disk languages vary substantially.

Evidence:

- `docs/BOUNDARY_DIRECTED_DEGREE4_DEGREE6_2026-08-04.md`
- `results/2026-08-04/boundary_directed_degree4_degree6_summary.json`
