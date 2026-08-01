# Higher-Order Q-First Canonical Campaign

**Date:** 2026-08-01  
**Status:** active  
**Counterexample found at campaign start:** no

## Objective

Search the first higher canonical orders for a natural cyclic-4-cut patch with an independently certified missing noncrossing two-path boundary state.

The primary progress metric is

```text
number of independently certified missing noncrossing Q states
```

The value at campaign start is zero.

## Hypothesis

The order-92 leading graph had maximal four-terminal signatures on every natural cyclic-4-cut side. A restrictive patch may first appear at a larger order, or in a different canonical shard, and should be detected most efficiently by testing the two noncrossing `Q` states before any path states.

## Scope

Target graph orders:

```text
94, 96, 98, 100
```

For each order:

- generate 12 disjoint plantri `res/mod` shards;
- retain up to 400 canonical graph6 outputs per shard;
- deduplicate all retained outputs;
- validate order, cubicity, bipartiteness, connectivity, and planarity;
- apply the implemented face-size and big-face-neighbour sufficient-condition filters;
- rank survivors using perfect-matching-complement fragmentation only as a heuristic;
- retain the six leading graphs;
- enumerate all natural cyclic 4-edge cuts in each retained graph;
- select up to 320 deterministic, side-size-diverse cut sides per graph;
- solve `Q01_23` and `Q03_12` first.

The planned maximum initial screening volume is:

```text
4 orders x 6 graphs x 320 patches x 2 Q states = 15,360 Q-state attempts
```

Actual counts may be lower when fewer cuts or theorem-escaping graphs are available.

## Generator

Official plantri 5.8:

```text
archive SHA-256:
e78a944116fec9f2c9f5e484206276cc2b0043bae803e9815f4b2683614629b8

command form:
plantri -bc4dg ORDERd RES/10000
```

Shard residues:

```text
0, 137, 911, 1597, 2718, 4093,
5003, 6121, 7351, 8123, 9001, 9733
```

Each shard is capped at 400 retained outputs and bounded by an external wall-clock timeout. A truncated shard is a sample, not an exhaustive residue class.

## Positive-state acceptance

A positive `Q` state is accepted only when its selected-edge witness independently passes all of the following:

1. every selected edge belongs to the patch;
2. no selected edge is duplicated;
3. every terminal has selected degree one;
4. every internal vertex has selected degree two;
5. the selected subgraph has exactly two connected components;
6. the two components induce the requested terminal pairing;
7. the selected edge count is `|V(P)| - 2`.

## Negative-state policy

A MILP infeasibility status is classified only as `provisional_negative`.

Every provisional negative or unresolved case is passed to an independent SAT formulation using:

- selected-edge variables;
- exact degree constraints;
- a binary component partition fixed by the requested terminal pairing;
- lazy connectivity cuts;
- proof logging.

A state is classified as a certified missing `Q` state only when:

1. the final SAT instance is UNSAT;
2. a proof log is produced;
3. `drat-trim` independently verifies the proof;
4. the CNF, proof, checker output, patch data, and hashes are published.

SAT models are treated as positive witnesses and independently checked combinatorially. Timeouts, proof-generation failures, proof-check failures, malformed cases, and solver errors remain `unknown`.

## Software baseline

- Python 3.12;
- NetworkX 3.6.1;
- NumPy 2.x;
- SciPy 1.18.0;
- python-sat 1.9.dev5;
- official plantri 5.8;
- drat-trim built from its public source repository.

The workflow records installed versions and hashes in each artifact manifest.

## Expected outputs

For each order:

```text
results/higher-order-q-first/ORDER/
```

including:

- raw canonical shards;
- deduplicated graph6 sample;
- ranking and theorem-filter output;
- exact positive Q witnesses;
- provisional negative and unknown cases;
- SAT verification results;
- CNF and proof files for every attempted negative certification;
- proof-checker output;
- a run manifest with file hashes and software versions.

## Stop and escalation criteria

Immediately checkpoint and escalate when any of the following occurs:

- a positive MILP witness fails independent validation;
- a MILP negative is contradicted by SAT;
- a proof-checked missing `Q` state is found;
- an empty verified transfer product is found;
- an assembled graph passes all Barnette predicates and lacks a Hamiltonian cycle under proof-checked SAT;
- a solver-version discrepancy appears;
- the computation exceeds the intended scope or exhibits systematic failure.

A proof-certified missing `Q` state triggers exact completion of that patch's full boundary signature and a targeted composition search before broader enumeration continues.

## Repository operation

The agent owns branch management, commits, CI monitoring, artifact retrieval, failure correction, PR maintenance, and all research checkpoints. No routine action is assigned to the repository owner.
