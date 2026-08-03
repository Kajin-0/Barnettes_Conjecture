# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative pull request:** PR #1  
**Snapshot timestamp:** 2026-08-03 16:24 UTC  
**Snapshot commit before this update:** `634a9e12f2baff39bc36c66aae7f067d560040f6`  
**Counterexample found:** No

This file is the single canonical mutable snapshot of the project. It exists to prevent research state from being lost when agents, conversations, tools, or working branches change.

`docs/RESEARCH_LOG.md` is the append-only chronology. This file is the current-state compression of that chronology.

## Mandatory state-retention invariant

A material research insight is not durably incorporated until the active agent has completed all applicable parts of this checkpoint transaction:

1. update this file with the current interpretation, confidence, evidence path, and next action;
2. append a dated entry to `docs/RESEARCH_LOG.md` without rewriting prior history;
3. commit machine-readable evidence under `results/YYYY-MM-DD/` when computation produced data;
4. update or add the relevant technical report;
5. update the authoritative PR description or add a PR checkpoint comment;
6. publish the commit to the authoritative branch.

Before ending any research session, the agent must compare this file with the newest commits, result files, reports, PR comments, and workflow outcomes. Any discrepancy must be resolved in the repository, not left in chat.

## 1. Project objective and proof standard

Barnette's conjecture states:

> Every cubic, 3-connected, bipartite planar graph is Hamiltonian.

A counterexample claim requires all of the following:

1. independent verification that the graph is simple, cubic, bipartite, planar, and at least 3-connected;
2. exact non-Hamiltonicity;
3. an independently checked machine proof, preferably a CaDiCaL DRAT/LRAT proof accepted by an independent checker;
4. complete provenance for source graphs, transformations, parameters, software versions, hashes, and proof artifacts.

Timeouts, interrupted computations, heuristic misses, malformed cases, and single-solver infeasibility statuses are `unknown`, never negative evidence.

## 2. Current strategic formulation

The project is no longer primarily a blind large-graph enumeration search. The strongest route is now a proof-oriented gadget-synthesis program:

```text
certified cofacial H^{+--}
        -> 3-connected cofacial H^{+-}
        -> Kelmans amplification
        -> independently certified Barnette counterexample
```

Here:

- `H^{+--}` means no Hamiltonian cycle can include one designated facial edge `x` while excluding two designated facial edges `y,z`;
- `H^{+-}` means no Hamiltonian cycle can include designated edge `X` while excluding designated edge `e`;
- the construction target is to reduce the certified ternary obstruction to a binary cofacial obstruction without restoring the forbidden Hamiltonian trace.

## 3. Strongest certified result: ternary facial obstruction

Canonical order-100 candidate 489 is a verified Barnette graph containing six proof-certified cofacial triples with the property

```text
x => y or z
```

The principal triple is:

```text
x = (14,18)
y = (10,17)
z = (5,11)
```

No Hamiltonian cycle contains `x` while avoiding both `y` and `z`.

Certification:

- graph order: 100;
- graph size: 150 edges;
- Barnette predicates independently checked;
- six cases solved UNSAT by CaDiCaL 3.0.1;
- textual DRAT proofs accepted by `drat-trim`;
- workflow run: `30750008325`;
- artifact ID: `8834131003`;
- artifact SHA-256: `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`.

Evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- `search/sat_verify_face_constraints.py`
- `.github/workflows/face-three-edge-proof.yml`

Classification: `verified`.

## 4. Exact six-pole languages

Three certified ternary cases supplied six-terminal poles `A`, `B`, and `C`.

Every pole was completed over the full 75-state boundary space using independent exhaustive perfect-matching recursion with closed-subtour pruning and a 100,000,000-call budget per state.

| Pole | Positive states | Exact negative states | Unknown |
|---|---:|---:|---:|
| A | 26 | 49 | 0 |
| B | 26 | 49 | 0 |
| C | 26 | 49 | 0 |

Critical correction:

```text
Pole C also realizes mask 63 with pairing (0,1)(2,5)(3,4).
```

That state was omitted from an earlier positive underapproximation. All finite-state compositions were regenerated from the exact languages. The correction prevented a false zero-language interpretation of a Hamiltonian five-pole graph.

