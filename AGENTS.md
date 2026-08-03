# Agent Handoff and Research Protocol

This file defines the mandatory operating protocol for every agent continuing work in this repository.

## Read order

Before running experiments, changing search logic, interpreting solver output, or making mathematical claims, read:

1. `AGENTS.md` — operating and validation rules;
2. `docs/CURRENT_STATE.md` — single canonical mutable snapshot of the current research state;
3. the newest entries in `docs/RESEARCH_LOG.md` — append-only chronology;
4. PR #1, its latest commit, comments, and workflow state.

`docs/CURRENT_STATE.md` is the authoritative answer to “where the project is now.” It must never be allowed to lag behind the newest material result.

## 1. Autonomous operation is mandatory

This is an agent-operated research repository. The repository owner is the project sponsor, not a required operator in the execution loop.

The active agent must independently perform all routine repository and research operations available through its tools, including:

- inspect branches, pull requests, issues, commits, files, and CI;
- create or select an appropriate `agent/*` branch;
- edit code, tests, workflows, reports, state files, and machine-readable results;
- run or dispatch experiments and validation workflows;
- create commits with descriptive messages;
- publish every material checkpoint;
- maintain the authoritative pull request;
- inspect failures, apply corrections, rerun checks, and record outcomes;
- publish hashes, manifests, witnesses, proof logs, and artifacts;
- keep the repository immediately usable by the next agent.

Do not ask the repository owner to run commands, create branches, commit, push, open or update pull requests, monitor CI, upload evidence, or reconstruct context.

Do not pause for approval before routine, reversible research operations. Make the strongest technically justified choice, preserve provenance, and checkpoint it. Ask for owner input only when a genuinely non-resolvable project-level decision is required.

Never force-push, erase evidence, silently rewrite a retraction, or merge an unverified counterexample claim.

## 2. Project objective

Search computationally for a counterexample to Barnette's conjecture:

> Every cubic, 3-connected, bipartite planar graph is Hamiltonian.

A graph is not a counterexample unless:

1. simplicity, cubicity, bipartiteness, planarity, and at least 3-connectivity are independently verified;
2. non-Hamiltonicity is established exactly;
3. the negative result has a machine-checkable certificate or independently checked proof log;
4. all source graphs, parameters, software versions, hashes, and transformations are recorded.

Timeouts, interrupted computations, heuristic misses, malformed cases, and solver failures are always `unknown`.

## 3. Canonical repository state

Authoritative branch:

```text
agent/adversarial-search-v2
```

Authoritative pull request:

```text
PR #1
```

Canonical current-state snapshot:

```text
docs/CURRENT_STATE.md
```

Append-only history:

```text
docs/RESEARCH_LOG.md
```

Dated machine-readable evidence:

```text
results/YYYY-MM-DD/
```

The active agent must verify that `docs/CURRENT_STATE.md` matches the newest commits, reports, result files, PR comments, and workflow results before beginning new work.

## 4. Mandatory state-retention invariant

A material insight is not considered incorporated until the active agent has completed every applicable part of this transaction:

1. update `docs/CURRENT_STATE.md` with:
   - the finding;
   - confidence label;
   - quantitative metrics;
   - evidence paths and hashes;
   - interpretation;
   - limitations;
   - resulting strategic change;
   - next action;
2. append a dated entry to `docs/RESEARCH_LOG.md`;
3. publish machine-readable evidence under `results/YYYY-MM-DD/` when computation produced data;
4. update or add the relevant technical report;
5. update the authoritative PR description or add a checkpoint comment;
6. commit and publish the changes.

No material finding may exist only in:

- chat history;
- private reasoning;
- terminal output;
- a local workspace;
- an Actions log;
- a PR comment;
- an auxiliary branch;
- an uncommitted result file.

PR comments and chat summaries are discovery aids, not durable state.

## 5. When the current-state snapshot must be updated

Update `docs/CURRENT_STATE.md` immediately after any of the following:

- a new exact positive or certified negative result;
- a solver discrepancy or retraction;
- an exact language correction;
- a new extreme candidate that changes prioritization;
- completion or elimination of a construction family;
- a workflow resolving with material data;
- a change in the strongest next experiment;
- discovery of stranded branch evidence or missing provenance;
- a new theorem-level structural insight;
- a strategy being retired or reinstated;
- a counterexample candidate being assembled;
- any result that a new agent would need to avoid repeating work or making a false claim.

Do not defer snapshot updates until the end of a long session when the interpretation has already changed.

## 6. Current mathematical direction

The detailed current state is maintained in `docs/CURRENT_STATE.md`.

The present strategic route is:

```text
certified cofacial H^{+--}
        -> 3-connected cofacial H^{+-}
        -> Kelmans amplification
        -> independently certified Barnette counterexample
```

The strongest certified object is a ternary facial obstruction in canonical order-100 candidate 489. Exact six-pole composition has produced planar cofacial binary-obstruction near-counterexamples that fail only 3-connectivity. The immediate problem is connectivity repair without restoring the forbidden Hamiltonian trace.

The first 655-repair source-2 family is fully eliminated. The next search must attack the sparsest remaining repair families, prioritizing one-closure cases. A discussion-derived `source-57` target must first be materialized as a committed reproducible repository object before computation continues.

## 7. Permanent validation policy

### Positive decisions

Accept a positive state or Hamiltonian cycle only with an independently checkable selected-edge witness.

Validate, as applicable:

- every selected edge belongs to the graph or patch;
- no selected edge is duplicated;
- selected edge count is exact;
- all degree constraints hold;
- the required number of connected components is present;
- terminal endpoints and pairings are correct;
- the required included/excluded edges are respected;
- a Hamiltonian witness is connected and spans every vertex.

### Negative decisions

A single MILP solver's infeasibility status is never mathematical evidence.

A final negative requires an independent proof-producing formulation, normally:

1. construct the final CNF;
2. solve UNSAT using an external proof-producing solver such as CaDiCaL;
3. emit textual DRAT or LRAT;
4. validate the proof with an independent checker such as `drat-trim`;
5. publish the CNF, proof, checker output, hashes, source graph, and transformation provenance.

### Exact finite enumeration

A local negative may be accepted as exact only when the finite enumeration is complete, has no budget abort, and its implementation and state space are independently checkable. Such a local exact negative is not automatically a whole-graph non-Hamiltonicity proof.

## 8. Permanent warnings and retractions

The following must remain visible in all future work:

1. **SciPy/HiGHS false infeasibility:** SciPy 1.17.0 falsely classified `c156-s0:P23` and `c446-s1:P01`; explicit witnesses under SciPy 1.18.0 retracted both results.
2. **Multi-parent key collision:** the first higher-order driver used locally numbered `c<cut>-s<side>` keys and could overwrite cases across graphs. Only `g<graph>-c<cut>-s<side>` output is authoritative.
3. **Positive underapproximation is insufficient for negative composition:** pole `C` contained an omitted positive six-terminal state. Negative language claims require complete exact languages or certified missing states.
4. **C4 repair orientation matters:** endpoint sorting can destroy directed bipartite face orientation and generate invalid repair interpretations.
5. **Matching rarity is not distance to nonexistence:** this failed for whole graphs, four-terminal `Q` states, and six-terminal signatures.

Never remove these warnings merely because later files contain corrected results.

## 9. Run specification before expensive work

Before a long or expensive experiment, commit a run specification containing:

- objective and hypothesis;
- exact source graph or graph family;
- generator and command;
- state space and mathematical formulation;
- shard, seed, or permutation selection;
- software and solver versions;
- timeout, retry, and budget policy;
- expected output paths;
- positive, negative, unknown, and retracted classification criteria;
- escalation conditions;
- abort conditions;
- required evidence and hashes.

For construction targets, include the graph encoding, pole identities, terminal permutations, separators, target edges, closure states, repair operation, and exact reproduction command.

## 10. Checkpoint contents

Every meaningful checkpoint should include, as applicable:

- machine-readable output;
- concise Markdown interpretation;
- exact counts and metrics;
- graph encodings or hashes;
- command-line arguments;
- environment versions;
- elapsed time or computational budget;
- witnesses or proof artifacts;
- known limitations;
- confidence label;
- next action.

Use these exact confidence labels:

### `verified`

Directly checkable positive witness, independently reproduced computation, complete finite enumeration, or checked proof certificate.

### `provisional`

Potentially important result from one formulation or incomplete confirmation.

### `unknown`

Timeout, interruption, malformed case, solver failure, resource exhaustion, missing provenance, or insufficient evidence.

### `retracted`

A prior result contradicted by a valid witness, stronger computation, or identified implementation error.

Do not use `non-Hamiltonian`, `counterexample`, `proved`, or equivalent final language unless the required certificate exists.

## 11. Branch and PR discipline

Use small descriptive commits. Prefer one coherent research checkpoint per commit or a short ordered sequence.

Recommended prefixes:

```text
experiment: record committed run specification
results: add exact state-language checkpoint
proof: add independently checked certificate
fix: correct formulation or indexing defect
docs: update canonical research state
docs: retract solver-dependent claim
ci: pin or repair validation workflow
```

Auxiliary branches may be used for isolated work, but material results must be integrated or explicitly indexed in `docs/CURRENT_STATE.md`. Do not allow an auxiliary branch to become the only location of a critical proof checker, witness set, generator, or result summary.

Do not merge diverged auxiliary branches wholesale. Selectively port valid files, preserve provenance, and run regressions.

## 12. Required files to keep synchronized

After a material result, update:

1. `docs/CURRENT_STATE.md`;
2. `docs/RESEARCH_LOG.md`;
3. the relevant technical report;
4. machine-readable evidence under `results/YYYY-MM-DD/`;
5. `AGENTS.md` only when the operating rules or permanent warning set changes;
6. PR #1 with a concise review-level checkpoint.

## 13. Immediate pickup checklist

A new agent must:

1. read `AGENTS.md`;
2. read `docs/CURRENT_STATE.md` completely;
3. read the latest research-log entries backward;
4. inspect PR #1 and current CI;
5. compare branch heads and newest results against the current-state snapshot;
6. resolve any state discrepancy before new computation;
7. verify that the active target has a committed reproducible specification;
8. execute autonomously;
9. checkpoint material results as they occur;
10. before ending, update the canonical snapshot and append the research log.

## 14. End-of-session gate

Before finishing any work session, explicitly verify:

- [ ] all material findings are committed;
- [ ] `docs/CURRENT_STATE.md` reflects the newest interpretation;
- [ ] `docs/RESEARCH_LOG.md` contains a dated append-only entry;
- [ ] evidence files and hashes are published;
- [ ] PR #1 contains the latest review-level checkpoint;
- [ ] CI status and unresolved jobs are recorded accurately;
- [ ] no critical work exists only on an auxiliary branch or in chat;
- [ ] the next agent can identify and reproduce the exact next action without reconstructing conversation history.

A session is not complete until this gate is satisfied.