# Project Report: From Image Errors to Bloom Curves

Status: **complete for all pre-registered analyses, 2026-09-28.** Four frozen backbones, three fusions, two class weightings, RQ1 to RQ3. Every number below comes from a file in the repository (paths given) and was checked against it. Local commits only; nothing has been pushed.

## 1. Key messages

1. **Temporal shift costs a fifth to a quarter of macro F1.** From the 2022 validation split to the 2021 Utö samples, macro F1 drops by 0.19 to 0.26 for every feature set.
2. **In-distribution validation does not select the most shift-robust model.** The all-four fusion ranks fourth on validation (0.944) but first on 2021 (0.755, smallest drop 0.19). The pre-registered rule, which uses validation only, keeps DINOv2 (0.945 val, 0.705 on 2021) as the primary feature set.
3. **Abundance error is an open-set problem.** 62% of 2021 images are unclassifiable particles. A closed-set classifier assigns them to known classes; they cause 70 to 85% of the over-estimation of N-fixing cyanobacteria. ACC, also closed-set, removes only 1 to 17% of the error.
4. **Image-level accuracy does not rank models for monitoring.** CLIP beats ResNet-18 on 2021 macro F1 (0.659 vs 0.623) but has the largest abundance error (1.03 vs 0.80 pp). BioCLIP 2 ties DINOv2 on 2021 macro F1 (0.705) but has 40% more abundance error (0.58 vs 0.42 pp).
5. **Class-balanced weights reduce abundance error by 44 to 66%**, contrary to the proposal's expectation, because the bloom taxa are the largest training classes.
6. **Review budgets set on in-distribution data do not transfer.** A nominal 10% review rate on 2022 validation becomes 36 to 58% of 2021 images.
7. **Triage with evidence beats random review everywhere and confidence-only review in most settings, and a small review share beats ACC.** Reviewing 2 to 10% of images (nominal 1%) beats ACC in all 14 configurations.
8. ***Nodularia spumigena*, the most toxic target, is the least observable through curves.** It has 5 images in 47 weekly samples; every configuration reports it falsely in 11 to 20 samples (13 to 63 excess images). A high-risk rule that flags only 0.05 to 0.11% of images removes all false detections in all configurations. It cannot recover missed images.

## 2. Data and Stage 0 audit

Source: `experiments/stage0_data_audit/`.

- Training (2016 to 2019): 63,074 images in 50 classes; counts match the dataset description exactly. Filenames carry no sample ID or time.
- Test (Utö 2021): 151,235 images, 57,207 classified in 48 classes (no Beads, no *Prorocentrum cordatum*) and 94,028 unclassifiable; 59 samples. No byte-identical images between train and test, no corrupt files.
- **Main series:** regular weekly samples (Tuesday around 12:00) are separated from supplementary samples chosen to enrich rare classes. One complete sample per ISO week gives 47 main-series samples; 11 supplementary samples are used only in a sensitivity analysis; one sample (week 29, 50 images of one class, particle coverage 0.6%) is incomplete and excluded.
- Ground truth (main series): N-fixing filamentous total peaks at 9.3% on 27 July; *Dolichospermum* 5.1% on 29 June; Oscillatoriales 12.9% on 17 August. *N. spumigena*: 5 images in the main series, 57 in supplementary samples.
- Onset: first main-series sample between 1 June and 30 September reaching 1%, 2% or 5% of the N-fixing total (8 June, 29 June, 29 June). The window excludes a 1 to 3% winter background caused by small winter samples.

Figures: `bloom_curve_2021_ground_truth.png`, `sample_coverage_2021.png`, `class_counts_train_vs_test.png`.

## 3. Methods

All choices were pre-registered in `docs/ANALYSIS_PLAN.md` (commit 4d7823b) before any 2021 evaluation.

