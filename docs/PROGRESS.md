# Progress Tracker (overnight session 2026-09-26)

Working log for the autonomous session while Yuchen is offline. Local commits only, nothing pushed. Decisions that need Yuchen are collected at the end.

## Background jobs

| Job | Started | Status |
|---|---|---|
| DINOv2 feature extraction | 00:05 | done about 02:35 (1.7 h test + 0.75 h train) |
| CLIP feature extraction | 09:37 (queue bug, see DEV_LOG) | running, QuickGELU fixed |
| BioCLIP 2 feature extraction | after CLIP (about 11:40) | queued, ETA about 19:00 |

## Checklist

- [x] Stage 0 data audit (committed, pushed earlier)
- [x] Environment, extractors, preprocessing, ResNet-18 features, val split
- [x] LR pipeline, ResNet-18 val results
- [x] Pre-registered analysis plan (`docs/ANALYSIS_PLAN.md`) before any 2021 evaluation
- [x] RQ1 evaluation script (temperature scaling, 2021 metrics, reliability, unclassifiable absorption)
- [x] RQ2 script (CC, ACC, curve metrics, Nodularia detection, CC error decomposition)
- [x] RQ3 scripts (kNN evidence, T3, T4, simulated review, baselines)
- [x] Full pipeline on ResNet-18 (both class weights)
- [x] DINOv2: LR grid + pipeline
- [ ] CLIP: LR grid + pipeline
- [ ] BioCLIP 2: LR grid + pipeline
- [ ] T1 fusion candidates and decision
- [ ] RQ2 and RQ3 on the primary feature set
- [ ] Summary report

## Log

- 00:26 Committed LR pipeline (6a01e2e). Wrote analysis plan and this tracker.
- 00:27 Committed analysis plan (4d7823b) before any 2021 evaluation.
- 00:29 RQ1 evaluation on ResNet-18 done (F1, F2).
- 00:31 RQ2 on ResNet-18 done (F3 to F7).
- 00:44 First RQ3 run stalled on swap; fixed (chunk 512, vectorised counting).
- 00:48 RQ3 on ResNet-18 (class weight none) done (F8 to F11).
- 00:53 ResNet-18 RQ3 balanced done; committed ResNet-18 pipeline locally (6c1a53c).
- 00:54 Exploratory size ablation (F12) rejects the size hypothesis in F2.
- 09:35 Found CLIP never started: self-matching pgrep in the queue (7 GPU hours lost). Restarted.
- 09:36 Found QuickGELU mismatch for OpenAI CLIP; fixed before any full CLIP extraction.
- 09:37 CLIP extraction running; DINOv2 pipeline started.
- 09:44 DINOv2 pipeline done (F13 to F15); ResNet-18 + DINOv2 fusion pipeline started.
- 10:09 Fusion pipeline done (F16); notification arrived at 11:10.
- 11:10 Post hoc no-distance policy diagnostic started (DINOv2, ResNet-18).

## Findings to report

