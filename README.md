# Barnette's Conjecture Counterexample Search

This repository develops reproducible computational searches for a counterexample to Barnette's conjecture:

> Every cubic, 3-connected, bipartite planar graph is Hamiltonian.

The project treats solver timeouts, heuristic misses, interrupted computations, and single-solver infeasibility statuses as unresolved. A counterexample claim requires independent validation of all Barnette-class predicates and machine-checkable exact evidence of non-Hamiltonicity.

## Operating model

This is an agent-operated research repository. Agents are responsible for the complete execution loop: research planning, code and workflow changes, experiments, validation, commits, branch publication, pull-request maintenance, CI follow-up, artifact publication, documentation, and durable handoff.

Routine repository work must not be delegated to the repository owner.

## Required reading order

Every agent continuing the project must begin with:

1. [`AGENTS.md`](AGENTS.md) — mandatory operating, proof, checkpoint, and continuity rules;
2. [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) — single canonical mutable snapshot of the current mathematical state, strongest result, active target, retired directions, evidence map, and integration debt;
3. [`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md) — append-only chronological record of experiments, corrections, retractions, and analytical pivots;
4. [`agent.md`](agent.md) — compact entry point for tools expecting that filename.

## Continuity rule

No material result may remain only in chat history, private reasoning, terminal output, an Actions log, a PR comment, an auxiliary branch, or an uncommitted workspace.

After every material result, the active agent must update `docs/CURRENT_STATE.md`, append `docs/RESEARCH_LOG.md`, publish the applicable evidence and report, and checkpoint the authoritative pull request.

The current-state snapshot is the repository's durable handoff. It must be reconciled against the newest commits, results, PR comments, and workflow outcomes before new research begins and before a work session ends.