- **Representation:** frozen ResNet-18 (512-D), DINOv2 ViT-B/14 (768-D), CLIP ViT-B/16 with QuickGELU (512-D), BioCLIP 2 ViT-L/14 (768-D). Images are padded to a square with the border intensity and resized to 224 without cropping (filaments have median aspect ratio up to 7.3). Fusion concatenates L2-normalised blocks. Fusion candidates: the top two single backbones by val macro F1 (DINOv2 + BioCLIP 2) and all four; ResNet-18 + DINOv2 was also run as an interim candidate.
- **Decision:** standardisation and multinomial logistic regression; C from {0.1, 1, 10} by val macro F1; with and without class-balanced weights. Temperature fitted on val (T2).
- **Validation split:** training indices carry no acquisition order (index-adjacency check with a positive control on 2021), so the split is stratified random 80/20 (seed 0).
- **Abundance (RQ2):** classify and count (CC); adjusted classify and count (ACC) with the val misclassification matrix and a constrained least-squares solve. Denominator: all images, unclassifiable included.
- **Evidence and policy (RQ3):** cosine kNN (k = 7) on the fit split; signals: low confidence, neighbour disagreement, nearest-neighbour distance, high-risk prediction (*N. spumigena*, *D. acuminata*). One shared quantile level per nominal rate, set on val. Reviewed images take their true label. Baselines: confidence-only and random review at the same realised workload.

## 4. RQ1: representation under temporal shift

Source: `experiments/stage1_rq1_representation/outputs/rq1_summary/` (`rq1_table.csv`, `t1_decision.json`, `macro_f1_val_vs_2021.png`, `target_f1_2021.png`), `rq1_eval/reliability__*.png`.

| Features (class weight none) | Val macro F1 | 2021 macro F1 | Drop | 2021 ECE raw | 2021 ECE after T | Unclassifiable into N-fixing |
|---|---|---|---|---|---|---|
| DINOv2 + BioCLIP 2 | 0.950 | 0.728 | 0.222 | 0.064 | 0.024 (T = 2.02) | 0.6% |
| ResNet-18 + DINOv2 | 0.947 | 0.704 | 0.243 | 0.090 | 0.030 (T = 3.16) | 0.4% |
| **DINOv2 (primary)** | 0.945 | 0.705 | 0.240 | 0.072 | 0.032 (T = 1.70) | 0.5% |
| All four | 0.944 | **0.755** | **0.189** | 0.037 | 0.023 (T = 1.21) | 0.5% |
| BioCLIP 2 | 0.931 | 0.705 | 0.226 | 0.028 | 0.028 (T = 1.00) | 0.6% |
| CLIP | 0.909 | 0.659 | 0.250 | 0.019 | 0.028 (T = 0.93) | 1.1% |
| ResNet-18 | 0.879 | 0.623 | 0.257 | 0.117 | 0.058 (T = 1.77) | 0.9% |

- **T1 decision (pre-registered, val only):** best single DINOv2 (0.945). DINOv2 + BioCLIP 2 gains +0.005, all four -0.001, ResNet-18 + DINOv2 +0.002; none reaches +0.01, so no fusion is adopted and **DINOv2 is the primary feature set**.
- **Val ranking vs 2021 ranking:** the all-four fusion is fourth on val but first on 2021 by 0.03. Validation drawn from the training years cannot measure robustness to the shift. The rule is not changed after the fact; this is reported as a finding.
- **T2:** val temperature improves 2021 ECE whenever T > 1 and worsens it whenever T < 1 (all 14 configurations). CLIP and BioCLIP 2 are already well calibrated on 2021 before scaling.
- **Targets on classified 2021 images:** *Aphanizomenon*, *Dolichospermum* and Oscillatoriales reach F1 0.90 to 0.99 with DINOv2; *D. acuminata* is weakest (0.56 to 0.92 across configurations).
- **Closed-set absorption:** ResNet-18 assigns 58,134 of 94,028 unclassifiable images to *Pyramimonas* and 9,840 to Beads, a class absent in 2021. An exploratory check shows that restoring absolute size does not reduce this (`exploratory_size_ablation/`).

## 5. RQ2: abundance curves

Source: `experiments/stage2_rq2_abundance/outputs/<features>/`, `experiments/summary_outputs/rq2_*.csv`.

