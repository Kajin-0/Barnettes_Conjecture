# Run specification: dual face-substitution attack

## Independent obstruction proof

```bash
python search/dual_face_cut_obstruction.py \
  --input results/2026-08-02/three_edge_face_candidates.json \
  --output-dir results/2026-08-04/dual-face-cut-obstruction \
  --solver g4 \
  --proof-solver tools/cadical/build/cadical \
  --drat-trim tools/drat-trim/drat-trim \
  --max-rounds 10000 \
  --proof-timeout 1800
```

Required checks:

- source remains a Barnette graph;
- dual is a simple even plane triangulation;
- principal dual vertex has degree 12;
- all eight principal patterns are classified;
- all six source negatives are independently proof-certified;
- no unknown or provisional case remains;
- every positive has both an explicit Hamiltonian cycle and two induced dual trees.

## Large-face implicate scan

```bash
python search/dual_face_implicate_scan.py \
  --input results/2026-08-02/three_edge_face_candidates.json \
  --output-dir results/2026-08-04/dual-face-implicate-scan \
  --solver g4 \
  --min-face-size 10 \
  --max-width 3 \
  --max-rounds 10000 \
  --proof-limit 32 \
  --proof-solver tools/cadical/build/cadical \
  --drat-trim tools/drat-trim/drat-trim \
  --proof-timeout 1800
```

Required checks:

- face sizes scanned are exactly 12, 30, and 30;
- all width-1/2/3 assignments are classified;
- no unknown remains;
- every selected prime ternary negative is reproduced by CaDiCaL and accepted by `drat-trim`;
- prime clauses retain face index, cyclic edge positions, cyclic span, and gap signature.

## Interpretation policy

The incremental solver's UNSAT results are discovery records until proof escalation. Only `certified_negative` results enter the permanent obstruction library. A positive is accepted only with a validated explicit cycle.
