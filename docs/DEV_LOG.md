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

## 2026-09-26 — Logistic regression pipeline; C selected on validation
RQ: RQ1
Problem / decision: Choose the regularisation strength C for the decision layer and check the effect of class-balanced weights, using only the 2022 validation split.
Root cause / options considered: Per-model L2 normalisation, StandardScaler, multinomial logistic regression (lbfgs); C in {0.1, 1, 10}; class_weight none or balanced. ResNet-18 on validation: macro F1 0.871 to 0.881 over all six settings, accuracy 0.956 to 0.962. C = 1 is best for both weightings (0.8795 none, 0.8808 balanced).
Resolution: C = 1 for ResNet-18, both weightings carried forward as the proposal requires. The same grid is rerun for every feature set. Balanced weights raise mean recall of classes with fewer than 60 validation images from 0.78 to 0.83 but lower their precision from 0.88 to 0.84; predicted/true count for N. spumigena rises from 1.09 to 1.18. This is the over-prediction effect RQ2 must quantify at sample level.
Rejected alternatives (if a decision, not a bug) and why: Wider C grid (differences are below 0.01 macro F1 and each fit costs time on fused features).

## 2026-09-26 — Pre-registered analysis plan before 2021 evaluation
RQ: RQ1 to RQ3
Problem / decision: Yuchen asked for autonomous overnight progress. Many choices (fusion candidates, T1 margin, signal selection, threshold search, comparison policies) had to be fixed without him, and without looking at 2021.
Root cause / options considered: Decide each choice ad hoc while running; or write all rules first.
Resolution: `docs/ANALYSIS_PLAN.md`, committed locally (4d7823b, 00:27) before any 2021 evaluation. Two points deviate from the wording of `02_proposal.md` and are listed for Yuchen: T1 is decided on val only (the proposal also mentions 2021 labelled images; the project rules forbid tuning on 2021), and the distance signal is kept in T3 regardless of its val AUROC because val contains no out-of-class particles.
Rejected alternatives (if a decision, not a bug) and why: Waiting for confirmation of each choice (would idle the whole night).

## 2026-09-26 — CC error decomposition (post hoc, descriptive)
RQ: RQ2
Problem / decision: After the first RQ2 result (ResNet-18), CC over-estimated all series with a false early onset. The pre-registered metrics show the size of the error but not its source.
Root cause / options considered: Split the CC bias of each series into false positives from unclassifiable images, false positives from other known classes, and false negatives.
Resolution: Added `cc_error_decomposition.csv` to `run_abundance.py`. It is descriptive, changes no decision, and is marked as post hoc. ResNet-18, N-fixing total: +0.66 pp from unclassifiable, +0.17 pp from known classes, -0.03 pp missed.
Rejected alternatives (if a decision, not a bug) and why: None.

## 2026-09-26 — kNN on an 8 GB machine: swap thrashing
RQ: n/a — infra/tooling
Problem / decision: The first RQ3 run stalled (13% CPU, swap 9.5 of 10 GB used) while DINOv2 extraction and desktop apps held most of the memory.
Root cause / options considered: Similarity chunks of 4,096 x 50,459 float32 (about 800 MB each) plus argpartition copies; and `pivot_table` counting called about 150 times in the review simulation.
Resolution: Chunk size 512 (about 100 MB); vectorised counting with `np.bincount`.
Rejected alternatives (if a decision, not a bug) and why: Approximate nearest neighbours (adds a dependency and changes the signal); running kNN on MPS (GPU busy with extraction).

## 2026-09-26 — Size hypothesis for closed-set absorption rejected (exploratory)
RQ: RQ1 (explains RQ2 error source)
Problem / decision: F2 attributed the absorption of unclassifiable particles into small-cell classes to pad-to-square resizing, which removes absolute size. This was an untested claim.
Root cause / options considered: Test it by appending log width and log height to ResNet-18 features (same C and weighting).
Resolution: Rejected. Absorption into Pyramimonas rises (58,134 to 60,528); share into N-fixing taxa 0.95% to 0.90%; CC N-fixing MAE 0.80 to 0.77 pp; val macro F1 0.880 to 0.875, 2021 macro F1 0.623 to 0.634. The primary pipeline keeps size-free features. The cause is the closed-set design. Script: `exploratory_size_ablation.py` (post hoc, exploratory).
Rejected alternatives (if a decision, not a bug) and why: Adding size to the primary pipeline (no meaningful gain, and a post hoc change).

