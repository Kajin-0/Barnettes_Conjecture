# Agent Entry Point

Read these files in order before continuing research:

```text
AGENTS.md
docs/CURRENT_STATE.md
docs/RESEARCH_LOG.md
```

- `AGENTS.md` defines the mandatory operating, proof, checkpoint, and continuity rules.
- `docs/CURRENT_STATE.md` is the single canonical mutable snapshot of the current research state and active target.
- `docs/RESEARCH_LOG.md` is the append-only chronological record.

Then inspect PR #1, its latest commit, comments, and workflow state. Compare those sources against `docs/CURRENT_STATE.md` and resolve any discrepancy before beginning new work.

This repository must be operated end to end by the active agent. Do not ask the repository owner to run commands, create branches, commit or push changes, open or update pull requests, monitor CI, upload artifacts, or maintain handoff documentation.

A material insight is not durably incorporated until the agent updates `docs/CURRENT_STATE.md`, appends `docs/RESEARCH_LOG.md`, publishes applicable evidence and reports, and checkpoints PR #1.

Before ending a session, leave the repository immediately reproducible and usable by the next agent. No critical result may exist only in chat, terminal output, an Actions log, a PR comment, an auxiliary branch, or an uncommitted workspace.