MAE of the N-fixing filamentous total over the 47 main-series samples (percentage points):

| Features | CC, none | ACC, none | CC, balanced | ACC, balanced |
|---|---|---|---|---|
| ResNet-18 | 0.80 | 0.70 | 0.42 | 0.35 |
| CLIP | 1.03 | 0.93 | 0.35 | 0.32 |
| BioCLIP 2 | 0.58 | 0.55 | 0.33 | 0.30 |
| **DINOv2 (primary)** | 0.42 | 0.39 | 0.21 | 0.19 |
| DINOv2 + BioCLIP 2 | 0.46 | 0.44 | 0.22 | 0.22 |
| ResNet-18 + DINOv2 | 0.40 | 0.37 | 0.18 | 0.17 |
| All four | 0.37 | 0.35 | 0.15 | 0.15 |

- **Error source:** unclassifiable particles cause 70 to 85% of the positive CC bias in every configuration; confusion among known classes causes the rest; missed target images offset only 0.01 to 0.04 pp (`rq2_cc_error_decomposition.csv`).
- **Curve shape:** the peak week of the N-fixing total is correct in every configuration. Errors sit in the off-season baseline. Without review, the 2% onset is predicted 3 to 4 weeks early in 9 of 14 CC configurations (a false early warning driven by a 1 June sample that is 92% unclassifiable); 4 configurations, all with balanced weights (DINOv2, DINOv2 + BioCLIP 2, ResNet-18 + DINOv2, all four), get all three onsets right.
- **Pearson vs Spearman:** Pearson r is 0.84 to 0.99, Spearman 0.53 to 0.83; Pearson is dominated by the summer peak and overstates agreement in the many near-zero weeks.
- **ACC** reduces MAE by 1 to 17%.
- **Class-balanced weights** reduce CC MAE by 44 to 66% for every feature set.
- **Sensitivity:** adding the 11 supplementary samples changes MAE by at most 0.07 pp and does not change the ranking.
- ***N. spumigena* as detection:** all 4 true-present samples are detected by every configuration, but 11 to 20 of the 43 absent samples report it (13 to 63 excess images against 5 true). BioCLIP 2 produces the most false detections (18 to 20 samples, 52 to 63 images).

## 6. RQ3: selective review

Source: `experiments/stage3_rq3_selective_review/outputs/<features>__<class weight>/`, `experiments/summary_outputs/rq3_*.csv`, figure `experiments/summary_outputs/rq3_triage_by_feature.png`.

- **T3:** low confidence (val AUROC 0.94 to 0.97) and neighbour disagreement (0.87 to 0.94) pass the rule; on 2021 they fall to 0.76 to 0.89 and 0.73 to 0.83. NN distance is weak (val 0.50 to 0.72; 2021 unclassifiable vs correct 0.56 to 0.71) and is kept only by the pre-registered exception; a post hoc check shows that removing it raises workload and does not lower error at matched workload. BioCLIP 2 has the most transferable confidence (2021 AUROC 0.88 vs 0.81 for DINOv2).
- **T4, transfer of review rates:** nominal 1, 5 and 10% on val become 2 to 10%, 22 to 41% and 36 to 58% on 2021. Unclassifiable images are flagged more often than classified ones, as intended, but the workload is underestimated by a factor of about 2 to 10.
- **Error vs workload** (N-fixing total, class weight none, nominal 10%):

| Features | Realised review | Triage | Confidence only | Random | ACC, no review |
|---|---|---|---|---|---|
| ResNet-18 | 37.7% | 0.084 | 0.243 | 0.504 | 0.697 |
| CLIP | 39.0% | 0.159 | 0.281 | 0.628 | 0.927 |
| BioCLIP 2 | 54.3% | 0.039 | 0.094 | 0.260 | 0.551 |
| **DINOv2 (primary)** | 45.8% | 0.071 | 0.124 | 0.230 | 0.385 |
| DINOv2 + BioCLIP 2 | 54.6% | 0.041 | 0.094 | 0.217 | 0.443 |
| ResNet-18 + DINOv2 | 46.5% | 0.032 | 0.065 | 0.217 | 0.366 |
| All four | 57.5% | 0.011 | 0.025 | 0.152 | 0.345 |

