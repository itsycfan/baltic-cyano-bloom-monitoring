# Agent instructions

This repository follows `template-rq-driven-research`'s SOP-1 / SOP-2 (see the root `README.md` for the full diagrams and narrative). If you are an AI assistant (Codex, Claude Code, or similar) working in this repo, follow these conventions without being asked each time:

## Always

- Read `docs/02_proposal.md` and `docs/RQ_MAPPING.md` first, in that order, before touching code. They define which research question (RQ) any given piece of work belongs to.
- Every experiment, script, or non-trivial code change belongs to exactly one RQ. If it doesn't, stop and ask whether it belongs in `docs/00_project_definition.md` (scope) instead.
- After resolving a non-trivial bug, or making a decision between two or more real options (a library, an architecture, a hyperparameter search strategy), append one entry to `docs/DEV_LOG.md` in the format already at the top of that file. Do this immediately, not at session end — the reasoning is easiest to capture right after making the call.
- When an RQ's status changes (OPEN → TESTING → CONCLUDE, or "carried forward"), update `docs/RQ_MAPPING.md` in the same commit as the work that caused the change.
- Commit at a meaningful granularity with a message that says what changed and why. Tag the commit when an RQ reaches CONCLUDE (`git tag rqN-concluded`) and when the Roadmap/Framework is confirmed (`git tag vFinal`).
- Never rewrite existing git history (no `rebase -i`, no `push --force`) on this repository.

## Never

- Don't invent a new top-level folder without updating the structure table in `README.md`.
- Don't commit anything under `data/` (see `.gitignore`) — only `demo_data/` is tracked.
- Don't compile or restructure the Word report / PPT in `reports/` until the Roadmap/Framework has actually been confirmed (`docs/CHANGELOG.md` has an entry) — it is a snapshot of a concluded state, not a running draft.

## When starting a brand-new project from this template

Confirm with the person that `docs/00_project_definition.md` has been filled in before doing anything else. An empty definition doc means SOP-1 hasn't started yet.
