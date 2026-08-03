# Computational Research Log

This is the append-only chronological record of material experiments, findings, corrections, and changes of analytical direction.

Do not rewrite prior entries to make the history appear cleaner. Add a dated correction when an earlier interpretation changes.

Every entry should include:

- timestamp in UTC;
- status: `verified`, `provisional`, `unknown`, or `retracted`;
- objective;
- inputs and exact computational scope;
- method and software environment;
- quantitative results;
- interpretation and limitations;
- repository paths containing machine-readable evidence;
- next action.

---

## 2026-08-01 — Canonical order-92 structural search

**Status:** `verified` for positive witnesses and reproduced aggregate counts  
**Counterexample found:** No

### Objective

Replace expansion-history sampling with canonical generation at the first order beyond the published exhaustive frontier, then search for a compositional non-Hamiltonicity obstruction across cyclic 4-edge cuts.

### Canonical input

- generator: official plantri 5.8;
- archive SHA-256: `e78a944116fec9f2c9f5e484206276cc2b0043bae803e9815f4b2683614629b8`;
- generation form: `plantri -bc4dg 92d RES/10000`;
- shard residues: `0, 137, 911, 2718, 4093, 6121, 7351, 9001` modulo 10,000;
- retained outputs per shard: 300;
- total canonical graph6 records: 2,400.

### Filtering and ranking

- all 2,400 inputs passed the implemented order, cubicity, bipartiteness, and planarity checks;
- 58 were rejected by the implemented big-face-neighbour sufficient-condition filter;
- 2,342 escaped the implemented face-based sufficient-condition filters;
- 8 graphs were retained using randomized perfect-matching fragmentation as a ranking heuristic;
- no Hamiltonian complement appeared in 128 randomized perfect-matching trials for each retained graph;
- the best sampled complementary 2-factors for the retained leaders had 8 components.

The matching statistics are heuristic prioritization data only. They are not evidence of non-Hamiltonicity.

### Exact natural cyclic-4-cut analysis

For the leading retained graph:

- vertices: 92;
- edges: 138;
- natural cyclic 4-edge cuts: 647;
- cut-side four-terminal patches: 1,294;
- complete signatures: 1,294;
- unresolved signatures after retry: 0;
- maximal six-state signatures: 1,294;
- independently certified restrictive signatures: 0;
- planar bipartition-preserving patch-map comparisons: 1,283,456;
- comparisons with six compatible state pairs: 1,283,456;
- incompatible patch maps: 0.

Positive state decisions were represented by explicit selected-edge witnesses and checked for edge membership, edge count, connectivity, terminal degrees, and internal degree constraints.

### Edge-deletion four-poles

Deleting both endpoints of each of the 138 edges produced 138 four-terminal patches. All 138 realized all six structurally permitted states through explicit witnesses.

### Annular transfer search

- nested-cut annuli available: 2,084;
- diverse annuli tested: 200;
- positively witnessed entries in each conservative 9-by-9 relation: 26;
- labelled relation patterns: 12;
- empty tested pair products: 0;
- minimum positively witnessed pair-product cardinality: 43.

Negative relation entries were not independently certified. The reported non-emptiness is robust because adding omitted true entries cannot make a nonempty Boolean product empty.

### Reproduction

Clean GitHub Actions reproduction:

- workflow run ID: `30699671554`;
- artifact SHA-256: `fd22be4b51b1d950391f8349697d5842e59b5b58f60b246aef9d08a57f5d104d`;
- Python: 3.12;
- NetworkX: 3.6.1;
- SciPy: 1.18.0;
- plantri archive hash independently recorded by the workflow.

### Interpretation

Every natural cyclic-4-cut side of the leading canonical order-92 graph was maximally Hamiltonian-flexible under the six boundary states permitted by bipartite parity and planar noncrossing constraints. No one-interface incompatible gluing was found.

This strongly disfavors constructing a counterexample from ordinary cyclic-4-cut pieces of this graph. It does not exclude restrictive patches in other order-92 graphs, at larger orders, through larger interfaces, or through global obstructions.

### Evidence paths

- `docs/CANONICAL_STRUCTURAL_SEARCH_2026-08-01.md`
- `results/2026-08-01/canonical_structural_summary.json`
- `results/2026-08-01/annular_transfer_summary.json`
- `.github/workflows/canonical-barnette-search.yml`

### Next action

Run a higher-order, Q-first search at orders 94, 96, 98, and 100. Test the two noncrossing two-path states before path states, require explicit positive witnesses, and independently re-encode every apparent missing state in proof-producing SAT.

---

## 2026-08-01 — Retraction of two apparent restrictive patches

