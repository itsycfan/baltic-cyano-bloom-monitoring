# Progress Tracker (overnight session 2026-09-26)

Working log for the autonomous session while Yuchen is offline. Local commits only, nothing pushed. Decisions that need Yuchen are collected at the end.

## Background jobs

| Job | Started | Status |
|---|---|---|
| DINOv2 feature extraction | 00:05 | running |
| CLIP feature extraction | queued after DINOv2 | queued |
| BioCLIP 2 feature extraction | queued after CLIP | queued |

## Checklist

- [x] Stage 0 data audit (committed, pushed earlier)
- [x] Environment, extractors, preprocessing, ResNet-18 features, val split
- [x] LR pipeline, ResNet-18 val results
- [x] Pre-registered analysis plan (`docs/ANALYSIS_PLAN.md`) before any 2021 evaluation
- [x] RQ1 evaluation script (temperature scaling, 2021 metrics, reliability, unclassifiable absorption)
- [x] RQ2 script (CC, ACC, curve metrics, Nodularia detection, CC error decomposition)
- [x] RQ3 scripts (kNN evidence, T3, T4, simulated review, baselines)
- [ ] Full pipeline on ResNet-18
- [ ] DINOv2: LR grid + pipeline
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

## Findings to report

- **F1 (RQ1, ResNet-18):** val macro F1 0.879 drops to 0.623 on 2021 classified images (accuracy 0.961 to 0.819). Temperature T = 1.77 fitted on val reduces 2021 ECE from 0.117 to 0.058 but does not remove the shift-induced overconfidence.
- **F2 (RQ1 to RQ2, closed-set absorption):** of 94,028 unclassifiable 2021 images, ResNet-18 assigns 58,134 to *Pyramimonas* and 9,840 to Beads (a class absent from 2021). Into targets: Aphanizomenon 413 (true 1,849), Dolichospermum 390 (true 790), Dolichospermum coiled 62 (true 70), *N. spumigena* 24 (true 62, only 5 in the main series), Oscillatoriales 1,364, *D. acuminata* 28 (true 17). On classified images target F1 is 0.82 to 0.99, so abundance error will be driven mainly by unclassifiable particles, not by confusion among known classes. Likely contributor: pad-to-square resizing removes absolute size, so small blobs resemble small flagellates such as *Pyramimonas*.
- **F3 (RQ2, ResNet-18, main series):** CC over-estimates every series (bias +0.80 pp for the N-fixing total). Decomposition: +0.66 pp from unclassifiable images predicted as N-fixing taxa, +0.17 pp from other known classes, -0.03 pp from missed target images. About 80% of the abundance error is open-set absorption. Peak weeks are all correct (offset 0), but the off-season baseline is inflated and the 2% onset is predicted 4 weeks early (a false early warning, 1 June vs 29 June), driven by the 1 June sample that is 92% unclassifiable.
- **F4 (RQ2):** ACC barely helps (N-fixing MAE 0.80 to 0.70 pp) because it is closed-set: its misclassification matrix, estimated on val, cannot describe unclassifiable particles.
- **F5 (RQ2, contrary to the proposal's expectation):** class-balanced weights *halve* the abundance error (N-fixing MAE 0.80 to 0.42 pp). The bloom taxa are the largest training classes (Dolichospermum 12,280, Aphanizomenon 6,989), so balancing lowers their prior and fewer unclassifiable particles fall into them. The proposal expected the opposite (inflation of rare classes); that effect exists (N. spumigena predicted/true 1.09 to 1.18 on val) but is outweighed.
- **F6 (RQ2, Nodularia):** CC reports N. spumigena in 18 of 47 main-series samples (true: 4); 25 predicted images vs 5 true; all 4 true-present samples are detected. As a detection task: sensitivity 4/4, but 14 false-positive samples.
- **F7 (metrics):** Pearson r is high (0.90 to 0.97) while Spearman is low for Dolichospermum (0.10 to 0.33): the curve shape at the peak is right, but ranks among the many near-zero weeks are noise. Pearson alone would overstate agreement.
- **F8 (RQ3, T3, ResNet-18):** all three signals pass the val rule (AUROC for val misclassification: confidence 0.94, neighbour disagreement 0.92, NN distance 0.72) and all degrade on 2021 (any error: 0.78, 0.74, 0.70). Contrary to the framework's assumption, NN distance is the *weakest* detector of unclassifiable particles (AUROC 0.71 vs 0.77 for low confidence).
- **F9 (RQ3, T4, key):** review rates calibrated on 2022 val do not transfer. Nominal 1, 5, 10, 20% become 3.1, 21.8, 37.7, 60.5% of 2021 main-series images. Unclassifiable images are flagged more (45% at nominal 10%) than classified ones (23%), which is desirable, but the workload is underestimated three- to four-fold. Operational review budgets cannot be set on in-distribution validation data.
- **F10 (RQ3, key):** at equal realised workload the triage policy dominates: N-fixing MAE at 37.7% review is 0.084 pp (triage) vs 0.243 (confidence only) vs 0.504 (random). Reviewing 3.1% already beats ACC (0.63 vs 0.70 pp). For Oscillatoriales, confidence-only review is no better than random: unclassifiable filament-like particles are predicted as Oscillatoriales *with high confidence*, and only the kNN evidence catches them. This is direct evidence for the evidence layer.
- **F11 (RQ3, Nodularia, supports the flagged paper finding):** the high-risk rule costs 0.1% of images, routes all 5 true N. spumigena images in the main series to review, and removes all 20 false-positive images; after review no main-series sample reports N. spumigena falsely (14 before).

## Needs Yuchen's decision
