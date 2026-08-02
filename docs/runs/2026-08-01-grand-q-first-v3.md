# Grand Q-First and Transfer Campaign v3

**Date:** 2026-08-01  
**Status:** active specification  
**Counterexample found at campaign start:** no

## Objective

Make a substantially broader, proof-oriented search for a Barnette counterexample by combining:

1. complete natural cyclic-4-cut `Q`-state coverage in a broader set of high-ranked order-96 and order-100 graphs;
2. repaired canonical sampling at the unresolved orders 94 and 98;
3. immediate proof-producing SAT escalation for every nonpositive state;
4. preservation of all witnesses, proof attempts, manifests, and partial generation output.

The primary certified progress metric remains:

```text
number of independently certified missing noncrossing Q states
```

The value at campaign start is zero.

## Motivation

The collision-safe v2 campaign produced independently validated positive witnesses for all 7,680 tested `Q` states at orders 96 and 100. The tested set covered only 3,840 of 17,732 natural cut-side patches available in twelve selected parent graphs.

Orders 94 and 98 were not analyzed because sparse `RES/10000` plantri classes produced no flushed graph6 record before their per-class wall-clock limits. Those failures were computational and have no mathematical interpretation.

The v3 campaign therefore broadens verified coverage while repairing the unresolved generator regime.

## State model

For every selected natural cyclic-4-cut side, test the two planar noncrossing two-path states first:

```text
Q01_23
Q03_12
```

A positive state is accepted only with an explicit selected-edge witness that independently verifies:

1. all selected edges belong to the patch;
2. no selected edge is duplicated;
3. every exposed terminal has selected degree one;
4. every internal patch vertex has selected degree two;
5. the selected subgraph has exactly two connected components;
6. the components induce the requested terminal pairing;
7. the selected edge count is `|V(P)| - 2`.

A MILP infeasibility status remains provisional. A final missing-state claim requires a CaDiCaL UNSAT proof accepted independently by `drat-trim`. Timeouts, interrupted runs, malformed cases, invalid witnesses, proof-generation failures, and proof-check failures remain `unknown`.

## Track A — complete broad coverage at orders 96 and 100

For each order:

- generate twelve distributed plantri `RES/10000` classes;
- retain up to 400 graph6 records per class;
- deduplicate the sample;
- validate graph order, cubicity, bipartiteness, connectivity, and planarity;
- apply the implemented sufficient-condition filters;
- rank survivors with 256 perfect-matching-complement trials per graph, used only as a heuristic;
- retain the twelve leading parent graphs;
- enumerate every natural cyclic 4-edge cut in every retained parent;
- test both noncrossing `Q` states for every cut side;
- retry every nonpositive state at a longer exact budget;
- pass every remaining nonpositive state to independent SAT and proof checking.

The patch limit is set above any expected number of cut sides so selection does not truncate the parent graphs.

Expected scale from the v2 counts is approximately:

```text
30,000–40,000 Q-state attempts per order
```

## Track B — repaired order-94 and order-98 canonical shards

Use lower-modulus, independent plantri classes:

```text
RES/64
```

with residues:

```text
0, 7, 15, 23, 31, 39, 47, 55
```

for each of orders 94 and 98.

Each class runs as a separate CI matrix job. This prevents one slow class from serially consuming the complete order budget and preserves independent partial results.

The workflow patches the official plantri 5.8 output routine at build time to call:

```c
fflush(outfile);
```

after every graph. The patch changes output buffering only; it does not change graph generation, canonical rejection, or class membership. Both the original archive hash and the patched-source hash are recorded.

Each class:

- uses the `-X` split-depth option;
- retains at most 160 graph6 outputs;
- has a bounded generation budget;
- preserves partial graph6 output even when the generator reaches its wall-clock limit;
- treats zero-output classes as `unknown_generation`, not workflow failure or mathematical evidence;
- ranks up to two surviving parent graphs;
- tests every natural cut side in those parents;
- independently verifies every nonpositive state through SAT and proof checking.

The sixteen class jobs sample one eighth of the residue classes at each unresolved order.

## Generator provenance

Official plantri 5.8 archive:

```text
SHA-256:
e78a944116fec9f2c9f5e484206276cc2b0043bae803e9815f4b2683614629b8
```

Broad-track command form:

```text
plantri -bc4dg ORDERd RES/10000
```

Hard-order command form:

```text
plantri-flush -X -bc4dg ORDERd RES/64
```

All commands, hashes, counts, termination statuses, and partial outputs are written to artifact manifests.

## Software and proof toolchain

- Python 3.12;
- NetworkX 3.6.1;
- NumPy 2.x;
- SciPy 1.18.0;
- python-sat 1.9.dev5;
- official plantri 5.8;
- CaDiCaL built from a recorded public commit;
- drat-trim built from a recorded public commit.

## Expected outputs

Broad jobs:

```text
results/grand-q-first-v3/broad/ORDER/
```

Hard-order shard jobs:

```text
results/grand-q-first-v3/hard/ORDER/residue-RES/
```

Every artifact should contain, as applicable:

- raw and deduplicated graph6 data;
- plantri standard error and termination status;
- theorem-filter and ranking records;
- exact positive witnesses;
- provisional negative and unknown cases;
- SAT instances and solver results;
- checked proof logs for any certified negative;
- software versions and source commits;
- file-level SHA-256 manifest;
- concise order or shard summary.

## Escalation criteria

Immediately checkpoint and redirect compute when any of the following occurs:

- a proof-checked missing noncrossing `Q` state is found;
- a positive witness fails independent validation;
- MILP and SAT disagree;
- an empty independently verified transfer product is found;
- an assembled graph passes all Barnette predicates and has proof-checked non-Hamiltonicity;
- a new solver-version discrepancy appears;
- a generator class systematically produces no output under the repaired regime.

A proof-certified missing `Q` state triggers completion of the patch’s entire boundary signature and a targeted composition search before broader enumeration resumes.

## Interpretation limits

This campaign is not an exhaustive enumeration by order. Canonical classes are sampled and high-ranked parent graphs are prioritized. Failure to find a missing state does not imply universal local flexibility or prove Barnette’s conjecture.

The campaign is designed to produce either:

- a proof-certified restrictive local object suitable for composition;
- a much stronger empirical basis for abandoning marginal four-terminal obstruction searches in favor of multi-interface transfer correlations.

## Repository operation

The agent owns all workflow dispatch, CI inspection, failure correction, artifact retrieval, evidence publication, research-log updates, handoff updates, and PR maintenance. No routine action is assigned to the repository owner.
