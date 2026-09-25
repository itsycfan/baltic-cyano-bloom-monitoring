# Developer & Decision Log

> Append-only. Write an entry the moment friction happens: a bug that took more than one try, a choice between two real options, an approach tried and abandoned. This log is what stops the same question from being re-asked (of a person or an AI assistant) three months from now, and it is the raw material `docs/CHANGELOG.md` and the eventual Word report draw on — don't wait to clean it up.

**Entry format:**

```
## YYYY-MM-DD — short title
RQ: RQ<n> (or "n/a — infra/tooling")
Problem / decision:
Root cause / options considered:
Resolution:
Rejected alternatives (if a decision, not a bug) and why:
```

---

<!-- entries below -->

## 2026-09-25 — Stage 0: main-series rule and exclusion of an incomplete 2021 sample
RQ: n/a — Stage 0 data audit (prerequisite for RQ1 to RQ3)
Problem / decision: The 2021 test set has 59 samples in 48 ISO weeks; weeks 14, 15, 18, 31 and 32 contain several samples. A rule is needed to build a one-sample-per-week main series. Sample D20210720T120102 (week 29) holds only 50 images, all Aphanizomenon flosaquae, with no unclassifiable images; its relative abundance would be 100%.
Root cause / options considered: Particle-index coverage (n_images / max particle index) is 0.0065 for that sample and at least 0.928 for all other 58 samples, so it was only partly annotated (probably a rare-class addition), not a complete sample.
Resolution: A sample is complete if particle-index coverage >= 0.5. Among complete samples, the main series takes, per ISO week, the sample closest to Tuesday 12:00 (the regular weekly slot). The rule uses timestamps only, never sample content. Result: 47 main-series samples, 11 supplementary, 1 excluded; weeks 1, 2, 29, 41 and 42 have no main-series sample.
Rejected alternatives (if a decision, not a bug) and why: Picking the sample with most images per week (depends on content, and favours bloom conditions); keeping the week-29 sample (not a complete sample, would create a false 100% peak).

## 2026-09-25 — Training filenames carry no sample ID or timestamp
RQ: RQ1 (affects validation split for T1 to T4)
Problem / decision: All 63,074 training images are named <legacy class name>_<index>.png. The IFCB sample ID and start time are lost, so a sample-level train/validation split cannot be built from filenames, and the temporal separation from 2021 cannot be verified per image.
Root cause / options considered: The 2022 release renamed files (dataset description notes legacy class names). Temporal separation was instead supported by the description (2016 to 2019) and by an MD5 check: 0 byte-identical images between train and test, 0 duplicates within train.
Resolution: Open. To be decided before Stage 1 splitting (see RQ_MAPPING next action).
Rejected alternatives (if a decision, not a bug) and why: Pending.

## 2026-09-25 — Validation split: pseudo-sample index blocks
RQ: RQ1 (affects T1 to T4); resolves the open entry "Training filenames carry no sample ID or timestamp"
Problem / decision: A sample-level split is required to avoid leakage, but training filenames have no sample ID.
Root cause / options considered: (a) stratified random split per class, reporting leakage risk; (b) contiguous index blocks within each class as pseudo-samples, split as groups, valid only if numbering follows acquisition order.
Resolution: (b), chosen by Yuchen. Before use, check that images with neighbouring indices are more similar (feature cosine) than random same-class pairs. If the check fails, fall back to (a) and report the limitation.
Rejected alternatives (if a decision, not a bug) and why: (a) as default, since leakage would make validation optimistic and thresholds set in T4 would not transfer to 2021; requesting original filenames from SYKE, too slow for the time budget.

## 2026-09-25 — Nodularia spumigena evaluated as detection; onset thresholds fixed
RQ: RQ2 (also RQ3 policy layer)
Problem / decision: In the 2021 main series N. spumigena has 5 images over 47 samples (max 2 per sample); 57 of 62 test images are in supplementary samples. With 1% and 2% thresholds and no season window, ground-truth onset falls in January because winter samples are small (350 to 900 images, 7 to 13 Aphanizomenon).
Root cause / options considered: Curve metrics on 0 to 2 images per sample are dominated by single errors. Onset thresholds on relative abundance are sensitive to small denominators.
Resolution: N. spumigena stays a primary and high-risk target but is evaluated per sample as detection and count errors; flagged as a paper finding in RQ_MAPPING. Onset = first main-series sample from 1 June to 30 September reaching 1%, 2% or 5% of the N-fixing total; all three reported. Ground truth: 8 June, 29 June, 29 June. The window was added after seeing the ground-truth curve only (no predictions exist yet); it follows the project definition of recurrent summer blooms.
Rejected alternatives (if a decision, not a bug) and why: A single threshold chosen after inspecting results (test-set tuning); onset without a season window (triggers on winter background).
