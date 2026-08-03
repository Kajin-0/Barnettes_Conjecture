# 2026-08-03 16:42 UTC — Grand Q-first v3 Closure and Face-Internal Ternary-Amplifier Pivot

**Status:** `verified` for Grand-v3 positive-state counts; `provisional` strategic synthesis direction  
**Counterexample found:** No

## Objective

Select the strongest analytical direction capable of producing a complete, independently certified counterexample rather than another heuristic near-miss.

## New verified evidence

Grand Q-first v3 workflow run `30810878974` completed.

| Order | Parents | Patch sides | Q states | Verified positive | Missing | Unknown |
|---|---:|---:|---:|---:|---:|---:|
| 96 | 12 | 16,852 | 33,704 | 33,704 | 0 | 0 |
| 100 | 12 | 18,892 | 37,784 | 37,784 | 0 | 0 |
| **Total** | **24** | **35,744** | **71,488** | **71,488** | **0** | **0** |

Artifacts:

- order 96 artifact `8859456435`, SHA-256 `dc0db45b6e862437a04d1a4b2f8b192bc7d905682b4ece86d772e6f10bb73bb3`;
- order 100 artifact `8860190315`, SHA-256 `be7d0927c32594829115354db2788c5992bf69c720c41ff9e7641ee99d30514f`.

The 16 repaired order-94/order-98 generation jobs completed operationally, but downstream Q analysis was skipped because the resulting shards supplied no actionable parents under the workflow conditions. This remains mathematically `unknown` for those orders.

Machine-readable evidence:

- `results/2026-08-03/grand_q_first_v3_broad_closure.json`

## Strategic interpretation

Ordinary natural four-terminal missing-`Q` search has reached diminishing returns for the retained order-96/order-100 parents. Every one of 71,488 tested states was positively witnessed.

The exact six-terminal tail also showed that matching-zero patches retained 23 or 24 exact states and at least nine compatible states under every tested gluing. Matching rarity is therefore not a reliable distance-to-obstruction metric.

The first post hoc connectivity-repair family exposed a separate structural failure: all 655 repaired graphs satisfied the Barnette predicates, but every repair restored the forbidden Hamiltonian trace.

The project should therefore stop treating connectivity repair after a two-cut assembly as the primary route.

## Selected direction

Use **face-internal ternary amplification**.

Retain canonical order-100 candidate 489, which is already a verified 3-connected Barnette graph and contains a DRAT-certified cofacial obstruction:

```text
x = (14,18) included
y = (10,17) excluded
z = (5,11) excluded
```

No Hamiltonian cycle realizes that trace.

Insert a planar bipartite cubic selector patch inside the same face. Synthesize the patch so every hypothetical Hamiltonian cycle of the expanded graph restricts to the certified forbidden source trace.

The exact synthesis objective is:

```text
L_source compose L_patch = empty
```

The glued graph must be simple, cubic, bipartite, planar, and 3-connected. If those properties and whole-graph UNSAT are independently certified, the glued graph itself is the complete counterexample; no subsequent binary reduction or Kelmans amplification is required.

## Execution sequence

### Phase 0 — consecutive facial ternary scan

Exhaustively test every three-consecutive-edge facial path for a Hamiltonian cycle containing the middle edge and avoiding the outer two.

Search:

1. candidate 489;
2. the 12 Grand-v3 order-96 parents;
3. the 12 Grand-v3 order-100 parents.

Positive results require explicit validated cycles. Negative results require CaDiCaL and independently checked DRAT/LRAT.

### Phase 1 — exact source-face language

If Phase 0 has no certified negative, enumerate all `2^12 = 4096` face-edge masks for candidate 489 face 2, then refine states by induced boundary connectivity pairings.

### Phase 2 — connectivity-first patch synthesis

Generate patches with `4,6,8,...,24` internal vertices under hard embedding, parity, degree, simplicity, and 3-connectivity constraints.

Use counterexample-guided synthesis:

1. propose a legal patch;
2. solve the glued graph for a Hamiltonian cycle;
3. validate and project any witness to a boundary trace;
4. block the trace family;
5. repeat until topology UNSAT or whole-graph Hamiltonicity UNSAT.

### Phase 3 — complete certification

A result requires graph6, edge list, rotation system, construction manifest, independent Barnette-predicate checks, independently generated Hamiltonian CNF, proof-producing UNSAT, checked DRAT/LRAT, a second independent formulation, hashes, and clean CI reproduction.

## Fallback hierarchy

If bounded face-patch synthesis through 24 internal vertices fails:

1. relation-first synthesis of larger face patches;
2. exact multi-copy pole synthesis with 3-connectivity imposed before instantiation;
3. materialize and attack the discussion-derived source-57 one-closure family only afterward.

## Durable repository changes

- `docs/FACE_INTERNAL_TERNARY_AMPLIFIER_2026-08-03.md`
- `docs/runs/2026-08-03-face-internal-ternary-amplifier.md`
- `results/2026-08-03/grand_q_first_v3_broad_closure.json`
- updated `docs/CURRENT_STATE.md`
- updated `AGENTS.md`
- PR #1 strategic checkpoint comment `5169328062`

## Next action

Implement and run the exhaustive consecutive facial ternary scan. The first binary milestone is either:

```text
a checked consecutive H^{+--} obstruction
```

or:

```text
the complete exact candidate-489 face-2 trace language
```
