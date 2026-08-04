# Degree-8 Semantic Descent

**Date:** 2026-08-04 UTC  
**Counterexample found:** No

## Main result

A geometry-aware degree-8 replacement strategy produced two successive exact contractions of the original 12-seam Hamiltonian language:

```text
421_32_6                      118 positive masks
first disjoint B8 replacement 111 positive masks
second disjoint B8 replacement 75 positive masks
```

Each language was classified over all 2,048 complement-normalized boundary colorings by exhaustive perfect-matching-complement recursion. No run reached its 100,000,000-call budget. Every positive witness was independently checked.

The contractions are not set inclusions. The replacements remove many previous masks and introduce different masks. The objective is therefore exact language cardinality and compositional structure, not a monotone subset chain.

## First descent: 118 to 111

```text
base = 421_32_6
target dual vertex = 2, outside the original seam
boundary degree = 8
disk = B8 k=3, distribution 300, class 0
dihedral map = 3
primal order = 116
positive seam masks = 111
exact negative masks = 1,937
unknown = 0
```

The complete B8 k=2..4 family at this face contained 95 exact graph encodings; the complete k=5 class contained 241. All 336 graphs have validated Hamiltonian cycles. Multiple k=3 and k=5 constructions produce exactly the same 111-mask seam set.

## Second descent: 111 to 75

The 111-mask source was ranked over its remaining degree-8 faces. A face sharing a vertex with the original seam was rejected as a fixed-seam target. The best disjoint face was relabeled vertex 23.

```text
exact joint queries = 28,416
positive pairs = 578
exact negative pairs = 27,838
unknown = 0
```

```text
base = 421_32_6__v2_B8_k3_300_0_m3
target relabeled dual vertex = 23
target disjoint from original seam
disk = B8 k=3, distribution 300, class 0
dihedral map = 5
primal order = 120
positive seam masks = 75
exact negative masks = 1,973
unknown = 0
```

The complete geometry-filtered degree-8 k=2..6 family at this second face contained 1,136 exact graph encodings across primal orders 118 through 126. All 1,136 are Hamiltonian.

## Structural correction

Relabeled vertex 14 initially appeared to have the narrowest witness relation, but it is itself on the original 12-seam. Replacing it destroys the boundary whose language was being optimized. Its relation is retained only as an overlapping-boundary relation and was not used in the fixed-seam descent.

## Interpretation

This is the first repeated exact semantic descent in the project. It does not produce a counterexample because both whole graphs remain Hamiltonian. It shows that embedded multi-face replacements can reduce the source language far more sharply than one-face order growth.

The next target is a third disjoint degree-8 replacement from the 75-mask source. If the cardinality descent stalls, the search moves from mask projection to the exact two-boundary forest-partition relation.
