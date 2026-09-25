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

## 2026-09-26 — Environment: Python 3.11 venv
RQ: n/a — infra/tooling
Problem / decision: System Python is 3.9.6 (end of life) without timm or open_clip.
Root cause / options considered: System 3.9 with user site-packages; Homebrew 3.11 in a project venv.
Resolution: `.venv` from Homebrew Python 3.11; versions pinned in `requirements.txt`. All four backbones load on MPS: ResNet-18 (512-D), DINOv2 ViT-B/14 via torch.hub (768-D), CLIP ViT-B/16 openai via open_clip (512-D), BioCLIP 2 via open_clip `hf-hub:imageomics/bioclip-2` (ViT-L/14, 224 px, 768-D). Measured throughput with data loading: ResNet-18 about 200 img/s (I/O bound), DINOv2 about 25, CLIP about 30, BioCLIP 2 about 7 to 9 img/s.
Rejected alternatives (if a decision, not a bug) and why: System Python 3.9, since newer library releases drop it.

## 2026-09-26 — Preprocessing: pad to square instead of centre crop
RQ: RQ1
Problem / decision: The default CLIP and open_clip transform resizes the short side and centre crops. IFCB particles are often elongated: median aspect ratio 7.3 for Aphanizomenon, 6.1 for Oscillatoriales, 32% of all images above 2.
Root cause / options considered: Centre crop (keeps resolution, discards most of a filament); pad to square then resize (keeps the whole particle, thin filaments become thinner).
Resolution: Pad with the median border intensity, resize to 224 bicubic, replicate grey to RGB, apply each model's own mean and std. Same geometry for all four backbones so that differences come from the representation. Visual check in `experiments/stage1_rq1_representation/outputs/preprocessing_examples.png`.
Rejected alternatives (if a decision, not a bug) and why: Centre crop, since it removes the shape cue that separates the filamentous targets. Appending absolute size as extra features: possible ablation, not planned now (scope).

## 2026-09-26 — Validation split falls back to stratified random
RQ: RQ1 (affects T1 to T4)
Problem / decision: Plan (b) required training indices to follow acquisition order.
Root cause / options considered: Cosine similarity of ResNet-18 features between images at index lag 1 to 1000 within each legacy name versus random same-class pairs. Train: excess 0.0002 at lag 1 (43% of 53 groups positive), flat at all lags. Positive control on 2021, sorted by sample: excess 0.0117, positive in 26 of 26 classes. The method detects sample structure; the training indices carry none.
Resolution: Fallback (a) as agreed: per-class stratified random split, 80/20, seed 0 (`train_val_split.csv.gz`; 50,459 fit, 12,615 val; smallest val classes have 4 images). Leakage is reported as a limitation; within-sample images are only 0.014 cosine more similar than across samples on 2021 data, so the optimism of validation metrics should be modest.
Rejected alternatives (if a decision, not a bug) and why: Index blocks (no evidence of order); clustering near-duplicates into pseudo-groups (extra complexity for a small expected gain, deferred).