## 2026-09-26 — Queued extraction never started (self-matching pgrep); 7 GPU hours lost
RQ: n/a — infra/tooling
Problem / decision: CLIP and BioCLIP 2 were queued to start after DINOv2 with `while pgrep -f 'model dinov2_vitb14'; do sleep 60; done`. DINOv2 finished around 02:35, but CLIP had not started by 09:35.
Root cause / options considered: `pgrep -f` matches full command lines, and the waiting shell's own command line contains the pattern, so the loop matched itself forever. The same bug blocked the completion watcher.
Resolution: Killed the loops; restarted with plain sequential commands in one shell (`extract clip; extract bioclip2`). Never wait on a pgrep pattern that appears in the waiting command itself; chain jobs sequentially or wait on a PID.
Rejected alternatives (if a decision, not a bug) and why: None.

## 2026-09-26 — OpenAI CLIP loaded with the wrong activation (QuickGELU)
RQ: RQ1
Problem / decision: At the CLIP restart open_clip warned: "QuickGELU mismatch between final model config (quick_gelu=False) and pretrained tag 'openai' (quick_gelu=True)". The smoke test output had filtered warnings, so this was missed on day 1.
Root cause / options considered: OpenAI CLIP weights were trained with QuickGELU; the default `ViT-B-16` config uses GELU, which silently degrades the features.
Resolution: `force_quick_gelu=True` in `src/features.py`; verified the MLP activation is QuickGELU and the warning is gone. No CLIP features had been extracted with the wrong setting (only the smoke test, since deleted). BioCLIP 2's own config has no QuickGELU flag and loads without the warning. Lesson: do not filter warnings in smoke tests.
Rejected alternatives (if a decision, not a bug) and why: None.

## 2026-09-26 — Post hoc check: triage policy without the distance signal
RQ: RQ3
Problem / decision: With DINOv2 the NN-distance signal is near chance (val AUROC 0.53) but was kept by the pre-registered exception. Question: does it only add workload?
Root cause / options considered: Rerun the policy with `--exclude-signal nn_distance` (separate output folders, marked post hoc) for DINOv2 and ResNet-18, class weight none.
Resolution: Workload rises without it (nominal 10%: DINOv2 45.8% to 55.5%, ResNet-18 37.7% to 48.1%), since the shared alpha loosens the thresholds of the remaining signals. At matched workload DINOv2 is unchanged and ResNet-18 is worse. The pre-registered policy is kept.
Rejected alternatives (if a decision, not a bug) and why: Replacing the primary policy post hoc (not justified by the evidence, and would break the pre-registration).

## 2026-09-28 — T1 final decision: no fusion; primary feature set DINOv2
RQ: RQ1
Problem / decision: Apply the pre-registered T1 rule once all four backbones and the two candidate fusions were available.
Root cause / options considered: Best single by val macro F1 (class weight none): DINOv2 0.945. Top-2 singles: DINOv2 and BioCLIP 2 (0.931). Fusions on val: DINOv2 + BioCLIP 2 0.950 (+0.005), all four 0.944 (-0.001), ResNet-18 + DINOv2 0.947 (+0.002, interim candidate).
Resolution: No fusion reaches +0.01; DINOv2 is the primary feature set (`t1_decision.json`). The all-four fusion is best on 2021 (0.755 vs 0.705) and on abundance, which is reported as a finding (validation cannot select for shift robustness) and not used to change the choice.
Rejected alternatives (if a decision, not a bug) and why: Adopting the all-four fusion after seeing 2021 results (selection on the test set).

## 2026-10-02 — Paper framing: retrospective evaluation in a near-real-time-capable setting
RQ: RQ1 to RQ3 (framing)
Problem / decision: The onset metric implies early warning. Is the study a real-time system?
Root cause / options considered: Kraft et al. (2022, Front. Mar. Sci. 9:867695) describe the Utö pipeline: a 5 mL sample about every 20 minutes, transfer over the station network and optical fibre to FMI and CSC Allas, hourly classification, about two hours from capture to classified output, online publication of cyanobacteria biomass in summer 2021. Our study uses weekly expert-verified samples and evaluates afterwards.
Resolution (Yuchen): frame the paper as a retrospective evaluation in a near-real-time-capable setting. Added to the limitations: one sample per week; review latency not modelled. Added to future work: two-stage operation (automatic early warning, expert confirmation). Also noted that Kraft et al. filter unclassifiable images with class-specific probability thresholds, which our closed-set baseline lacks; it must be cited and discussed as related work.
Rejected alternatives (if a decision, not a bug) and why: Presenting the work as a real-time warning system (not what was evaluated).