Exact-language result SHA-256:

```text
4c167dd746a9afb4ecee982fd989dc141d5b577df0921f3e503d478b1a856863
```

Evidence:

- `results/2026-08-02/exact_six_pole_and_repair_summary.json`
- `docs/EXACT_SIX_POLE_AND_CONNECTIVITY_REPAIR_2026-08-02.md`

Classification: `verified`.

## 5. Five-pole near-counterexamples

Using corrected `AABCC` exact pole languages, 100,000 terminal permutations were screened for the target trace `X+e-`.

| Stage | Count |
|---|---:|
| Exact zero target languages | 9,818 |
| Legal and copy-connected | 2,597 |
| Planar | 122 |
| Planar with `X` and `e` cofacial | 65 |
| 3-connected | 0 |

All 65 cofacial exact-language obstructions have vertex connectivity exactly two.

Interpretation:

- the desired binary Hamiltonian-trace obstruction exists exactly at the pole-language level;
- the remaining defect is 3-connectivity;
- connectivity repair is the immediate constructive bottleneck.

Classification: `verified` for exact boundary-language obstruction and graph predicates.

## 6. Completed source-2 connectivity-repair family

Selected source near-counterexample:

```text
source index = 2
separator = (17,400)
component sizes = 99 and 399
X = (5,110)
e = (11,105)
```

A correctly oriented separator-crossing facial `C4` expansion generated 655 repairs. Endpoint-sorted orientation was explicitly rejected because it can violate the required bipartite orientation.

All 655 repairs independently passed:

- simplicity;
- cubicity;
- bipartiteness;
- planarity;
- 3-connectivity.

Each repair is therefore a 504-vertex Barnette graph.

Exact contraction of untouched poles and exhaustive/validated solution of affected supercomponents found the forbidden-compatible trace in every repair:

| Repair class | Repairs | Positive |
|---|---:|---:|
| `C3-C4` internal edges | 359 | 359 |
| `B2-C4` internal edges | 126 | 126 |
| `A0-C4` internal edges | 52 | 52 |
| `A1-C4` internal edges | 87 | 87 |
| `C4` plus glue `B2-C3` | 14 | 14 |
| `C4` plus glue `A0-B2` | 14 | 14 |
| glue `A1-C3` plus `C4` | 3 | 3 |
| **Total** | **655** | **655** |

Conclusion:

```text
The source-2 separator-crossing C4 repair geometry is completely eliminated.
```

This does not invalidate the ternary-obstruction program. It shows that this repair operation restores both 3-connectivity and the forbidden Hamiltonian trace for this separator geometry.

Evidence:

- `docs/EXACT_SIX_POLE_AND_CONNECTIVITY_REPAIR_2026-08-02.md`
- `results/2026-08-02/exact_six_pole_and_repair_summary.json`

Classification: `verified`.

## 7. Exact six-terminal cyclic-cut tail

The six-terminal pilot sampled 4,594 cut-side patches and initially reported 106 zero-observed-state patches and 1,679,866 zero-observed-compatibility maps. Those apparent zeros were sampling artifacts.

Nine of the smallest and strongest zero-hit patches were completed by exhaustive perfect-matching enumeration:

| Patch | Order | Matchings enumerated | Exact states |
|---|---:|---:|---:|
| `g5-c111-s0` | 44 | 58,556 | 23 |
| `g5-c78-s0` | 44 | 56,230 | 24 |
| `g5-c246-s0` | 46 | 87,521 | 24 |
| `g5-c80-s0` | 46 | 90,649 | 24 |
| `g1-c140-s0` | 48 | 144,261 | 23 |
| `g1-c82-s0` | 48 | 137,706 | 24 |
| `g5-c179-s0` | 48 | 146,816 | 24 |
| `g1-c174-s0` | 50 | 233,064 | 24 |
| `g2-c140-s0` | 50 | 240,078 | 23 |

Across 540 exact patch-pair/dihedral-map comparisons:

```text
minimum compatibility = 9
incompatible exact gluings = 0
```

All nine exact signatures share this kernel:

```text
U012345_01_23_45
U012345_05_12_34
U0123_01_23
U0123_03_12
U0145_01_45
U01_01
U2345_23_45
U23_23
U45_45
```

This is an empirical exact result for the nine completed patches, not a theorem for every cyclic six-edge-cut patch.

Consequence:

```text
few randomized matching hits != sparse exact boundary language
```

Matching rarity is retired as the primary six-terminal search objective.

Evidence:

- `docs/SIX_TERMINAL_EXACT_TAIL_2026-08-03.md`
- `results/2026-08-03/six_terminal_exact_tail_summary.json`
- summary SHA-256: `5a83c3b453b81be1e4327d7dd94f00918f43eb3c267aad69f18f034833fc3689`.

Classification: `verified` for the nine completed patches.

## 8. Four-terminal, higher-order, and annular results that constrain strategy

### Canonical order-92 natural cyclic-4-cut analysis

- 2,400 canonical order-92 graphs sampled;
- 2,342 escaped implemented sufficient-condition filters;
- 647 natural cyclic 4-edge cuts in the leading graph;
- 1,294 patch sides;
- all 1,294 signatures were maximal six-state signatures;
- 1,283,456 legal patch-map comparisons;
- every comparison retained six compatible state pairs;
- zero incompatible maps.

### Order-92 matching-Q exact tail

The matching reduction is exact: a natural four-terminal `Q` state is the complement of a perfect matching whose complement has two components with the requested terminal pairing.

Sampling all 10,192 patch sides and deepening the hardest tail left 71 zero-hit patches. Exact escalation produced:

```text
142 / 142 requested Q states positive
```

The strongest sampler near-miss, `g6-c633-s0`, had zero target hits in 4,096 trials but admitted both target states exactly.

### Higher-order collision-safe Q-first v2

Across orders 96 and 100:

- 9,600 canonical graphs sampled;
- 12 high-ranked parents analyzed;
- 17,732 natural cut-side patches available;
- 3,840 patch sides selected;
- 7,680 noncrossing `Q` states tested;
- 7,680 independently validated positive witnesses;
- zero provisional negatives;
- zero unknown states;
- zero certified missing `Q` states.

The original multi-parent driver keyed tasks only as `c<cut>-s<side>` and could overwrite cases across parent graphs. Its output is superseded and must not be used. The authoritative key scheme is:

```text
g<graph>-c<cut>-s<side>
```

### Annular transfer pilot

The tracked order-100 pilot contained 13-17 positively witnessed transitions per selected relation and 95 end-to-end composed `Q` witnesses. Conservative order-92 annular products also remained nonempty.

### Exact 8-cycle annular swap checkpoint

The authoritative PR body contained an additional exact result that had not been preserved in a dedicated tracked report or raw result file. A continuity checkpoint now records the claim without upgrading its provenance.

Reported scan:

- 300 order-100 annuli;
- six cardinality-two `Q -> Q` blocks;
- structurally three 8-cycle rings viewed in both directions;
- exact block:

```text
Q01_23 -> Q03_12
Q03_12 -> Q01_23
```

The two diagonal transitions were reported exactly impossible because the 8-cycle degree constraints leave two alternating perfect matchings: off-diagonal closure gives one spanning cycle, while diagonal closure gives two disjoint cycles.

Reported full relation powers:

| Relation | Cardinality |
|---|---:|
| `R` | 14 |
| `R^2` | 28 |
| `R^3` | 36 |

Reported broader semigroup:

- 14 distinct positive relation patterns;
- 834 relations in the Boolean closure;
- stabilization by depth six;
- no empty product;
- minimum generated cardinality 13;
- complete 36-transition relations reached.

Strategic consequence:

- the exact 8-cycle relation is a swap permutation, not an annihilator;
- repeated composition increases flexibility;
- the remaining annular target is an exact `Q` block with zero or one transition, or a non-bijective two-transition block with a zero row or column;
- certified ternary-pole connectivity repair remains the stronger immediate construction route.

Provenance status:

```text
provenance incomplete
```

The original 300-annulus raw output, exact ring enumeration, and 834-relation semigroup artifact were not located. Recover or reproduce before treating this checkpoint as independently verified evidence.