- Triage beats random review in all 42 configuration-rate pairs. It is at least as good as confidence-only review in 14 of 14 configurations at nominal 1%, 13 of 14 at 10%, and 11 of 14 at 5%; the exceptions are all balanced classifiers, where the gap is small.
- For Oscillatoriales with ResNet-18, confidence-only review is no better than random: filament-like debris is predicted as Oscillatoriales with high confidence, and only the kNN evidence catches it.
- ***N. spumigena*:** the high-risk rule flags 0.05 to 0.11% of main-series images and removes all false-positive images in every configuration and rate. One true image was missed by CLIP at nominal 1% (both weightings): it was predicted as another class and no other rule fired.

## 7. Findings to carry into the paper

- *N. spumigena* is the most toxic and the least observable target; the high-risk rule is cheap and removes all false detections, but cannot recover missed ones. The biological foundation model produced the most false detections.
- Abundance error is dominated by out-of-class particles; monitoring evaluation should move from accuracy to open-set handling.
- Accuracy rankings do not transfer to abundance rankings (CLIP vs ResNet-18; BioCLIP 2 vs DINOv2), and in-distribution validation does not identify the most shift-robust model (all-four fusion).
- Val-calibrated review budgets inflate by a factor of about 2 to 10 under temporal shift; operational review needs calibration data from the deployment period.
- Evidence-based triage adds value beyond confidence where errors are confident (Oscillatoriales).

## 8. Deviations, problems and limitations

- **Deviations from the proposal wording:** T1 decided on val only (the proposal also mentions 2021 images); distance signal kept in T3 despite val AUROC below 0.6 (pre-registered reason); class-balanced weights reduce rather than inflate abundance error.
- **Post hoc analyses (marked as such):** CC error decomposition; size ablation; policy without the distance signal.
- **Problems during the run:** a self-matching `pgrep` in the job queue idled the GPU for about 7 hours; OpenAI CLIP needed `force_quick_gelu=True` (fixed before extraction); memory pressure on the 8 GB machine slowed BioCLIP 2 to about 6 img/s. All in `DEV_LOG.md`.
- **Limitations:** random validation split (no sample IDs in training data); simulated review is a perfect taxonomist; 2021 labels were corrected from CNN predictions; image counts, not biomass; one station, one year; *N. spumigena* conclusions rest on 5 main-series images; single seed for the split and for kNN.

## 9. Status of RQs

All three RQs meet the "concluded when" criteria in `02_proposal.md`. They stay TESTING in `RQ_MAPPING.md` until Yuchen reviews the results; then CONCLUDE and tags `rq1-concluded` to `rq3-concluded`.

## 10. Decisions needed from Yuchen

1. **Review and push.** Local commits since `v0.1-stage0` are not pushed.
2. **Mark RQ1 to RQ3 as CONCLUDE and tag them**, or request further analyses first.
3. **Primary configuration for the paper.** The pre-registered primary is DINOv2 with class weight none. The balanced variant has half the abundance error and correct onsets. Options: keep none as primary and report balanced as the key RQ2 result (recommended, consistent with pre-registration), or present both as primary.
4. **The all-four fusion.** It is best on 2021 but was rejected by the val-only rule. Recommended: keep DINOv2 as primary and report the fusion's 2021 advantage as the "validation cannot select for shift" finding; do not switch post hoc.
5. **Proposal deviations** in section 8 (T1 on val only; distance exception) need your approval before they go into `02_proposal.md` vFinal and `CHANGELOG.md`.
6. **Scope for the remaining days.** Candidates, all outside the current plan: (a) calibrating review thresholds on the first weeks of 2021 and testing on the rest (addresses the workload inflation); (b) an explicit reject option using the kNN distance; (c) BioCLIP 2 zero-shot ablation (optional in the proposal). Recommended: (a) as future work in the paper; skip (b) and (c) unless time remains after writing.
