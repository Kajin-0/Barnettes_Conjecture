# Adversarial Barnette Counterexample Search — 2026-08-01

## Result

No counterexample was found. The strongest candidates were difficult for the chosen heuristics but each has an explicit, independently validated Hamiltonian cycle. Solver timeouts were never treated as evidence of non-Hamiltonicity.

## Why this run was different

The previous search emphasized large faces and difficult expansion histories. This run optimized a more direct obstruction surrogate. For a cubic graph, the complement of every perfect matching is a spanning 2-factor. The graph is Hamiltonian exactly when at least one such complement has one component. The evolutionary objective therefore rewarded candidates for which randomized perfect matchings produced highly fragmented complements.

The search retained a beam of 10 candidates, generated 10 children per parent for 10 generations, and evaluated 978 new candidates through order 264. Each candidate received 512 randomized perfect-matching trials. The two leaders in every generation were then tested using a single-commodity-flow MILP enforcing a connected degree-2 spanning subgraph.

## Quantitative outcome

| Metric | Value |
|---|---:|
| New candidates evaluated | 978 |
| Maximum order | 264 vertices |
| Random matching evaluations | approximately 500,000 |
| Generation leaders exact-tested | 20 |
| Leaders with explicit Hamiltonian cycles | 20 |
| Additional validated finalist cycles | 15 |
| Same-face forced-in/forced-out tests | 72 |
| Proven edge-pair obstructions | 0 |
| Four-terminal patches scored in pilot | 276 |
| Exact patch signatures completed in follow-up | 1 |
| Counterexamples found | 0 |

## Strongest finalist

Candidate `n264-823d1137eea6f837` has 264 vertices and 396 edges. In 512 randomized perfect matchings:

- Hamiltonian complements found: 0
- minimum complementary 2-factor components: 27
- 5th percentile: 30 components
- median: 36 components
- mean: 36.121 components

Its embedding has 134 faces, maximum face size 110, four faces of size at least 10, and a maximum of six large-face neighbors. A dual separating-triangle check found no cyclic 3-edge cut, so the graph is cyclically 4-connected. A 10,000-pair sample found no failure of 2-extendability, although that sampling test is not a proof that the graph is a brace.

Despite its fragmented matching landscape, the exact flow MILP produced Hamiltonian cycles. Five distinct cycles were validated. The initial 24 same-face edge-pair tests contained eight 2-second timeouts; all eight were rerun with a 20-second solver budget and all eight produced valid constrained Hamiltonian cycles. The second-ranked finalist's four timeouts were likewise resolved. Thus all 48 selected same-face constraints on the top two finalists have explicit witnesses.

## Four-terminal patch-composition attempt

A second route searched for a compositional obstruction across a cyclic 4-edge cut. Deleting the endpoints of an edge creates a planar four-terminal patch. Its exact Hamiltonian boundary signature has nine possible states:

- six spanning Hamilton paths indexed by their two exposed terminals;
- three spanning two-path covers indexed by terminal pairing.

Two patches can be glued only if their exact signatures contain compatible states under the selected boundary map. If both signatures are complete and no compatible state exists, the glued graph is non-Hamiltonian by construction, after which the full graph must still be independently validated.

The pilot scored 276 patches and produced 42 apparently incompatible gluings under sampled signatures, but the sampling phase had found no Hamiltonian cycles and therefore under-approximated the true signatures. An exact 10-second-per-state analysis of patch `g2-e0-14` completed all nine decisions and found six feasible states:

`P02, P03, P12, P13, Q01_23, Q03_12`.

Both bipartition-preserving dihedral gluings had compatible states. This candidate patch therefore cannot create the desired obstruction with itself. No counterexample arose from the pilot.

## What is conclusive

Positive Hamiltonian findings are conclusive for the included graph instances because every certificate is checked for:

1. exactly `n` selected graph edges;
2. degree two at every vertex;
3. one connected component;
4. all Barnette-class predicates: simple, cubic, bipartite, planar, and vertex connectivity at least three.

The search as a whole is not exhaustive. It does not extend the published exhaustive frontier. It sampled expansion histories and used heuristic evolutionary selection.

## Highest-value next experiment

The next run should combine canonical generation with obstruction-first filtering:

1. Compile plantri 5.8.
2. Generate canonical cyclically 4-connected Barnette graphs directly as duals of 4-connected Eulerian triangulations. For a target dual order `n`, use the form `plantri -bc4dg n"d"` (for example, `plantri -bc4dg 92d`). Use `res/mod` shards for parallel enumeration.
3. Reject graphs covered by known sufficient Hamiltonicity subclasses.
4. Compute fast matching-fragmentation statistics and retain only the extreme tail.
5. Search exact four-terminal signatures on low-entropy edges.
6. Run Hamiltonicity SAT with proof logging on the survivors. Any UNSAT result must be checked independently with DRAT/LRAT tooling before a mathematical claim is made.

A more ambitious route is to encode the graph and the absence of a Hamiltonian cycle in one quantified or cutting-plane search. The structural generator should enforce planarity through an Eulerian triangulation or rotation-system representation rather than testing arbitrary cubic bipartite graphs after generation.

## Reproduction

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python search/adversarial_evolution.py \
  --verified data/verified_search_results.json \
  --fragility data/matching_fragility_1000.json \
  --output-dir results/run \
  --seed-count 8 --beam 10 --children-per-parent 10 \
  --generations 10 --matching-trials 512 --workers 4 \
  --exact-top 2 --exact-time 12 \
  --cycle-enumeration 5 --cycle-time 8 \
  --pair-tests 24 --pair-time 2 --seed 20260801
```

Verify the included finalist certificate:

```bash
python verify_certificate.py \
  results/2026-08-01/finalist_1.graph6 \
  results/2026-08-01/finalist_1_hamiltonian_cycle.json
```

## Limitations

- No direct plantri enumeration was executed in the local runtime because the external binary was unavailable.
- Matching-fragmentation statistics depend on the matching sampler and are not invariant graph parameters.
- The 10,000 independent-edge-pair checks are empirical support for 2-extendability, not an exact brace certificate.
- Thirteen rank-3 same-face edge-pair tests remain unresolved at the original two-second budget; none is proven infeasible.
- The patch search examined a small pilot subset; its sampled signatures are not exact unless explicitly marked complete.
