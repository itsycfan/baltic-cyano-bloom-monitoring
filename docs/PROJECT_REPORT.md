# Project Report: From Image Errors to Bloom Curves

Status: **draft, 2026-09-26.** ResNet-18, DINOv2, CLIP and the ResNet-18 + DINOv2 fusion are complete. BioCLIP 2 and the all-four fusion are running; sections marked *[pending BioCLIP 2]* will be updated. All numbers below come from files in the repository (paths given). Nothing has been pushed.

## 1. Key messages

1. **Temporal shift costs about a quarter of macro F1.** Frozen features with logistic regression lose 0.24 to 0.26 macro F1 from the 2022 validation split to the 2021 Utö samples (best: DINOv2, 0.945 to 0.705).
2. **Abundance error is an open-set problem.** 62% of 2021 images are unclassifiable particles. A closed-set classifier assigns them to known classes; 70 to 85% of the over-estimation of N-fixing cyanobacteria comes from these particles, not from confusion among known taxa. ACC, being closed-set too, removes little of it.
3. **Image-level accuracy does not rank models for monitoring.** CLIP beats ResNet-18 on 2021 macro F1 (0.659 vs 0.623) but gives the largest abundance error (CC MAE 1.03 vs 0.80 pp).
4. **Class-balanced weights halve abundance error here**, contrary to the proposal's expectation, because the bloom taxa are the largest training classes.
5. **Review budgets set on in-distribution data do not transfer.** A nominal 10% review rate on 2022 validation becomes 38 to 53% of 2021 images.
6. **Triage with evidence beats confidence-only and random review at equal workload** (clearly for unweighted classifiers; marginally for balanced ones), and a small review share already beats ACC.
7. ***Nodularia spumigena*, the most toxic target, is the least observable through curves.** It has 5 images in 47 weekly samples; classifiers report it falsely in 11 to 16 samples. A high-risk rule costing 0.1% of review removes all false detections.

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

- **Representation:** frozen ResNet-18 (512-D), DINOv2 ViT-B/14 (768-D), CLIP ViT-B/16 with QuickGELU (512-D), BioCLIP 2 ViT-L/14 (768-D). Images are padded to a square with the border intensity and resized to 224 without cropping (filaments have median aspect ratio up to 7.3). Fusion concatenates L2-normalised blocks.
- **Decision:** standardisation and multinomial logistic regression; C from {0.1, 1, 10} by val macro F1; with and without class-balanced weights. Temperature fitted on val (T2).
- **Validation split:** training indices carry no acquisition order (index-adjacency check with a positive control on 2021), so the split is stratified random 80/20 (seed 0). Leakage risk is a limitation.
- **Abundance (RQ2):** classify and count (CC); adjusted classify and count (ACC) with the val misclassification matrix and a constrained least-squares solve. Denominator: all images, unclassifiable included.
- **Evidence and policy (RQ3):** cosine kNN (k = 7) on the fit split; signals: low confidence, neighbour disagreement, nearest-neighbour distance, high-risk prediction (*N. spumigena*, *D. acuminata*). One shared quantile level per nominal rate, set on val. Reviewed images take their true label. Baselines: confidence-only and random review at the same realised workload.

## 4. RQ1: representation under temporal shift

Source: `experiments/stage1_rq1_representation/outputs/rq1_summary/rq1_table.csv`, figures `macro_f1_val_vs_2021.png`, `target_f1_2021.png`, `rq1_eval/reliability__*.png`.

| Features (class weight none) | Val macro F1 | 2021 macro F1 | 2021 ECE raw | 2021 ECE after T | Unclassifiable into N-fixing |
|---|---|---|---|---|---|
| DINOv2 | 0.945 | 0.705 | 0.072 | 0.032 (T = 1.70) | 0.5% |
| ResNet-18 + DINOv2 | 0.947 | 0.704 | 0.090 | 0.030 (T = 3.16) | 0.4% |
| CLIP | 0.909 | 0.659 | 0.019 | 0.028 (T = 0.93) | 1.1% |
| ResNet-18 | 0.879 | 0.623 | 0.117 | 0.058 (T = 1.77) | 0.9% |
| BioCLIP 2 | *[pending]* | | | | |

- The drop from val to 2021 is similar for all backbones (0.24 to 0.26). DINOv2 leads.
- Target classes transfer well on classified images (2021 F1 0.90 to 0.99 for *Aphanizomenon*, *Dolichospermum* and Oscillatoriales with DINOv2); *D. acuminata* is weakest (0.56 to 0.84).
- **T1 (interim):** ResNet-18 + DINOv2 gains 0.002 val macro F1 over DINOv2, below the 0.01 rule, so fusion is not adopted. Final decision after BioCLIP 2 and the all-four fusion *[pending]*.
- **T2:** val temperature helps when T > 1 (overconfident models) and hurts when T < 1 (CLIP, balanced DINOv2). Calibration fitted in-distribution does not reliably transfer across years.
- **Closed-set absorption:** ResNet-18 assigns 58,134 of 94,028 unclassifiable images to *Pyramimonas* and 9,840 to Beads, a class absent in 2021. An exploratory check shows that restoring absolute size does not reduce this (`exploratory_size_ablation/`).

## 5. RQ2: abundance curves

Source: `experiments/stage2_rq2_abundance/outputs/<features>/`, `experiments/summary_outputs/rq2_*.csv`.

MAE of the N-fixing filamentous total over the 47 main-series samples (percentage points):

