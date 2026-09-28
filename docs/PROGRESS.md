# Progress Tracker (overnight session 2026-09-26)

Working log for the autonomous session while Yuchen is offline. Local commits only, nothing pushed. Decisions that need Yuchen are collected at the end.

## Background jobs

| Job | Started | Status |
|---|---|---|
| DINOv2 feature extraction | 00:05 | done about 02:35 (1.7 h test + 0.75 h train) |
| CLIP feature extraction | 09:37 (queue bug, see DEV_LOG) | done 12:09; pipeline done 12:24 |
| BioCLIP 2 feature extraction | 26 Sep 12:09 | done about 21:10 (6.0 to 6.2 img/s); final stage done 22:13 |

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
- [x] CLIP: LR grid + pipeline
- [x] BioCLIP 2: LR grid + pipeline
- [x] T1 fusion candidates and decision (no fusion adopted; primary DINOv2)
- [x] RQ2 and RQ3 on the primary feature set (and all others)
- [x] Summary report (`docs/PROJECT_REPORT.md`)

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
- 11:12 Diagnostic done (F17).
- 12:09 CLIP extracted; BioCLIP 2 started; final stage chained to its PID.
- 12:24 CLIP pipeline done (F18 to F20).
- 12:27 Report draft written and every number checked against the output files (F21).
- 26 Sep 22:13 BioCLIP 2, DINOv2 + BioCLIP 2 and all-four pipelines, T1 decision and summaries done (automatic chain); completion notice reached the session on 28 Sep.
- 28 Sep 22:05 Final numbers checked; report completed (F22 to F25).

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
- **F15 (RQ3, T3):** the NN distance signal is near chance for DINOv2 (val AUROC 0.53; 2021 unclassifiable vs correct 0.56), weaker than for ResNet-18 (0.72; 0.71). It was kept only by the pre-registered exception. Realised review rates are higher with DINOv2 (nominal 10% becomes 45.8%). See F17.
- **F16 (T1, interim, two backbones):** ResNet-18 + DINOv2 reaches val macro F1 0.947 vs 0.945 for DINOv2 alone (+0.002, below the +0.01 rule): not adopted. On 2021 it is equal (0.704 vs 0.705) and slightly better for abundance (balanced CC N-fixing MAE 0.175 vs 0.208 pp); the rule is not changed for that. Final T1 waits for CLIP and BioCLIP 2.
- **F17 (post hoc diagnostic, supports the pre-registered choice):** dropping the distance signal does not reduce workload; it raises it (DINOv2 nominal 10%: realised 45.8% to 55.5%; ResNet-18: 37.7% to 48.1%), because alpha is recalibrated on val and the remaining signals, which inflate more under shift, take a larger share. At matched workload DINOv2 is unchanged and ResNet-18 is worse without distance (30.2% review: 0.226 pp vs 21.8% review: 0.215 pp with distance). Keeping the distance signal was harmless for DINOv2 and useful for ResNet-18.
- **F18 (RQ1 vs RQ2, key):** image-level ranking does not predict abundance ranking. CLIP beats ResNet-18 on 2021 macro F1 (0.659 vs 0.623) but has the largest abundance error (CC N-fixing MAE 1.03 vs 0.80 pp) because it absorbs the most unclassifiable particles into N-fixing taxa (1.1% vs 0.9%). Model selection by accuracy can pick a worse monitoring model.
- **F19 (T2):** CLIP is the best calibrated on 2021 before scaling (ECE 0.019); the val-fitted T = 0.93 makes it worse (0.028). Across backbones, val temperature helps when T > 1 (ResNet-18, DINOv2 none) and hurts when T < 1.
- **F20 (RQ3, limit of the high-risk rule):** with CLIP at nominal 1%, one true N. spumigena image is missed after review: it was predicted as another class and triggered no rule. The high-risk rule removes false detections but cannot recover missed ones; missed detections depend on the other signals.
- **F21 (RQ3, qualifies F10):** triage beats confidence-only clearly with unweighted classifiers (all four feature sets), but with balanced weights the gap is small and not consistent (CLIP balanced at nominal 5%: 0.154 vs 0.142 pp; ResNet-18 + DINOv2 balanced: 0.054 vs 0.037). Across all 8 configurations, reviewing 2 to 7% of images beats ACC.
- **F22 (T1, final):** best single DINOv2 (val 0.945). Fusion gains on val: DINOv2 + BioCLIP 2 +0.005, all four -0.001, ResNet-18 + DINOv2 +0.002. None reaches +0.01; no fusion adopted; primary feature set DINOv2.
- **F23 (key, validation vs shift):** the all-four fusion is fourth on val (0.944) but best on 2021 (0.755; drop 0.189 vs 0.22 to 0.26 for all others) and has the lowest abundance error (balanced CC MAE 0.154 pp). In-distribution validation cannot select the most shift-robust model. Not used to change the primary choice (that would be selection on the test set).
- **F24 (BioCLIP 2):** ties DINOv2 on 2021 macro F1 (0.705) with the smallest drop among singles (0.226), the best transferring confidence signal (2021 AUROC 0.88), and near-perfect raw calibration (T = 1.00); but 40% more abundance error than DINOv2 (0.58 vs 0.42 pp) and the most false *N. spumigena* detections (18 to 20 of 43 absent samples, 52 to 63 excess images).
- **F25 (robustness of earlier findings across all 14 configurations):** unclassifiable share of CC bias 70 to 85%; balanced weights reduce CC MAE by 44 to 66%; ACC by 1 to 17%; realised review at nominal 10% is 36 to 58%; nominal-1% triage beats ACC in 14 of 14; triage beats random in 42 of 42 configuration-rate pairs; high-risk rule removes all false *N. spumigena* images everywhere (0.05 to 0.11% of images); T > 1 always helps and T < 1 always hurts 2021 ECE.

## Needs Yuchen's decision

See `docs/PROJECT_REPORT.md`, section 10.