**Status:** `retracted`

### Earlier claim

A local SciPy 1.17.0 run reported two five-state cut-side patches:

- `c156-s0`, apparently missing `P23`;
- `c446-s1`, apparently missing `P01`.

The local HiGHS interface returned infeasibility statuses for those states.

### Contradicting evidence

A clean SciPy 1.18.0 GitHub Actions run produced explicit spanning-path witnesses for both states.

Each witness was independently checked to satisfy:

- all selected edges belong to the patch;
- exactly `n - 1` edges are selected;
- the selected subgraph is connected;
- the requested terminals have degree one;
- every other patch vertex has degree two.

The positive witnesses conclusively invalidate the earlier negative classifications.

### Correction

- the restrictive-patch claim was withdrawn;
- the certificate file containing the false negative classifications was deleted;
- the aggregate result was corrected to 1,294 maximal six-state signatures;
- SciPy was pinned to 1.18.0 for the reproduced environment;
- future single-solver infeasibility statuses are prohibited as mathematical evidence.

### Evidence path

- `results/2026-08-01/solver_discrepancy_retraction.json`

### Permanent validation rule

An apparent missing state remains `provisional` until reproduced independently. A final negative state requires an independently checked proof-producing SAT certificate. Timeouts and solver failures remain `unknown`.

---

## 2026-08-01 — Durable agent handoff and checkpoint protocol

**Status:** `verified`

### Objective

Prevent loss of research state when conversational or agent context is unavailable.

### Repository changes

- added root `AGENTS.md` as the authoritative operational handoff;
- added this append-only research log;
- defined mandatory checkpoints before expensive runs and after every material phase;
- defined result-confidence labels;
- required synchronization of reports, machine-readable outputs, handoff state, and the active pull request;
- recorded the current validated metrics, retraction, stopping point, and next experiment.

### Rule going forward

No material finding may remain only in chat history, terminal output, a local workspace, or an uncommitted scratch file. Important results and analytical pivots must be checkpointed to the repository immediately.

---

## 2026-08-01 — Fully autonomous repository operation

**Status:** `verified`

### Objective

Remove any operational dependency on the repository owner and make continuation possible without manual branching, commits, pushes, pull-request administration, CI monitoring, artifact handling, or handoff maintenance.

### Repository changes

- added a mandatory autonomous-operation section to `AGENTS.md`;
- defined the repository owner as project sponsor rather than routine operator;
- assigned branch management, code changes, experiments, commits, publication, PR maintenance, CI follow-up, artifacts, documentation, and handoff to the active agent;
- prohibited agents from transferring routine repository mechanics to the owner;
- required agents to choose a durable alternative when a specific platform operation is unavailable;
- updated `README.md` and `agent.md` so the autonomous model is visible from every entry point.

### Operating rule

The active agent owns the complete execution loop. The agent must not ask the owner to run commands, push changes, open or update pull requests, monitor workflows, upload evidence, or reconstruct state. Routine reversible research decisions should be made autonomously and checkpointed immediately.

If direct merge capability is unavailable, the agent must keep the authoritative research branch and pull request complete and current rather than delegating the merge or publication process to the owner.

### Evidence paths

- `AGENTS.md`
- `agent.md`
- `README.md`
- `docs/RESEARCH_LOG.md`

### Next action

Continue the higher-order Q-first campaign under the autonomous checkpoint protocol. Every material experimental phase must be committed, published, documented, and reflected in the active pull request by the agent.

---

## 2026-08-01 — Higher-order Q-first v2 campaign

**Status:** `verified` for positive witnesses at orders 96 and 100; `unknown` for generation at orders 94 and 98  
**Counterexample found:** No

### Objective

Search higher canonical orders for a natural cyclic-4-cut side lacking one of the two noncrossing two-path boundary states.

### Corrected driver

The collision-safe v2 driver names every patch using:

```text
g<graph-index>-c<cut-index>-s<side-index>
```

and asserts key uniqueness before and after parallel execution.

### Verified scope

Order 96:

- 4,800 canonical graphs sampled;
- 4,740 escaped the implemented sufficient-condition filters;
- 6 parent graphs analyzed;
- 8,620 natural cut-side patches available in those parents;
- 1,920 patch sides selected;
- 3,840 Q states attempted;
- 3,840 explicit positive witnesses independently validated;
- 0 provisional negatives;
- 0 unknowns.

Order 100:

- 4,800 canonical graphs sampled;
- 4,738 escaped the implemented sufficient-condition filters;
- 6 parent graphs analyzed;
- 9,112 natural cut-side patches available in those parents;
- 1,920 patch sides selected;
- 3,840 Q states attempted;
- 3,840 explicit positive witnesses independently validated;
- 0 provisional negatives;
- 0 unknowns.

