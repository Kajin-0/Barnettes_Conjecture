# Canonical Current Research State

**Repository:** `Kajin-0/Barnettes_Conjecture`  
**Authoritative branch:** `agent/adversarial-search-v2`  
**Authoritative pull request:** PR #1  
**Snapshot timestamp:** 2026-08-03 16:42 UTC  
**Counterexample found:** No

This file is the single canonical mutable snapshot of the project. It must match the newest committed results, reports, PR checkpoints, branch state, and completed workflows.

`docs/RESEARCH_LOG.md` is the append-only chronology. This file records the current interpretation and active direction.

## 1. State-retention invariant

A material result or analytical pivot is not incorporated until the active agent has completed every applicable part of this transaction:

1. update this file;
2. append `docs/RESEARCH_LOG.md`;
3. publish machine-readable evidence under `results/YYYY-MM-DD/`;
4. update or add the technical report and run specification;
5. update PR #1 through its body or a checkpoint comment;
6. commit and publish all changes.

No important result may exist only in chat, private reasoning, terminal output, an Actions log, a PR discussion, an auxiliary branch, or an uncommitted file.

## 2. Objective and proof standard

Barnette's conjecture states:

> Every simple cubic 3-connected bipartite planar graph is Hamiltonian.

A counterexample claim requires:

1. independent verification of simplicity, cubicity, bipartiteness, planarity, and vertex connectivity at least three;
2. exact whole-graph non-Hamiltonicity;
3. a machine-checkable UNSAT proof, preferably CaDiCaL DRAT/LRAT accepted by an independent checker;
4. a second independent Hamiltonian encoding or transparent exact decomposition check;
5. complete source, construction, software, parameter, hash, and workflow provenance.

Timeouts, interrupted runs, malformed cases, heuristic misses, and single-solver infeasibility statuses are always `unknown`.

## 3. Primary strategic direction: face-internal ternary amplification

The previous canonical route was:

```text
certified H^{+--}
    -> connectivity-two five-pole H^{+-} near-counterexample
    -> repair the two-cut
    -> Kelmans amplification
```

That route remains a fallback, but it is no longer primary.

The strongest current route is:

```text
proof-certified cofacial H^{+--} in an existing 3-connected Barnette graph
    -> insert a planar bipartite cubic selector patch inside the same face
    -> force every global Hamiltonian trace into the certified forbidden state
    -> obtain a closed non-Hamiltonian Barnette graph directly
```

The inserted patch must preserve simplicity, cubicity, bipartiteness, planarity, and 3-connectivity. If every Hamiltonian cycle of the expanded graph would restrict to a source cycle containing `x` and avoiding `y,z`, the expanded graph is non-Hamiltonian by the existing certified obstruction.

This route is documented in:

- `docs/FACE_INTERNAL_TERNARY_AMPLIFIER_2026-08-03.md`
- `docs/runs/2026-08-03-face-internal-ternary-amplifier.md`

### Why this is the strongest route

1. The source graph is already a verified 3-connected Barnette graph.
2. The obstruction is already exact and DRAT-certified.
3. A face patch can attach through three or more separated boundary regions, making 3-connectivity structurally easier than repairing an existing two-cut.
4. The construction can produce the final non-Hamiltonian graph directly, without first deriving a binary obstruction.
5. Historical strengthening results identify a three-edge facial failure as an equivalent route to disproving Barnette's conjecture.
6. The completed source-2 repair family showed that generic post hoc `C4` repair is too permissive: it restored the forbidden Hamiltonian trace in every case.

## 4. Immediate executable sequence

### Phase 0: consecutive facial ternary scan

Exhaustively test every facial three-edge path `(a,b,c)` for a Hamiltonian cycle with:

```text
a excluded
b included
c excluded
```

Search order:

1. all facial paths in canonical order-100 candidate 489;
2. all facial paths in the 12 retained Grand-v3 order-96 parents;
3. all facial paths in the 12 retained Grand-v3 order-100 parents.

Every positive requires an explicit independently checked Hamiltonian-cycle witness. Every negative requires CaDiCaL plus checked DRAT/LRAT.

A certified consecutive triple is theorem-complete: instantiate the explicit face construction associated with the strengthened equivalent formulation and send the resulting closed graph directly to whole-graph proof.

### Phase 1: exact face-2 trace language

If Phase 0 produces no negative, compute the exact Hamiltonian boundary language of candidate 489's 12-edge face 2.

First enumerate all `4096` face-edge inclusion masks. Then refine feasible masks by the induced connectivity pairing of opened boundary path segments.

