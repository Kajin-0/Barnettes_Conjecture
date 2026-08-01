# Barnette's Conjecture Counterexample Search

This repository develops reproducible computational searches for a counterexample to Barnette's conjecture:

> Every cubic, 3-connected, bipartite planar graph is Hamiltonian.

The project treats solver timeouts only as unresolved cases. A counterexample claim requires all graph-class predicates to be independently validated and non-Hamiltonicity to be supported by a machine-checkable exact certificate.

Research code and experimental results are developed through reviewable branches and pull requests.

## Agent handoff

Any agent continuing the project must begin with:

- [`AGENTS.md`](AGENTS.md) — authoritative current state, validation policy, checkpoint protocol, and next experiment;
- [`agent.md`](agent.md) — compact entry point for tools expecting that filename;
- [`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md) — append-only chronological record of experiments, corrections, and analytical pivots.

No material result should remain only in chat history, terminal output, local scratch files, or an uncommitted workspace.