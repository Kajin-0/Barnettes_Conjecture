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