# Signature-directed deep multi-face leader

**Timestamp:** 2026-08-04 18:45 UTC  
**Counterexample found:** No  
**Classification:** complete positive classification

The 103 distinct hard-base disk classes were compared using an exact local two-tree boundary invariant.

For every binary coloring of a disk, each monochromatic induced subgraph was required to be a forest and every component was required to meet the boundary. A state records the boundary coloring and the connectivity partition induced on boundary vertices for both colors.

The smallest exact language belonged to disk class `421_32`:

```text
valid internal/boundary colorings = 1,304
boundary color masks = 309
exact forest signatures = 380
```

This class was therefore selected for a complete deeper second-face campaign rather than relying only on Hamiltonicity solver runtime.

## Complete second-face depth

Every degree-4, degree-6, and degree-8 dual vertex in base closure `421_32_6` was replaced by every parity-valid disk with at most four internal vertices under every dihedral boundary map.

```text
attempted replacements = 2,192
structurally valid = 1,530
exact duplicate labeled graphs removed = 475
distinct graph encodings = 1,055
```

By primal order:

```text
order 114 = 65
order 116 = 386
order 118 = 604
```

By replacement location:

```text
outside face = 792
seam-adjacent = 594
nested = 144
```

## Hamiltonicity classification

Four reproducible exact perfect-matching-complement branch orders were run with a 5,000-call budget each.

Their union produced explicit Hamiltonian cycles for 1,054/1,055 graphs. The only graph unresolved by all four portfolios was

```text
421_32_6__v17_B6_k4_310_1_outside_m10
```

An independent binary 2-factor MILP with iterative subtour cuts found and validated a Hamiltonian cycle in 16 rounds and 0.759 seconds.

Witness SHA-256:

```text
d88150a71f6654fd4aca563b9423fa5d5b9825878978abd55eb5faae29091ed6
```

Final result:

```text
Hamiltonian = 1,055
negative = 0
unknown = 0
invalid witnesses = 0
```

Evidence:

- `results/2026-08-04/signature_leader_deep_complete_summary.json`
- task SHA-256 `ada7111431e883dc6acf8593b9608387b3b1210048471e1f51eb3ef1e3e6de37`