Checkpoint evidence:

- `docs/ANNULAR_SWAP_SEMIGROUP_CHECKPOINT_2026-08-03.md`
- `results/2026-08-03/annular_swap_semigroup_checkpoint.json`

## 9. Permanent retractions and warnings

### SciPy/HiGHS false infeasibility

SciPy 1.17.0 reported two false missing path states:

```text
c156-s0:P23
c446-s1:P01
```

SciPy 1.18.0 produced explicit valid spanning-path witnesses. Single-solver MILP infeasibility is permanently prohibited as mathematical evidence.

Evidence:

- `results/2026-08-01/solver_discrepancy_retraction.json`

### Multi-parent task-key collision

The first higher-order driver used locally numbered keys and could overwrite results from different parent graphs. Only the collision-safe v2 output is authoritative.

### Exact-language underapproximation error

Positive underapproximations cannot support a negative composition claim. Pole `C` had an omitted positive state, so all negative composition arguments must use complete exact languages or independently certified missing states.

### Orientation-sensitive C4 repair

Sorting endpoints of facial edges destroys directed bipartite orientation information. Separator-crossing `C4` repair generation must preserve oriented face-edge roles.

### PR-body-only results are not durable evidence

A mathematical result written only in a PR body or comment is at risk of loss and lacks complete reproducibility. Such claims must be copied into the canonical snapshot, a dated report, and machine-readable evidence with explicit provenance status.

## 10. Retired or strongly deprioritized strategies

Do not restart these without a new mathematical reason:

1. randomized perfect-matching fragmentation as evidence of non-Hamiltonicity;
2. increasing random matching samples as a proxy for exact boundary-language sparsity;
3. ordinary natural four-terminal missing-`Q` searches as the sole attack;
4. direct six-terminal gluing based on sampled zero signatures;
5. unrestricted adjacent-edge-deletion four-pole search;
6. repeated composition of the exact 8-cycle annular swap relation;
7. the completed source-2 separator-crossing `C4` repair family;
8. blind growth to larger whole graphs without an exact obstruction objective.

Heuristics may still rank cases, but they cannot determine negative classifications.

## 11. Immediate active target

Continue across the remaining 64 cofacial five-pole near-counterexamples.

For each source graph:

1. enumerate every two-vertex separator;
2. generate correctly oriented separator-crossing `C4` repairs and any justified alternative minimal repair gadgets;
3. reject failures of simplicity, cubicity, bipartiteness, planarity, or 3-connectivity;
4. contract untouched poles using exact 26-state languages;
5. enumerate exact compatible outside closures;
6. rank repair families by closure count, attacking one-closure cases first;
7. solve the affected supercomponent exactly;
8. route any repair with zero compatible closures to proof-producing whole-graph SAT;
9. if a cofacial `H^{+-}` obstruction is certified, apply Kelmans amplification and independently certify the resulting Barnette graph.

A prior discussion identified a `source-57` one-closure repair family as the strongest immediate target. At this snapshot, no tracked source-57 candidate record, generator specification, result file, or branch artifact was found. Therefore `source-57` is currently a discussion-derived identifier, not a durable executable checkpoint.

Required first action before computation:

```text
Materialize source 57 in the repository with graph encoding, pole permutation,
separator geometry, target edges, outside closure, repair specification,
and exact reproduction command.
```

Do not rely on the label alone.

## 12. Current CI and workflow state

As of 2026-08-03 16:14 UTC at pre-continuity head `7b21af64...`:

- canonical cyclic-cut regression: success;
- three-edge facial obstruction proof: success;
- Q-state SAT proof regression: success;
- Grand Q-first v3 run `30810878974`: in progress;
- full natural-cut Q tests at orders 96 and 100: in progress;
- repaired order-94 jobs: generation completed, downstream analysis skipped because shards were empty or non-actionable under the workflow conditions;
- repaired order-98 generation jobs: in progress.

The PR body still names older Grand-v3 run `30727791413`; live workflow inspection supersedes that stale identifier.

Workflow state is time-sensitive. The next agent must re-check it and update this section when the run resolves.

## 13. Repository continuity and integration debt

The authoritative branch contains the current mathematical reports but not every useful implementation or checkpoint artifact.

