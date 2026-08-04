# Research checkpoint: dual face-substitution attack

**Timestamp:** 2026-08-04 02:04 UTC  
**Counterexample found:** No

## Decision

The next primary analytical route is dual, embedding-aware substitution synthesis around mandatory 10+-faces.

## Basis

- Candidate 489's planar dual has 52 vertices, all even degrees, and vertex connectivity 4.
- Face 2 becomes a degree-12 dual vertex.
- A primal Hamiltonian cycle is the cut of a dual face 2-coloring; its two color classes induce trees.
- The principal obstruction translates to one bichromatic and two monochromatic incident dual edges.
- Recent work proves Hamiltonicity for Barnette graphs whose faces all have size at most 8 and uses exact embedded graph substitutions. A counterexample must contain a 10+-face.
- Existing mixed-pole empty products fail because actual terminal rotations force nonplanarity. The dual formulation makes the rotation intrinsic.

## Implemented

1. `search/dual_face_cut_obstruction.py`
   - independent face-color/XOR Hamiltonicity encoding;
   - all eight principal triple patterns;
   - all six previously certified obstructions;
   - independent induced-tree and primal-cycle validation;
   - CaDiCaL textual DRAT and `drat-trim` verification for negatives.
2. `search/dual_face_implicate_scan.py`
   - complete width-1/2/3 scan on candidate 489's 12-, 30-, and 30-faces;
   - incremental exact connectivity cuts;
   - prime forbidden-pattern extraction;
   - proof escalation for the 32 most compact prime ternary clauses.
3. Workflows:
   - `.github/workflows/dual-face-cut-obstruction.yml`
   - `.github/workflows/dual-face-implicate-scan.yml`
4. Design report:
   - `docs/DUAL_FACE_SUBSTITUTION_ATTACK_2026-08-04.md`

## Next transaction

Run both campaigns in an isolated execution PR. Reconcile all checked artifacts into the authoritative branch. Then synthesize embedded disk substitutions whose exact boundary language is contained in a certified forbidden large-face relation.
