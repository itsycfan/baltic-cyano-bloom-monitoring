# Roadmap / Framework Changelog

> One entry per meaningful revision of the Research Roadmap or Technical Framework in `02_proposal.md`. The point is to record *why* it changed, which a renamed file or an "(old version)" copy never does. Pair each entry with a git tag.

## v0-proposal — 2026-09-25

Initial Roadmap and Framework, from the Proposal. See `git tag v0-proposal`.

## v0.1-stage0 — 2026-09-25

Revisions after the Stage 0 data audit (see `experiments/stage0_data_audit/`). See `git tag v0.1-stage0`.

- **Main series defined:** one complete sample per ISO week (closest to Tuesday 12:00); supplementary rare-class samples for sensitivity only; one incomplete sample excluded. Reason: supplementary samples are not a random draw.
- ***Nodularia spumigena* evaluated as detection, not as a curve:** it stays a primary and high-risk target, but it has at most 2 images per main-series sample. Curve metrics now centre on the N-fixing total, *Aphanizomenon* and *Dolichospermum*.
- **Onset defined:** thresholds 1%, 2% and 5% fixed in advance, searched from June to September. Reason: small winter samples create a 1 to 3% background that would trigger onset in January. *(Note added 2026-10-02: the area-weighted analysis showed this background is a few large filaments in a sparse winter community, not a small-sample artefact; the window itself is unchanged.)*
- **Validation split:** pseudo-sample blocks of contiguous indices, because training filenames have no sample ID. *(Superseded in vFinal: the index-adjacency check failed and a stratified random split was used.)*

## vFinal — 2026-10-02

Roadmap and Framework after RQ1 to RQ3 concluded. See `git tag vFinal` (v0 at `v0-proposal`).

**Roadmap**
- All four stages completed; the optional BioCLIP 2 zero-shot ablation was not run (outside the scope rule; future work).
- Added a pre-registered analysis plan (`ANALYSIS_PLAN.md`) before any 2021 evaluation, with two addenda written before running: class-specific threshold check and area-weighted abundance. Reason: decisions were made without the author present; pre-registration keeps the 2021 test clean.
- Added a methodological positioning and a scope rule to `02_proposal.md`. Reason: after reading Kraft et al. (2022), new comparisons risked being added ad hoc; the rule admits only comparisons required by an RQ or needed to test a stated conclusion.
- Target output changed from the CVC 2027 conference paper to an open preprint (arXiv, EarthArXiv) with code archived on Zenodo; double-blind constraints dropped.

**Framework**
- Validation split: stratified random 80/20 instead of index blocks. Reason: the index-adjacency check showed training indices carry no acquisition order.
- Representation: DINOv2 is the primary feature set; no fusion adopted (T1, validation only). The all-four fusion was best on 2021 and is reported as a finding, not used.
- Decision layer: class-balanced weights kept alongside unweighted ones in all results. Reason (RQ2): contrary to v0's expectation, balanced weights halve abundance error because the bloom taxa are the largest training classes.
- Calibration (T2): temperature scaling kept, with the finding that it helps on 2021 only when T > 1.
- Policy layer: unchanged; distance signal kept under the pre-registered exception (post hoc check: removing it raises workload).
- Evaluation: *N. spumigena* as a detection task; CC error decomposition (post hoc, descriptive); two validity checks; matched-workload baselines for review.
- Limitations extended (weekly resolution, review latency, frozen backbones) and future work listed as tentative.