Unique work remains on diverged auxiliary branches:

| Branch | Unique material not integrated into authoritative head |
|---|---|
| `agent/matching-q-reduction` | order-92 matching-Q screen/deep code and exact-tail evidence |
| `agent/proof-regression-checkpoint` | SAT/DRAT positive and negative regression certificates |
| `agent/six-terminal-interface` | six-terminal sampler, direct-glue search, and workflow |
| `agent/higher-order-q-results` | detailed order-96/100 hardest-case checkpoint |
| `agent/order94-98-expansion-fallback` | exact-order expansion fallback implementation and workflow |
| `agent/whole-graph-sat-proof` | `search/sat_verify_hamiltonian_candidates.py`, a 387-line whole-graph proof checker |

The exact annular swap and semigroup result also had a continuity defect: it was present in the PR body but no dedicated raw artifact was located. It is now preserved as a provenance-incomplete checkpoint pending recovery.

Integration rule:

- do not merge auxiliary branches wholesale;
- rebase or selectively port still-valid files onto the authoritative head;
- preserve evidence hashes and provenance;
- run regressions after integration;
- close obsolete PRs only after their unique evidence is durably incorporated.

## 14. Canonical evidence map

| Topic | Human-readable report | Machine-readable evidence |
|---|---|---|
| Order-92 structural search | `docs/CANONICAL_STRUCTURAL_SEARCH_2026-08-01.md` | `results/2026-08-01/canonical_structural_summary.json` |
| Higher-order Q-first v2 | `docs/HIGHER_ORDER_Q_FIRST_V2_2026-08-01.md` | `results/2026-08-01/higher_order_q_first_v2_summary.json` |
| Ternary obstruction | `docs/EXACT_SIX_POLE_AND_CONNECTIVITY_REPAIR_2026-08-02.md` | `results/2026-08-02/three_edge_face_candidates.json` |
| Exact six-pole languages and source-2 repair | `docs/EXACT_SIX_POLE_AND_CONNECTIVITY_REPAIR_2026-08-02.md` | `results/2026-08-02/exact_six_pole_and_repair_summary.json` |
| Exact six-terminal tail | `docs/SIX_TERMINAL_EXACT_TAIL_2026-08-03.md` | `results/2026-08-03/six_terminal_exact_tail_summary.json` |
| Annular swap and semigroup checkpoint | `docs/ANNULAR_SWAP_SEMIGROUP_CHECKPOINT_2026-08-03.md` | `results/2026-08-03/annular_swap_semigroup_checkpoint.json` |
| Retraction | `docs/CANONICAL_STRUCTURAL_SEARCH_2026-08-01.md` | `results/2026-08-01/solver_discrepancy_retraction.json` |
| Chronology | `docs/RESEARCH_LOG.md` | dated result directories |

## 15. Required pickup sequence for every new agent

1. Read `AGENTS.md`.
2. Read this file completely.
3. Read the newest entries of `docs/RESEARCH_LOG.md` backward until the current strategic pivot is understood.
4. Inspect PR #1, its latest commit, comments, and workflow state.
5. Compare the newest branch commits and result files against this snapshot.
6. Resolve any discrepancy before starting a new experiment.
7. Materialize the active target as a committed run specification.
8. Execute autonomously and checkpoint every material result.
9. Before ending, update this file and append the research log.

## 16. Compact current stopping point

```text
No Barnette counterexample is known.

The strongest exact object is a proof-certified cofacial ternary obstruction
x => y or z in a 100-vertex Barnette graph.

Exact AABCC pole compositions produce 65 planar cofacial binary-obstruction
near-counterexamples, all failing only 3-connectivity.

The first 655 correctly oriented C4 repairs all became Hamiltonian-compatible.

The six-terminal sampled-zero route was eliminated exactly by a recurring
nine-state compatibility kernel.

The exact 8-cycle annular Q block is a swap relation whose powers become full;
it is not an annihilating obstruction. Its original raw provenance still must
be recovered or reproduced.

The next attack is the sparsest remaining connectivity-repair family,
especially one-closure cases, with source 57 first materialized as a durable
repository object before further computation.
```