Positive states require witnesses. Negative states used in synthesis require checked proofs.

### Phase 2: face-patch synthesis

Generate planar bipartite subcubic patches in increasing even internal order:

```text
4, 6, 8, ..., 24
```

Hard constraints:

- prescribed terminal cyclic order and bipartition colors;
- correct residual terminal degrees;
- internal degree three;
- simple cubic glued graph;
- planar embedding with even internal faces;
- glued vertex connectivity at least three.

Exact objective:

```text
L_source compose L_patch = empty
```

Preferred explanatory objective:

```text
Every compatible global trace forces x=1, y=0, z=0.
```

Use counterexample-guided inductive synthesis: propose a patch, obtain and validate any Hamiltonian witness, project its boundary trace, block that trace family, and iterate. A final candidate must be rebuilt and certified independently.

### Phase 3: final proof bundle

A graph may be called a counterexample only after the repository contains:

1. graph6 and sorted edge list;
2. planar rotation system and face data;
3. independent Barnette-predicate checks;
4. complete construction manifest;
5. source and output hashes;
6. independently generated Hamiltonian CNF;
7. solver UNSAT result and textual DRAT/LRAT;
8. independent proof-checker success;
9. second independent encoding or exact decomposition verification;
10. clean GitHub Actions reproduction.

## 5. Strongest certified source: order-100 candidate 489

Candidate 489 is a verified simple cubic bipartite planar 3-connected graph with 100 vertices and 150 edges.

On face 2, whose cyclic vertex order is

```text
5, 10, 17, 25, 35, 48, 40, 30, 22, 14, 18, 11
```

the principal certified triple is

```text
x = (14,18)
y = (10,17)
z = (5,11)
```

No Hamiltonian cycle contains `x` while avoiding both `y` and `z`.

Six cofacial cases were solved UNSAT by CaDiCaL 3.0.1 and their textual DRAT proofs were accepted by `drat-trim`.

Evidence:

- `results/2026-08-02/three_edge_face_candidates.json`
- `search/sat_verify_face_constraints.py`
- `.github/workflows/face-three-edge-proof.yml`
- workflow run `30750008325`
- artifact `8834131003`
- artifact SHA-256 `0aab9f4cdcd8ed61467f2a11de3d764e2dfc410b61b28a48ada61581ca9c1da1`

Classification: `verified`.

One-copy closure analysis found that every alternative planar bipartite closure had vertex connectivity two; the only alternative 3-connected closure was nonplanar. Therefore a direct multi-attachment face amplifier or multi-copy assembly is required.

## 6. Exact six-pole languages and five-pole near-counterexamples

Three certified ternary cases supplied poles `A`, `B`, and `C`. Each was completed over the full 75-state boundary space by exhaustive perfect-matching recursion.

| Pole | Positive | Exact negative | Unknown |
|---|---:|---:|---:|
| A | 26 | 49 | 0 |
| B | 26 | 49 | 0 |
| C | 26 | 49 | 0 |

Permanent correction:

```text
Pole C realizes mask 63 with pairing (0,1)(2,5)(3,4).
```

The omission of that state from an earlier positive underapproximation invalidated a false zero-language interpretation. Negative composition claims must use complete exact languages.

Exact-language SHA-256:

```text
4c167dd746a9afb4ecee982fd989dc141d5b577df0921f3e503d478b1a856863
```

Corrected `AABCC` synthesis over 100,000 terminal permutations produced:

| Stage | Count |
|---|---:|
| Exact zero `X+e-` languages | 9,818 |
| Legal and copy-connected | 2,597 |
| Planar | 122 |
| Planar with `X,e` cofacial | 65 |
| 3-connected | 0 |

All 65 cofacial near-counterexamples have connectivity exactly two. They remain a useful fallback library, but post hoc repair is not the primary attack.

Evidence:

- `docs/EXACT_SIX_POLE_AND_CONNECTIVITY_REPAIR_2026-08-02.md`
- `results/2026-08-02/exact_six_pole_and_repair_summary.json`

## 7. Completed source-2 repair family

Source 2 had separator `(17,400)`, component sizes `99/399`, `X=(5,110)`, and `e=(11,105)`.

Correctly oriented separator-crossing `C4` expansion produced 655 graphs. Every graph passed simplicity, cubicity, bipartiteness, planarity, and 3-connectivity, becoming a 504-vertex Barnette graph.

Every one of the 655 graphs nevertheless admitted the forbidden-compatible `X+e-` Hamiltonian trace.

```text
source-2 repair family: completely eliminated
```