- **F1 (RQ1, ResNet-18):** val macro F1 0.879 drops to 0.623 on 2021 classified images (accuracy 0.961 to 0.819). Temperature T = 1.77 fitted on val reduces 2021 ECE from 0.117 to 0.058 but does not remove the shift-induced overconfidence.
- **F2 (RQ1 to RQ2, closed-set absorption):** of 94,028 unclassifiable 2021 images, ResNet-18 assigns 58,134 to *Pyramimonas* and 9,840 to Beads (a class absent from 2021). Into targets: Aphanizomenon 413 (true 1,849), Dolichospermum 390 (true 790), Dolichospermum coiled 62 (true 70), *N. spumigena* 24 (true 62, only 5 in the main series), Oscillatoriales 1,364, *D. acuminata* 28 (true 17). On classified images target F1 is 0.82 to 0.99, so abundance error will be driven mainly by unclassifiable particles, not by confusion among known classes. ~~Likely contributor: pad-to-square resizing removes absolute size.~~ Rejected by F12: adding size does not reduce absorption.
- **F3 (RQ2, ResNet-18, main series):** CC over-estimates every series (bias +0.80 pp for the N-fixing total). Decomposition: +0.66 pp from unclassifiable images predicted as N-fixing taxa, +0.17 pp from other known classes, -0.03 pp from missed target images. About 80% of the abundance error is open-set absorption. Peak weeks are all correct (offset 0), but the off-season baseline is inflated and the 2% onset is predicted 4 weeks early (a false early warning, 1 June vs 29 June), driven by the 1 June sample that is 92% unclassifiable.
- **F4 (RQ2):** ACC barely helps (N-fixing MAE 0.80 to 0.70 pp) because it is closed-set: its misclassification matrix, estimated on val, cannot describe unclassifiable particles.
- **F5 (RQ2, contrary to the proposal's expectation):** class-balanced weights *halve* the abundance error (N-fixing MAE 0.80 to 0.42 pp). The bloom taxa are the largest training classes (Dolichospermum 12,280, Aphanizomenon 6,989), so balancing lowers their prior and fewer unclassifiable particles fall into them. The proposal expected the opposite (inflation of rare classes); that effect exists (N. spumigena predicted/true 1.09 to 1.18 on val) but is outweighed.
- **F6 (RQ2, Nodularia):** CC reports N. spumigena in 18 of 47 main-series samples (true: 4); 25 predicted images vs 5 true; all 4 true-present samples are detected. As a detection task: sensitivity 4/4, but 14 false-positive samples.
- **F7 (metrics):** Pearson r is high (0.90 to 0.97) while Spearman is low for Dolichospermum (0.10 to 0.33): the curve shape at the peak is right, but ranks among the many near-zero weeks are noise. Pearson alone would overstate agreement.
- **F8 (RQ3, T3, ResNet-18):** all three signals pass the val rule (AUROC for val misclassification: confidence 0.94, neighbour disagreement 0.92, NN distance 0.72) and all degrade on 2021 (any error: 0.78, 0.74, 0.70). Contrary to the framework's assumption, NN distance is the *weakest* detector of unclassifiable particles (AUROC 0.71 vs 0.77 for low confidence).
- **F9 (RQ3, T4, key):** review rates calibrated on 2022 val do not transfer. Nominal 1, 5, 10, 20% become 3.1, 21.8, 37.7, 60.5% of 2021 main-series images. Unclassifiable images are flagged more (45% at nominal 10%) than classified ones (23%), which is desirable, but the workload is underestimated three- to four-fold. Operational review budgets cannot be set on in-distribution validation data.
- **F10 (RQ3, key):** at equal realised workload the triage policy dominates: N-fixing MAE at 37.7% review is 0.084 pp (triage) vs 0.243 (confidence only) vs 0.504 (random). Reviewing 3.1% already beats ACC (0.63 vs 0.70 pp). For Oscillatoriales, confidence-only review is no better than random: unclassifiable filament-like particles are predicted as Oscillatoriales *with high confidence*, and only the kNN evidence catches them. This is direct evidence for the evidence layer.
- **F11 (RQ3, Nodularia, supports the flagged paper finding):** the high-risk rule costs 0.1% of images, routes all 5 true N. spumigena images in the main series to review, and removes all 20 false-positive images; after review no main-series sample reports N. spumigena falsely (14 before).
- **F12 (exploratory, post hoc, corrects F2):** appending log width and log height to ResNet-18 features does not reduce absorption: unclassifiable images predicted as *Pyramimonas* rise from 58,134 to 60,528, the share predicted as N-fixing taxa moves only from 0.95% to 0.90%, and CC N-fixing MAE from 0.80 to 0.77 pp (onset still 4 weeks early). Unclassifiable particles are small (median 72 x 42 px), like small flagellates, so size does not separate them. The cause is the closed-set design itself (no class for other particles), not the preprocessing.
- **F13 (RQ1, DINOv2 vs ResNet-18):** DINOv2 is better on every image-level measure: val macro F1 0.945 vs 0.880, 2021 macro F1 0.705 vs 0.623, 2021 ECE after scaling 0.032 vs 0.058, and it absorbs fewer unclassifiable images into N-fixing taxa (0.5% vs 0.9%). Balanced weights with T = 0.95 make 2021 calibration slightly worse after scaling (0.031 to 0.037): val-fitted temperature does not always transfer.
- **F14 (RQ2):** better features reduce abundance error roughly in proportion: CC N-fixing MAE 0.80 (ResNet-18) to 0.42 pp (DINOv2); with balanced weights 0.21 pp, and all three onsets (1, 2, 5%) are then correct without any review. Unclassifiable absorption remains the largest error source (0.30 of 0.42 pp bias).
- **F15 (RQ3, T3):** the NN distance signal is near chance for DINOv2 (val AUROC 0.53; 2021 unclassifiable vs correct 0.56), weaker than for ResNet-18 (0.72; 0.71). It was kept only by the pre-registered exception. Realised review rates are higher with DINOv2 (nominal 10% becomes 45.8%). A post hoc check of the policy without the distance signal is planned.
- **F16 (T1, interim, two backbones):** ResNet-18 + DINOv2 reaches val macro F1 0.947 vs 0.945 for DINOv2 alone (+0.002, below the +0.01 rule): not adopted. On 2021 it is equal (0.704 vs 0.705) and slightly better for abundance (balanced CC N-fixing MAE 0.175 vs 0.208 pp); the rule is not changed for that. Final T1 waits for CLIP and BioCLIP 2.

## Needs Yuchen's decision
