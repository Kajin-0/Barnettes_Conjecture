# Agent Handoff and Research Protocol

This file is the authoritative operational handoff for any agent continuing work in this repository.

Read this file before running experiments, changing search logic, interpreting solver output, or making mathematical claims.

## 1. Project objective

Search computationally for a counterexample to Barnette's conjecture:

> Every cubic, 3-connected, bipartite planar graph is Hamiltonian.

The project must remain reproducible and proof-oriented. A graph is not a counterexample unless:

1. all Barnette-class predicates are independently verified;
2. non-Hamiltonicity is established exactly;
3. the negative result has a machine-checkable certificate or independently checked proof log;
4. all source graphs, parameters, software versions, hashes, and transformations are recorded in the repository.

Timeouts, solver failures, and heuristic misses are always **unknown**, never negative evidence.

## 2. Current repository state

Active research branch:

```text
agent/adversarial-search-v2
```

Active draft pull request:

```text
PR #1: Canonical Barnette search: all tested cyclic-cut patches maximal at order 92
```

Primary technical report:

```text
docs/CANONICAL_STRUCTURAL_SEARCH_2026-08-01.md
```

Chronological checkpoint log:

```text
docs/RESEARCH_LOG.md
```

Machine-readable results:

```text
results/2026-08-01/
```

Reproducible workflow:

```text
.github/workflows/canonical-barnette-search.yml
```

## 3. Current validated findings

No counterexample has been found.

Canonical order-92 campaign:

- official plantri 5.8 archive;
- archive SHA-256: `e78a944116fec9f2c9f5e484206276cc2b0043bae803e9815f4b2683614629b8`;
- generation form: `plantri -bc4dg 92d RES/10000`;
- 8 disjoint shards;
- 300 canonical graph6 outputs retained per shard;
- 2,400 non-isomorphic 92-vertex graphs sampled;
- 2,342 graphs escaped the implemented face-based sufficient-condition filters;
- 8 matching-fragmentation leaders retained.

Exact natural cyclic-4-cut analysis of the leading retained graph:

- 647 cyclic 4-edge cuts;
- 1,294 cut-side four-terminal patches;
- 1,294 complete signatures;
- 1,294 maximal six-state signatures;
- 0 certified restrictive patches;
- 0 unresolved signatures;
- 1,283,456 planar bipartition-preserving patch-map comparisons;
- all 1,283,456 comparisons had six compatible state pairs;
- 0 incompatible patch maps.

Other validated positive findings:

- all 138 adjacent-edge-deletion four-poles had maximal six-state signatures;
- 200 conservative annular transfer relations were tested;
- each relation had 26 positively witnessed entries;
- 12 labelled relation patterns occurred;
- no tested pair product was empty;
- the smallest witnessed pair product had 43 entries.

Clean reproduction record:

- GitHub Actions workflow run ID: `30699671554`;
- uploaded artifact SHA-256: `fd22be4b51b1d950391f8349697d5842e59b5b58f60b246aef9d08a57f5d104d`;
- verified solver environment: SciPy 1.18.0.

This was a distributed canonical sample. It was not an exhaustive enumeration of all order-92 Barnette graphs and was not a statistically uniform random sample.

## 4. Critical retraction and solver policy

An earlier local SciPy 1.17.0 run reported two apparent missing path states:

- `c156-s0`, state `P23`;
- `c446-s1`, state `P01`.

Those claims were false. A clean SciPy 1.18.0 run generated explicit valid spanning-path witnesses for both states. The earlier restrictive-patch certificates were deleted and the discrepancy was recorded in:

```text
results/2026-08-01/solver_discrepancy_retraction.json
```

Mandatory interpretation rules:

- A positive state is accepted only with an independently checkable selected-edge witness.
- A single MILP solver's infeasibility status is never mathematical evidence.
- Every apparent missing state is provisional until independently reproduced with a different formulation.
- A retained negative state ultimately requires a checked proof-producing SAT result, such as DRAT or LRAT.
- Timeouts and interrupted solves remain unknown.
- Retracted findings must remain documented; do not silently delete the history of the error.

## 5. Boundary-state model

For four terminals `0,1,2,3`, the nominal state labels are:

```text
P01 P02 P03 P12 P13 P23
Q01_23 Q02_13 Q03_12
```

For a planar bipartite four-terminal patch, bipartition parity and planar noncrossing constraints leave six structurally possible states: four `P` states and two `Q` states. A six-state signature is maximal relative to those constraints.

The highest-value local obstruction is a proof-certified missing noncrossing `Q` state, not merely a missing `P` state.

Current primary progress metric:

```text
number of independently certified missing noncrossing Q states = 0
```

## 6. Strongest next experiment

Continue with a higher-order, Q-first, proof-producing search.

Target orders:

```text
94, 96, 98, 100
```

Recommended sequence:

1. Generate distributed canonical plantri shards.
2. Record the exact plantri command, archive hash, shard residues, limits, and graph counts before analysis.
3. Verify cubicity, bipartiteness, planarity, connectivity, and cyclic connectivity independently.
4. Apply valid theorem-based sufficient-condition filters.
5. Rank the surviving graphs using heuristic matching-fragmentation metrics only as prioritization signals.
6. Enumerate natural cyclic 4-edge-cut sides.
7. Solve the two noncrossing `Q` states first.
8. Validate every positive result through an explicit selected-edge witness checker.
9. Treat every apparent negative as provisional.
10. Re-encode provisional negatives using an independent SAT formulation.
11. Retain a restrictive patch only after checking an UNSAT proof.
12. Construct annular transfer relations from verified decisions.
13. Search the Boolean transfer semigroup for an empty product.
14. If a full graph is assembled, revalidate all Barnette predicates and prove whole-graph non-Hamiltonicity independently.

Do not spend substantial compute solving all path states for patches that already realize both noncrossing `Q` states unless those path states are required for a specific transfer calculation.

## 7. Mandatory repository checkpoint protocol

No important result may exist only in chat history, local scratch files, terminal output, or an uncommitted workspace.

### Before a long or expensive experiment

Commit or update a run specification containing:

- objective;
- hypothesis;
- graph order and class;
- generator and exact command;
- shard or seed selection;
- software and solver versions;
- timeout and retry policy;
- expected output paths;
- acceptance and rejection criteria.

### After every meaningful phase

Create a repository checkpoint after any of the following:

- canonical generation completes;
- filtering completes;
- a new extreme candidate is identified;
- an exact signature batch completes;
- an apparent negative state appears;
- an independent confirmation succeeds or fails;
- a solver discrepancy is detected;
- a certificate or witness is generated;
- a composition search completes;
- the analytical direction changes;
- an experiment is terminated because the formulation is inefficient or unsound.

Each checkpoint must include, as applicable:

- machine-readable output;
- a concise Markdown interpretation;
- exact counts and metrics;
- input hashes;
- command-line arguments;
- environment versions;
- elapsed time or computational budget;
- known limitations;
- classification as `verified`, `provisional`, `unknown`, or `retracted`;
- the next recommended action.

### Required files to keep synchronized

After a material result, update:

1. `docs/RESEARCH_LOG.md` with an append-only dated entry;
2. the current technical report or a new dated report;
3. machine-readable files under `results/YYYY-MM-DD/`;
4. this `AGENTS.md` file if the validated state, warning set, or next experiment changes;
5. the active PR description or a PR comment when the result changes the review-level interpretation.

### Commit discipline

Use small, descriptive commits. Prefer one coherent research checkpoint per commit or short sequence of commits.

Recommended prefixes:

```text
experiment: record generation checkpoint
results: add exact cyclic-cut signatures
proof: add independently checked witness
fix: correct boundary-state formulation
docs: retract solver-dependent claim
ci: pin verified solver environment
```

Never overwrite a prior result in a way that obscures a retraction. Preserve the old claim in the chronological log and add an explicit correction.

## 8. Result confidence levels

Use these exact labels in reports and machine-readable summaries:

### `verified`

Directly checkable positive witness, independently reproduced computation, or checked proof certificate.

### `provisional`

Potentially important result from one formulation or solver, awaiting independent confirmation.

### `unknown`

Timeout, interrupted solve, numerical failure, malformed case, resource exhaustion, or insufficient evidence.

### `retracted`

Previously reported result contradicted by a valid witness, stronger computation, or identified implementation error.

Do not use `infeasible`, `non-Hamiltonian`, `counterexample`, or `proved` in a final interpretation unless the required independent certificate exists.

## 9. Reproduction baseline

Install the pinned environment:

```bash
python -m pip install -r requirements.txt
```

Unpack source files when needed:

```bash
python source/unpack_sources.py
```

The GitHub Actions workflow downloads and hashes official plantri 5.8, compiles it, generates canonical order-92 shards, ranks candidates, solves cyclic-cut boundary signatures, records a manifest, and uploads the output artifact.

Before extending the workflow to higher orders, preserve the order-92 job as a regression test or retain equivalent fixed regression cases for:

- maximal six-state patch recognition;
- timeout-to-unknown behavior;
- witness validation;
- the two formerly misclassified states;
- manifest and hash generation.

## 10. Immediate pickup checklist

A new agent should:

1. Read this file.
2. Read `README.md`.
3. Read `docs/CANONICAL_STRUCTURAL_SEARCH_2026-08-01.md`.
4. Read `docs/RESEARCH_LOG.md` from the most recent entry backward.
5. Inspect PR #1 and its latest checks.
6. Confirm the working branch and uncommitted state before changing files.
7. Reproduce or inspect the order-92 regression before altering solver logic.
8. Begin the next experiment from a committed run specification.
9. Checkpoint all important findings immediately.

## 11. Current stopping point

The order-92 natural one-interface route has produced no restrictive patch. Ordinary cyclic-4-cut sides of the leading graph are maximally Hamiltonian-flexible. The next rational search is higher-order and `Q`-first, with proof-producing confirmation for every apparent missing state.

Do not restart the superseded adjacent-vertex-deletion or unrestricted all-state-first searches without a specific new theoretical reason.