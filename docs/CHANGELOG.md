# Roadmap / Framework Changelog

> One entry per meaningful revision of the Research Roadmap or Technical Framework in `02_proposal.md`. The point is to record *why* it changed, which a renamed file or an "(old version)" copy in `archive/` never does. Pair each entry with a git tag.

## v0-proposal — YYYY-MM-DD

Initial Roadmap and Framework, from the Proposal. See `git tag v0-proposal`.

## v0.1-stage0 — 2026-09-25

Revisions after the Stage 0 data audit (see `experiments/stage0_data_audit/`). See `git tag v0.1-stage0`.

- **Main series defined:** one complete sample per ISO week (closest to Tuesday 12:00); supplementary rare-class samples for sensitivity only; one incomplete sample excluded. Reason: supplementary samples are not a random draw.
- ***Nodularia spumigena* evaluated as detection, not as a curve:** it stays a primary and high-risk target, but it has at most 2 images per main-series sample. Curve metrics now centre on the N-fixing total, *Aphanizomenon* and *Dolichospermum*.
- **Onset defined:** thresholds 1%, 2% and 5% fixed in advance, searched from June to September. Reason: small winter samples create a 1 to 3% background that would trigger onset in January.
- **Validation split:** pseudo-sample blocks of contiguous indices, because training filenames have no sample ID.

## vFinal — YYYY-MM-DD

*What changed relative to v0, and why (which RQ result forced the change). See `git tag vFinal`.*