| Features | CC, none | ACC, none | CC, balanced | ACC, balanced |
|---|---|---|---|---|
| ResNet-18 | 0.80 | 0.70 | 0.42 | 0.35 |
| CLIP | 1.03 | 0.93 | 0.35 | 0.32 |
| DINOv2 | 0.42 | 0.39 | 0.21 | 0.19 |
| ResNet-18 + DINOv2 | 0.40 | 0.37 | 0.18 | 0.17 |
| BioCLIP 2 | *[pending]* | | | |

- **Error source:** decomposition of the CC bias (none): unclassifiable particles contribute 0.30 to 0.90 pp, other known classes 0.09 to 0.17 pp, missed targets -0.02 to -0.03 pp (`rq2_cc_error_decomposition.csv`).
- **Curve shape:** the peak week of the N-fixing total is correct for every configuration (offset 0). Errors sit in the off-season baseline. Without review, the 2% onset is predicted 3 to 4 weeks early in 5 of 8 configurations (a false early warning driven by a 1 June sample that is 92% unclassifiable); DINOv2 with balanced weights and both ResNet-18 + DINOv2 variants get the 2% onset right, and the balanced ones all three onsets.
- **Pearson vs Spearman:** Pearson r is 0.84 to 0.99, Spearman 0.53 to 0.81; Pearson is dominated by the summer peak and overstates agreement in the many near-zero weeks.
- **ACC** reduces MAE by only 3 to 17% because its misclassification matrix, estimated on val, cannot describe unclassifiable particles.
- **Class-balanced weights** halve the MAE for all backbones.
- **Sensitivity:** adding the 11 supplementary samples changes MAE by at most 0.06 pp and does not change the ranking (`rq2_sensitivity_supplementary.csv`).
- ***N. spumigena* as detection:** all 4 true-present samples are detected by every configuration, but 11 to 16 of the 43 absent samples report it (15 to 27 excess images against 5 true).

## 6. RQ3: selective review

Source: `experiments/stage3_rq3_selective_review/outputs/<features>__<class weight>/`, `experiments/summary_outputs/rq3_*.csv`, figure `experiments/summary_outputs/rq3_triage_by_feature.png`.

- **T3:** low confidence (val AUROC 0.94 to 0.96) and neighbour disagreement (0.87 to 0.92) pass the rule; all degrade on 2021 (0.73 to 0.81). NN distance is weak (val 0.53 to 0.72; 2021 unclassifiable vs correct 0.56 to 0.71) and is kept only by the pre-registered exception. A post hoc check shows that removing it does not reduce workload and hurts ResNet-18 at equal workload.
- **T4, transfer of review rates:** nominal 1, 5, 10% on val become 2 to 7%, 22 to 33% and 36 to 53% on 2021. Unclassifiable images are flagged more often than classified ones, as intended, but workload is underestimated three- to five-fold.
- **Error vs workload** (N-fixing total, class weight none, nominal 10%):

| Features | Realised review | Triage | Confidence only | Random | ACC, no review |
|---|---|---|---|---|---|
| ResNet-18 | 37.7% | 0.084 | 0.243 | 0.504 | 0.697 |
| CLIP | 39.0% | 0.159 | 0.281 | 0.628 | 0.927 |
| DINOv2 | 45.8% | 0.071 | 0.124 | 0.230 | 0.385 |
| ResNet-18 + DINOv2 | 46.5% | 0.032 | 0.065 | 0.217 | 0.366 |

- Reviewing 2 to 7% of images already beats ACC in every configuration. For Oscillatoriales with ResNet-18, confidence-only review is no better than random: filament-like debris is predicted as Oscillatoriales with high confidence, and only the kNN evidence catches it. With balanced weights the advantage of triage over confidence-only is small and not consistent.
- ***N. spumigena*:** the high-risk rule routes all true *N. spumigena* images predicted as such and removes all false-positive images at every rate. One true image was missed with CLIP at nominal 1%, because it was predicted as another class and no other rule fired.

## 7. Findings to carry into the paper

- *N. spumigena* is the most toxic and the least observable target; the high-risk rule is cheap and removes false detections, but cannot recover missed ones.
- Abundance error is dominated by out-of-class particles; this reframes monitoring evaluation from accuracy to open-set handling.
- Accuracy rankings do not transfer to abundance rankings (CLIP vs ResNet-18).
- Val-calibrated review budgets inflate three- to five-fold under temporal shift; operational review needs calibration data from the deployment period.
- Evidence-based triage adds value beyond confidence where errors are confident (Oscillatoriales).

## 8. Deviations, problems and limitations

- **Deviations from the proposal wording:** T1 decided on val only (the proposal also mentions 2021 images); distance signal kept in T3 despite val AUROC below 0.6 (pre-registered reason); class-balanced weights reduce rather than inflate abundance error.
- **Post hoc analyses (marked as such):** CC error decomposition; size ablation; policy without the distance signal.
- **Problems during the run:** a self-matching `pgrep` in the job queue idled the GPU for about 7 hours; OpenAI CLIP needed `force_quick_gelu=True` (fixed before extraction). Both in `DEV_LOG.md`.
- **Limitations:** random validation split (no sample IDs in training data); simulated review is a perfect taxonomist; 2021 labels were corrected from CNN predictions; image counts, not biomass; one station, one year; *N. spumigena* conclusions rest on 5 main-series images.

## 9. Status of RQs

| RQ | Status | Remaining |
|---|---|---|
| RQ1 | TESTING | BioCLIP 2, all-four fusion, final T1 *[pending]* |
| RQ2 | TESTING | BioCLIP 2 and final primary feature set *[pending]* |
| RQ3 | TESTING | Same |

## 10. Decisions needed from Yuchen

*(filled at the end of the run)*
