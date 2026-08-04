# Uniform dual substitution through order 112

**Timestamp:** 2026-08-04 17:20 UTC  
**Counterexample found:** No

A single exact link-cycle generator replaced the earlier order-specific polygonal generators.

For a disk with `k` internal vertices, restoring the removed dual vertex gives an even sphere triangulation with `13+k` vertices. Proper three-coloring and rainbow-face counting imply

```text
E01 = E02 = E12 = 11 + k.
```

Thus the color-1/color-2 graph is the fixed 12-cycle plus `k-1` extra edges. Internal color-0 links are alternating cycles covering boundary edges once and extra edges twice. Candidate triangle complexes are accepted only when every edge has two incident triangles, every vertex link is one cycle, the complex is connected, and its Euler characteristic is two.

This formulation exhaustively generated every normalized color distribution for `k=1,...,7`. Every feasible disk was glued into candidate 489 under all 24 dihedral boundary maps, and only even 4-connected closures were retained.

Final totals:

```text
disk classes = 4,243
boundary maps = 101,832
valid closure constructions = 46,672
tested graph encodings = 46,109
Hamiltonian = 46,109
negative = 0
unknown = 0
invalid witnesses = 0
```

The 563-count difference consists of exact duplicate labeled graphs removed before solving.

Two earlier completeness claims were corrected:

- order 106: 44 disk classes and 568 closures, not 43 and 556;
- order 108: 206 disk classes, not 193 in the prior completed accounting.

Every newly added closure is Hamiltonian. No earlier positive witness was invalidated.

Evidence:

- `docs/UNIFORM_DUAL_SUBSTITUTION_THROUGH_ORDER112_2026-08-04.md`
- `results/2026-08-04/uniform_dual_substitution_k7_summary.json`
- `search/uniform_dual_cycle_disk_generator.py`
- updated `docs/CURRENT_STATE.md`

Hashes:

```text
generator  2caa76f131031df2c92e7877610d79ce89260bc05421594b9e96da2400766a99
summary    4596e3f3a7b7f9c760d110ee26ab3bf49f55ae0495cf7e1ad82cd24548caf19b
archive    d9a0686c6405478878ddf462f0f559db3caa745c7c4ccee0d1151ee677c5ad40
```

Strategic consequence: a counterexample in this candidate-489 one-face substitution family requires at least eight inserted vertices, giving primal order at least 114. The primary next route shifts to exact boundary-language optimization and embedded multi-face composition rather than blind disk-order growth.