Combined verified result:

```text
7,680 / 7,680 attempted Q states positively witnessed
```

### Generation failures

Orders 94 and 98 produced no flushed graph6 record in twelve sparse `RES/10000` classes before the 240-second per-class timeout. The jobs failed closed before ranking or Q-state analysis.

These are computational generation failures and have no negative mathematical interpretation. Both orders remain unresolved by this campaign.

### Reproduction

- workflow run ID: `30702896816`;
- order-96 artifact ID: `8819552108`;
- order-96 artifact SHA-256: `ac2e219a86811b11fc646b9d5b012eac55e0a2b1f2db5b89d693c62ff675d591`;
- order-100 artifact ID: `8819569587`;
- order-100 artifact SHA-256: `0b4cfbab9b08c896dedc76404c01f56845597d404cc6fc2f3067f246aaad9188`.

### Interpretation

The ordinary missing-Q-state mechanism appears substantially rarer than expected. The campaign did not cover all available cut sides or all sampled parents, so it does not establish universal Q-flexibility.

The stronger continuation is dual-track:

1. complete and broaden natural-cut Q-state coverage, including repaired generation at orders 94 and 98;
2. escalate to multi-interface annular transfer correlations, which can remain restrictive even when every one-boundary marginal is full.

### Evidence paths

- `docs/HIGHER_ORDER_Q_FIRST_V2_2026-08-01.md`
- `results/2026-08-01/higher_order_q_first_v2_summary.json`
- `.github/workflows/higher-order-q-first-v2.yml`
- `search/higher_order_q_first_v2.py`
- `search/sat_verify_q_candidates.py`

### Next action

Repair sparse generation using an output-flushing plantri wrapper and lower-modulus adaptive shards. In parallel, expand the verified orders to all natural cut sides in a broader parent set and implement a reproducible multi-interface transfer search.

---

## 2026-08-03 16:14 UTC — Canonical current-state snapshot and continuity correction

**Status:** `verified` repository-state correction  
**Counterexample found:** No

### Objective

Correct a durable handoff failure discovered when a new agent reconstructed the project from the repository and pull requests.

The repository contained later exact results and strategic pivots, but the files claiming to be the authoritative handoff still stopped at the early order-92 and higher-order-Q phases. Important context had migrated into technical reports, result files, PR comments, and diverged branches without being incorporated into one current canonical location.

### Failure observed

`AGENTS.md` and this research log did not contain the later project state, including:

- the proof-certified ternary facial obstruction in order-100 candidate 489;
- exact six-pole languages for poles `A`, `B`, and `C`;
- the correction of the omitted positive pole-`C` state;
- 65 planar cofacial five-pole binary-obstruction near-counterexamples failing only 3-connectivity;
- complete elimination of the 655-repair source-2 family;
- the exact six-terminal tail and recurring nine-state kernel;
- retirement of matching rarity as a boundary-language sparsity objective;
- the current one-closure connectivity-repair direction;
- stranded implementation and evidence on auxiliary branches;
- the fact that the discussion-derived `source-57` target had not been materialized as a tracked reproducible object.

The prior rule requiring agents to “update the handoff” was insufficient because it did not designate one canonical mutable snapshot or enforce an end-of-session reconciliation transaction.

### Repository correction

Created:

```text
docs/CURRENT_STATE.md
```

This file is now the single canonical mutable snapshot of:

- the strongest validated mathematical results;
- exact metrics and evidence paths;
- permanent warnings and retractions;
- retired strategies;
- the current construction route;
- the immediate active target;
- current workflow state;
- branch and integration debt;
- the exact pickup sequence for the next agent.

Updated:

- `AGENTS.md` to make the canonical snapshot mandatory and define a hard state-retention invariant;
- `README.md` so every repository entry path points to the snapshot;
- `agent.md` so tool-oriented agents read the snapshot before work;
- `docs/RESEARCH_LOG.md` with this append-only incident and correction record.

Commits:

```text
522bb33e86a889d17b04f1fad34b69796db62ac0  docs: add canonical current research state
83258d5a0f6fcdd065023935ae220df047aaa503  docs: make current state checkpoint mandatory
4dcd6c5185ac1455b420c21af61972927b5bb9e5  docs: point entry path to canonical state snapshot
f3fc62b17e9f3592586f020af774cc5d95e5685c  docs: update compact agent entry point
```

### New mandatory invariant

A material insight is not durably incorporated until all applicable parts of the following transaction are complete:

1. update `docs/CURRENT_STATE.md` with finding, confidence, evidence, interpretation, limitations, strategic consequence, and next action;
2. append this chronological log;
3. publish machine-readable evidence under `results/YYYY-MM-DD/` when data was produced;
4. update the relevant technical report;
5. checkpoint PR #1;
6. commit and publish.

Before ending a work session, the active agent must compare the canonical snapshot against the newest commits, reports, results, PR comments, auxiliary branches, and workflow outcomes. Any discrepancy must be resolved in the repository.

### Current strategic state captured

The canonical snapshot now records the active route:

```text
certified cofacial H^{+--}
        -> 3-connected cofacial H^{+-}
        -> Kelmans amplification
        -> independently certified Barnette counterexample
```

The next exact attack is the sparsest remaining connectivity-repair family, prioritizing one-closure cases. Before computation, the discussion-derived `source-57` target must be committed with graph encoding, pole permutation, separator geometry, target edges, outside closure, repair specification, and exact reproduction command.

### Limitations

This correction captures repository state available through the authoritative branch, all open PRs, accessible branch comparisons, reports, result summaries, PR comments, and current workflow metadata. Workflow state remains time-sensitive and must be updated when Grand Q-first v3 resolves.

### Next action

1. Add a PR #1 checkpoint linking the canonical snapshot and continuity rule.
2. Materialize the `source-57` one-closure target as a committed run specification and machine-readable candidate record.
3. Selectively integrate still-valid proof and search artifacts stranded on auxiliary branches.
4. Reconcile `docs/CURRENT_STATE.md` whenever the active workflows complete or the construction target changes.

---

## 2026-08-03 16:24 UTC — Annular swap and semigroup provenance recovery

**Status:** `provisional` for provenance; exact claims preserved from authoritative PR body  
**Counterexample found:** No

### Objective

Reconcile the newly created canonical current-state snapshot against the complete PR #1 body.

The comparison immediately found another important result that existed only in PR-level prose and had not been represented by a dedicated tracked report or machine-readable summary.

### Recovered claim

The PR body reported a 300-annulus order-100 scan with six cardinality-two `Q -> Q` blocks. These were identified as three 8-cycle rings viewed in both directions.

The exact two-state block was reported as:

```text
Q01_23 -> Q03_12
Q03_12 -> Q01_23
```

The two diagonal transitions were exactly impossible. The reported structural explanation was that degree constraints leave the two alternating perfect matchings of the 8-cycle; off-diagonal closure yields one spanning cycle, while diagonal closure yields two disjoint cycles.

The reported full relation had:

```text
|R|   = 14
|R^2| = 28
|R^3| = 36
```

The reported broader Boolean relation semigroup had:

- 14 distinct positive relation patterns;
- 834 relations in its closure;
- stabilization by depth six;
- no empty product;
- minimum generated cardinality 13;
- complete 36-transition relations.

### Interpretation

The 8-cycle ring provides an exact nontrivial annular correlation but not an obstruction. Its `Q -> Q` block is a swap permutation, and repeated composition increases flexibility until the full relation is reached.

The remaining annular target is therefore an exact block with:

- zero transitions;
- one transition; or
- two non-bijective transitions producing a zero row or column.

The certified ternary-obstruction connectivity-repair program remains the higher-priority constructive route.

### Provenance problem

No dedicated tracked raw artifact was found for:

- the 300-annulus scan;
- the six annulus identifiers;
- the exact 8-cycle enumeration;
- the 14-transition full relation;
- the relation powers;
- the 834-relation semigroup calculation;
- commands, software versions, elapsed times, or hashes.

Therefore the mathematical claim has been preserved but not silently upgraded to independently verified repository evidence.

### Repository correction

Created:

- `docs/ANNULAR_SWAP_SEMIGROUP_CHECKPOINT_2026-08-03.md`;
- `results/2026-08-03/annular_swap_semigroup_checkpoint.json`.

Updated:

- `docs/CURRENT_STATE.md` with the exact reported metrics, strategic consequence, provenance warning, evidence map, and recovery action.

Commits:

```text
fee341674a946cde7d06dea1b2c69f85cd10005a  results: preserve annular swap semigroup checkpoint
634a9e12f2baff39bc36c66aae7f067d560040f6  docs: preserve annular swap semigroup result
00cdf3f51830999fc68eae6d00f28680b7f27729  docs: reconcile annular swap result into current state
```

### Required next action

1. Search auxiliary branches and workflow artifacts for the original annular files.
2. If absent, reconstruct and rerun the 8-cycle exact relation and Boolean semigroup closure.
3. Publish the full commands, identifiers, software versions, raw output, and hashes.
4. Upgrade or correct the checkpoint only after the evidence is available.
