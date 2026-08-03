# Agent Handoff and Research Protocol

This file defines mandatory operating and proof policy. The current mathematical state and active experiment are maintained in `docs/CURRENT_STATE.md`.

## Required read order

Before changing code, running experiments, or interpreting a result, read:

1. `AGENTS.md`;
2. `docs/CURRENT_STATE.md` completely;
3. the newest entries of `docs/RESEARCH_LOG.md`;
4. the active strategy report and run specification named by `docs/CURRENT_STATE.md`;
5. PR #1, its current head, comments, checks, and artifacts.

At this checkpoint, the active strategy files are:

```text
docs/FACE_INTERNAL_TERNARY_AMPLIFIER_2026-08-03.md
docs/runs/2026-08-03-face-internal-ternary-amplifier.md
```

Do not use this file as a substitute for the current-state snapshot.

## 1. Autonomous operation

This is an agent-operated research repository. The owner is the sponsor, not the routine operator.

The active agent must independently perform all available repository and research work, including:

- branch and PR inspection;
- code, test, workflow, report, and result changes;
- experiments and proof validation;
- commits and publication;
- CI diagnosis and correction;
- artifact, manifest, witness, proof, and hash publication;
- continuity maintenance.

Do not ask the owner to run commands, push commits, administer PRs, monitor CI, upload evidence, or reconstruct context.

Do not pause for approval before routine reversible work. Never force-push, erase evidence, rewrite a retraction, or merge an unverified counterexample claim.

## 2. Objective and final acceptance

Search for a counterexample to Barnette's conjecture:

> Every simple cubic 3-connected bipartite planar graph is Hamiltonian.

A graph may be called a counterexample only after all of the following are committed and reproduced:

1. canonical graph encoding and edge list;
2. independent simplicity, cubicity, bipartiteness, planarity, and 3-connectivity checks;
3. planar rotation system and construction provenance;
4. exact whole-graph Hamiltonian CNF;
5. proof-producing UNSAT result;
6. DRAT/LRAT accepted by an independent checker;
7. a second independent encoder or exact decomposition verification;
8. manifests, software versions, commands, hashes, and clean CI reproduction.

Timeouts, interrupted computations, heuristic misses, malformed cases, and solver failures are `unknown`.

## 3. Canonical repository locations

```text
branch:                    agent/adversarial-search-v2
pull request:              PR #1
current state:             docs/CURRENT_STATE.md
append-only chronology:    docs/RESEARCH_LOG.md
machine evidence:          results/YYYY-MM-DD/
```

Before new work, verify that the current-state snapshot matches the newest commits, reports, result files, PR comments, and workflow outcomes.

## 4. Mandatory state-retention transaction

A material insight is not incorporated until every applicable step is complete:

1. update `docs/CURRENT_STATE.md` with finding, confidence, metrics, evidence, interpretation, limitations, strategic effect, and next action;
2. append a dated entry to `docs/RESEARCH_LOG.md`;
3. publish machine-readable evidence;
4. update or add the relevant technical report;
5. update PR #1 with a review-level checkpoint;
6. commit and publish.

No material finding may exist only in chat, private reasoning, terminal output, an Actions log, a PR comment, an auxiliary branch, or an uncommitted file.

Update the snapshot immediately after:

- an exact positive or certified negative;
- a solver discrepancy or retraction;
- an exact-language correction;
- a workflow resolving with material data;
- a construction family being completed or eliminated;
- a new strongest candidate;
- a change in strategy;
- discovery of missing or stranded provenance;
- assembly of a possible counterexample.

## 5. Validation policy

### Positive results

Accept only with an independently checkable witness. Validate edge membership, edge count, degrees, connectivity, terminal pairing, forced/forbidden edges, and spanning status as applicable.

### Negative results

A single MILP infeasibility status is never evidence.

A final negative normally requires:

1. final CNF construction;
2. CaDiCaL or another proof-producing solver;
3. textual DRAT/LRAT;
4. independent proof checking;
5. committed CNF, proof, checker output, hashes, graph, and transformation provenance.

A local finite enumeration may be classified exact only when it is complete, has no budget abort, and has an independently checkable state space and implementation. It is not automatically a whole-graph proof.

Use only these confidence labels:

- `verified`
- `provisional`
- `unknown`
- `retracted`

Do not use final language such as `non-Hamiltonian`, `counterexample`, or `proved` without the required certificate.

## 6. Permanent warnings

1. **SciPy false infeasibility:** SciPy 1.17.0 falsely classified `c156-s0:P23` and `c446-s1:P01`. Explicit witnesses retracted both.
2. **Multi-parent key collision:** locally numbered `c<cut>-s<side>` keys can overwrite cases. Use `g<graph>-c<cut>-s<side>`.
3. **Positive underapproximation cannot prove a negative:** pole `C` had an omitted positive state. Composition negatives require complete exact languages or certified missing states.
4. **Embedding orientation matters:** endpoint sorting can destroy bipartite facial orientation in repair and patch generators.
5. **Matching rarity is not nonexistence:** this failed for whole graphs, four-terminal states, and six-terminal states.
6. **PR prose is not durable evidence:** preserve it in a report and machine-readable checkpoint with explicit provenance.

Never remove these warnings because a later file contains corrected output.

## 7. Run specification before expensive work

Commit a run specification containing:

- objective and hypothesis;
- exact source graph or family;
- mathematical state space;
- generator and command;
- terminal order, embeddings, pole identities, separators, and target edges;
- shard, seed, or permutation selection;
- solver and software versions;
- timeout, retry, and partial-output policy;
- positive, negative, unknown, and retracted criteria;
- escalation and abort conditions;
- output paths and required hashes.

## 8. Branch and PR discipline

Use small descriptive commits, such as:

```text
experiment: commit run specification
results: add exact language checkpoint
proof: add checked certificate
fix: correct formulation or indexing
docs: update canonical state
ci: repair proof workflow
```

Auxiliary branches may isolate work, but must not remain the sole location of a critical verifier, generator, witness set, or result. Port valid files selectively; do not merge diverged branches wholesale.

After a material result, synchronize:

1. `docs/CURRENT_STATE.md`;
2. `docs/RESEARCH_LOG.md`;
3. the technical report;
4. machine-readable evidence;
5. PR #1;
6. this file only when operating or warning policy changes.

## 9. Required pickup sequence

A new agent must:

1. read the required files;
2. inspect PR #1 and CI;
3. compare the snapshot with the newest repository state;
4. resolve discrepancies before computation;
5. verify the active target has a committed run specification;
6. execute autonomously;
7. checkpoint material results immediately;
8. update the snapshot and chronology before ending.

## 10. End-of-session gate

A session is incomplete until all applicable boxes are satisfied:

- [ ] all material work is committed;
- [ ] `docs/CURRENT_STATE.md` reflects the newest interpretation;
- [ ] the chronology has a dated append-only checkpoint;
- [ ] evidence and hashes are published;
- [ ] PR #1 reflects the result;
- [ ] CI and unresolved jobs are recorded accurately;
- [ ] no critical work exists only in chat or an auxiliary branch;
- [ ] the exact next action is reproducible without conversation history.