This proves that the tested generic repair geometry restores too much Hamiltonian flexibility. It does not refute the ternary-obstruction program.

The previously discussed source-57 one-closure target remains unmaterialized in the authoritative branch. Before it can be used as a fallback, it must be committed with graph encoding, pole permutation, separator, target edges, exact closure, repair specification, and reproduction command.

## 8. Grand Q-first v3 closure

Workflow run `30810878974` completed.

| Order | Parents | Patch sides | Q states | Positive | Missing | Unknown |
|---|---:|---:|---:|---:|---:|---:|
| 96 | 12 | 16,852 | 33,704 | 33,704 | 0 | 0 |
| 100 | 12 | 18,892 | 37,784 | 37,784 | 0 | 0 |
| **Total** | **24** | **35,744** | **71,488** | **71,488** | **0** | **0** |

Artifacts:

- order 96: artifact `8859456435`, SHA-256 `dc0db45b6e862437a04d1a4b2f8b192bc7d905682b4ece86d772e6f10bb73bb3`;
- order 100: artifact `8860190315`, SHA-256 `be7d0927c32594829115354db2788c5992bf69c720c41ff9e7641ee99d30514f`.

The 16 repaired order-94/order-98 residue jobs completed operationally, but downstream Q analysis was skipped because the generated shards supplied no actionable parent inputs under the workflow conditions. This has no mathematical negative interpretation.

Machine-readable closure:

- `results/2026-08-03/grand_q_first_v3_broad_closure.json`

Strategic conclusion:

```text
Ordinary natural four-terminal missing-Q search is retired as an active
breakthrough route for these parent sets.
```

## 9. Exact six-terminal tail

The six-terminal pilot sampled 4,594 cut-side patches. Apparent sampled zeros disappeared under exact enumeration.

Nine strongest patches had 23 or 24 exact states after enumerating 56,230 to 240,078 perfect matchings each. Across 540 exact patch-pair/dihedral-map comparisons:

```text
minimum compatibility = 9
incompatible exact gluings = 0
```

All nine shared the exact nine-state kernel recorded in:

- `docs/SIX_TERMINAL_EXACT_TAIL_2026-08-03.md`
- `results/2026-08-03/six_terminal_exact_tail_summary.json`
- summary SHA-256 `5a83c3b453b81be1e4327d7dd94f00918f43eb3c267aad69f18f034833fc3689`.

Consequence:

```text
few randomized matching hits != sparse exact boundary language
```

Matching rarity is retired as a primary search objective.

## 10. Annular transfer state

Natural annular relations exhibit exact correlations, but no tested composition annihilated the language.

The tracked PR reported an exact 8-cycle `Q` swap:

```text
Q01_23 -> Q03_12
Q03_12 -> Q01_23
```

with full relation cardinalities `14`, `28`, and `36` for `R`, `R^2`, and `R^3`. The reported Boolean closure had 834 relations, no empty product, minimum cardinality 13, and stabilization by depth six.

That result is preserved as provenance-incomplete because its original raw 300-annulus output and semigroup artifact were not located:

- `docs/ANNULAR_SWAP_SEMIGROUP_CHECKPOINT_2026-08-03.md`
- `results/2026-08-03/annular_swap_semigroup_checkpoint.json`

Repeated composition of this swap is not an active route because it increases flexibility.

## 11. Permanent warnings and retractions

### SciPy/HiGHS false infeasibility

SciPy 1.17.0 falsely reported missing states `c156-s0:P23` and `c446-s1:P01`. SciPy 1.18.0 produced valid witnesses. A single MILP infeasibility status is never proof.

### Multi-parent key collision

The first higher-order driver keyed tasks only as `c<cut>-s<side>` and could overwrite different parent cases. Only `g<graph>-c<cut>-s<side>` output is authoritative.

### Exact-language underapproximation

Positive underapproximations cannot establish a negative composition. The pole-C correction is permanent.

### Orientation-sensitive repair

Endpoint sorting can destroy directed bipartite face-edge orientation. Repair and face-patch generators must retain oriented embedding roles.

### PR-only evidence

PR prose is not reproducible evidence. Every such claim must be copied into a dated report and machine-readable checkpoint with explicit provenance.

## 12. Retired or strongly deprioritized strategies

Do not restart without a new mathematical reason:

1. random matching fragmentation as evidence of non-Hamiltonicity;
2. increasing matching samples as a proxy for exact language sparsity;
3. ordinary natural four-terminal missing-Q search as the sole attack;
4. direct six-terminal gluing based on sampled zeros;
5. unrestricted adjacent-edge-deletion four-poles;
6. repeated composition of the 8-cycle annular swap;
7. the completed source-2 `C4` repair family;
8. generic post hoc repair as the primary strategy;
9. blind growth to larger graphs without an exact obstruction objective.

## 13. Fallback hierarchy

If no face amplifier is found through 24 internal vertices:

1. perform relation-first SAT synthesis of larger face patches;
2. synthesize a multi-copy composition whose skeleton is constrained to be 3-connected before instantiation;
3. use exact 26-state pole languages jointly with topology constraints;
4. then materialize and attack source-57 one-closure repair;
5. send every zero-language Barnette assembly directly to whole-graph proof-producing SAT.

The essential rule is:

```text
3-connectivity is a hard synthesis constraint, not a property repaired after
an exact obstruction has already been assembled.
```

## 14. Repository integration debt

Still-valid unique material remains on diverged branches:

| Branch | Unique material |
|---|---|
| `agent/matching-q-reduction` | matching-Q exact-tail implementation/evidence |
| `agent/proof-regression-checkpoint` | SAT/DRAT regression certificates |
| `agent/six-terminal-interface` | six-terminal code and workflow |
| `agent/higher-order-q-results` | detailed higher-order checkpoint |
| `agent/order94-98-expansion-fallback` | exact-order fallback generator |
| `agent/whole-graph-sat-proof` | whole-graph proof-producing Hamiltonian verifier |

Do not merge these branches wholesale. Port still-valid files selectively, preserve hashes, and rerun regressions.

The whole-graph SAT verifier is directly relevant to the face-amplifier campaign and should be integrated early.

## 15. Canonical evidence map

| Topic | Report | Machine-readable evidence |
|---|---|---|
| Primary amplifier strategy | `docs/FACE_INTERNAL_TERNARY_AMPLIFIER_2026-08-03.md` | run specification under `docs/runs/` |
| Grand Q-first v3 closure | strategy report above | `results/2026-08-03/grand_q_first_v3_broad_closure.json` |
| Ternary obstruction | `docs/EXACT_SIX_POLE_AND_CONNECTIVITY_REPAIR_2026-08-02.md` | `results/2026-08-02/three_edge_face_candidates.json` |
| Exact poles/source-2 repair | same report | `results/2026-08-02/exact_six_pole_and_repair_summary.json` |
| Exact six-terminal tail | `docs/SIX_TERMINAL_EXACT_TAIL_2026-08-03.md` | `results/2026-08-03/six_terminal_exact_tail_summary.json` |
| Higher-order Q-first v2 | `docs/HIGHER_ORDER_Q_FIRST_V2_2026-08-01.md` | `results/2026-08-01/higher_order_q_first_v2_summary.json` |
| Order-92 structural search | `docs/CANONICAL_STRUCTURAL_SEARCH_2026-08-01.md` | `results/2026-08-01/canonical_structural_summary.json` |
| Annular checkpoint | `docs/ANNULAR_SWAP_SEMIGROUP_CHECKPOINT_2026-08-03.md` | `results/2026-08-03/annular_swap_semigroup_checkpoint.json` |
| Solver retraction | canonical report | `results/2026-08-01/solver_discrepancy_retraction.json` |

## 16. Mandatory pickup sequence

1. Read `AGENTS.md`.
2. Read this file completely.
3. Read the newest entries of `docs/RESEARCH_LOG.md`.
4. Inspect PR #1 and current workflows.
5. Verify this snapshot against the newest commits and artifacts.
6. Read the face-amplifier report and run specification.
7. begin with the consecutive-triple scan;
8. checkpoint every result immediately.

## 17. Compact stopping point

```text
No Barnette counterexample is currently known.

The strongest exact object is a DRAT-certified cofacial three-edge obstruction
in a 100-vertex Barnette graph.

Grand Q-first v3 tested 71,488 natural cut-side Q states in 24 retained
order-96/order-100 parents; all 71,488 were positive.

Exact six-terminal sampled-zero candidates remained highly compatible.

Five-copy exact compositions produce 65 cofacial binary-obstruction
near-counterexamples, but all have connectivity two. The first 655 repairs all
restored the forbidden Hamiltonian trace.

The primary attack is now a connectivity-first face-internal ternary amplifier:
retain the original 3-connected source and synthesize a patch whose exact
boundary language has empty composition with the source.

First execute the exhaustive consecutive facial H^{+--} scan. If it has no
certified negative, compute the exact 12-edge face language and begin CEGIS
patch synthesis.
```