## 2026-10-02 — Scope rule; threshold-filter validity check (plan A)
RQ: RQ2
Problem / decision: After reading Kraft et al. (2022), the question arose whether to add comparisons each time another method appears. Yuchen judged the framework to be drifting.
Root cause / options considered: Add comparisons ad hoc; or define what qualifies. Decided (Yuchen): methodological positioning and a scope rule in `02_proposal.md`: a comparison enters only if an RQ requires it or a stated conclusion depends on it. Kraft's class-specific thresholds qualify under the second condition, because they are the operational open-set filter on the same data and could invalidate the RQ2 open-set conclusion.
Resolution: Pre-registered plan A (ANALYSIS_PLAN Addendum 1, commit 5c45b5a), then ran `run_threshold_filter.py`. Thresholds set on val reject 8 to 12% of unclassifiable 2021 images; N-fixing MAE falls by 9 to 27%; unclassifiable particles remain the largest positive source (61 to 78%) for both backbones. Verdict: the conclusion holds. Plan B (2021 supplementary samples for calibration) and a timing benchmark are tentative future work.
Rejected alternatives (if a decision, not a bug) and why: Plan B now (uses 2021 data, answers a different question); timing benchmark (no RQ requires it).

## 2026-10-02 — Target classes confirmed; ground truth consistent with Kraft et al. (2022)
RQ: n/a — Stage 0 (supports RQ2 and RQ3)
Problem / decision: The proposal still said target classes were "to be confirmed against Kraft et al.", the role of the 44 non-target classes was undocumented, and the ground-truth figure had no caption.
Root cause / options considered: Kraft et al. (2022, section 3.2) publish near-real-time biomass for the same three main bloom-forming taxa at Utö in summer 2021 and describe the bloom sequence.
Resolution: Targets marked as confirmed in `02_proposal.md`; added the role of non-target classes; closed the open question in `00_project_definition.md`; added a figure caption and an external-consistency note to the Stage 0 README; added both to the report and RQ_MAPPING. Their sequence (Dolichospermum peak 2 July, Aphanizomenon 5 July and end of July, Nodularia sporadic) matches our weekly curve (29 June, 6 July, 27 July). Their 19 to 20 July secondary peak falls on our excluded week-29 sample, a concrete example of the weekly-resolution limitation.
Rejected alternatives (if a decision, not a bug) and why: None; documentation only, no result changed.

## 2026-10-02 — Area-weighted abundance (biomass proxy); winter background explanation corrected
RQ: RQ2
Problem / decision: RQ2 conclusions were stated for image counts; marine readers expect biomass. Pre-registered as Addendum 2 (commit d774e7e) and run.
Root cause / options considered: Segmented particle area per image (`src/morphology.py`, rule fixed before the visual check; faint fringes around small particles are included and were not tuned away, to avoid adjusting after seeing results); bounding-box area as sensitivity.
Resolution: Conclusion holds and strengthens (unclassifiable share of positive N-fixing bias 79% DINOv2, 87% ResNet-18; by count 70%, 80%). Relative MAE roughly halves by area and the false early onset shrinks to 1 week. New failure mode: one large detrital aggregate predicted as N. spumigena (163,000 px, 19% of the 26 October sample's area) makes a false 21% peak; the high-risk rule covers it. Filamentous area share in July and August is 25% (count 6%), close to Kraft et al.'s "about a third of biomass". The area curves show 15 to 20% filamentous share in January and February: the winter background is a few large filaments in a sparse community, not a small-sample artefact as previously written. Corrected in 02_proposal, report, Stage 0 README and taxa.json description; the CHANGELOG v0.1 entry is left as a historical record.
Rejected alternatives (if a decision, not a bug) and why: Tuning the segmentation threshold after the visual check (post hoc); ESD-based biovolume (assumes round cells, wrong for filaments).

## 2026-10-02 — Unpushed history cleaned of manuscript and third-party PDF before first push
RQ: n/a — infra/tooling
Problem / decision: 19 local, never-pushed commits contained the manuscript draft (`paper/`) and the Kraft et al. (2022) PDF (`references/`). Both are now git-ignored, but a normal push would still publish them through history.
Root cause / options considered: Push history as is; or rewrite only the unpushed commits. AGENTS.md forbids rewriting history; Yuchen approved an exception because these commits had never left the machine, so no public history changes and no force push is needed.
Resolution: Backup branch `backup-before-history-cleanup`; `git filter-branch --index-filter 'git rm -r --cached --ignore-unmatch paper references' origin/main..HEAD`. Verified: no paper/ or references/ paths in the new commits, final tree identical to the backup apart from those folders, fast-forward from origin/main, local files untouched. Pushed normally.
Rejected alternatives (if a decision, not a bug) and why: Pushing the history unchanged (would publish an unreviewed draft and a third-party PDF).
