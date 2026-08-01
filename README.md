# Barnette's Conjecture Counterexample Search

This repository develops reproducible computational searches for a counterexample to Barnette's conjecture:

> Every cubic, 3-connected, bipartite planar graph is Hamiltonian.

The project treats solver timeouts only as unresolved cases. A counterexample claim requires all graph-class predicates to be independently validated and non-Hamiltonicity to be supported by a machine-checkable exact certificate.

## Operating model

This is an agent-operated research repository. Agents are responsible for the complete execution loop: research planning, code changes, experiments, validation, commits, branch publication, pull-request maintenance, CI follow-up, artifact publication, documentation, and durable handoff.

Routine repository work must not be delegated to the repository owner. The owner is not expected to run commands, push commits, open or update pull requests, monitor workflows, upload evidence, or reconstruct lost context.

Research code and results are maintained through agent-managed branches, commits, automated workflows, and pull requests. When a specific operation is unavailable to an agent, the agent must preserve a complete authoritative branch and PR state rather than transferring the task to the owner.

## Agent handoff

Any agent continuing the project must begin with:

- [`AGENTS.md`](AGENTS.md) — authoritative current state, autonomous operating policy, validation rules, checkpoint protocol, and next experiment;
- [`agent.md`](agent.md) — compact entry point for tools expecting that filename;
- [`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md) — append-only chronological record of experiments, corrections, and analytical pivots.

No material result should remain only in chat history, terminal output, local scratch files, or an uncommitted workspace.