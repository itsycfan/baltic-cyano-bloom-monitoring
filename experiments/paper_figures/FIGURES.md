# Paper figures: index and draft captions

All files in this folder are produced by `python experiments/make_paper_figures.py` (new figures are drawn there; the others are copied from stage outputs, source paths in the script). 300 dpi PNG. Numbers in captions come from the repository outputs and `docs/PROJECT_REPORT.md`.

**Before posting:** check that the SYKE dataset licence allows showing example images (Fig. 2, Fig. S1, Fig. S10) and cite both datasets.

## Main figures (proposed)

| No. | File | Draft caption |
|---|---|---|
| 1 | `fig01_framework.png` (+ `.svg`) | Method schematic. Top: data partition; the 2022 validation split (dashed) is the only data used to fit C, the temperature T, review thresholds τ and the ACC matrix M; the 2021 test set (dotted) is used only for evaluation. (A) Each region of interest (W × H) is padded to an S × S square with the median border grey and resized to 224 × 224 without cropping. (B) Frozen backbones give L2-normalised embeddings; fusion concatenates them. (C) Standardisation and multinomial logistic regression with temperature scaling give the predicted class ŷ and confidence c over 50 closed-set classes. (D) Cosine kNN (k = 7) on the fit split gives the nearest-neighbour distance d_NN and neighbour agreement a. (E) Three suspicion scores are thresholded at (1 − α) validation quantiles, with one α per nominal review rate; together with the high-risk rule they feed an OR gate (≥1) that routes an image to review. (F) Reviewed images take the expert label, others keep ŷ; per-sample counts give CC and ACC abundance, evaluated as bloom curves (MAE, correlation, peak offset, onset error Δ). |
| 2 | `fig02_example_images.png` | Example 2021 IFCB images of the target taxa (a to f) and of unclassifiable particles (g, h). Images are not to scale. |
| 3 | `fig03_ground_truth_bloom_curve.png` | Ground-truth relative abundance (share of all images, unclassifiable included) at Utö in 2021. Lines: 47 weekly main-series samples; hollow circles: supplementary samples; dotted line: excluded incomplete sample (20 July). Upper panel: bloom-forming filamentous cyanobacteria; lower panel: low-abundance high-risk taxa. |
| 4 | `fig04_macro_f1_val_vs_2021.png` | Image-level macro F1 on the 2022 validation split and on 2021 classified images for four frozen backbones and three fusions (class weight none). |
| 5 | `fig05_unclassifiable_absorption.png` | Where the 94,028 unclassifiable 2021 images go under a closed-set classifier (DINOv2 and ResNet-18, class weight none): top destination classes (grey) and target taxa (orange), log scale. |
| 6 | `fig06_rq2_curves_dinov2.png` | Predicted vs ground-truth relative abundance for the primary feature set (DINOv2): classify and count (CC) with and without class-balanced weights, and adjusted classify and count (ACC). |
| 7 | `fig07_error_decomposition.png` | Decomposition of the CC bias of the N-fixing filamentous total over the main series: unclassifiable particles predicted as N-fixing taxa, other known classes predicted as N-fixing taxa, and missed N-fixing images (negative). |
| 8 | `fig08_accuracy_vs_abundance.png` | Image-level accuracy does not rank models for abundance: 2021 macro F1 against CC MAE of the N-fixing total, for seven feature sets and two class weightings. |
| 9 | `fig09_onset_error.png` | Onset error of the N-fixing total without review (predicted minus true onset week, June to September window) for thresholds of 1, 2 and 5%. Negative values are false early warnings. |
| 10 | `fig10_rq3_mae_vs_review_dinov2.png` | Abundance error against realised review workload on the 2021 main series (DINOv2, class weight none): triage policy, confidence-only review and random review at matched workload; dashed line: ACC without review. |
| 11 | `fig11_nominal_vs_realised.png` | Review rates set on the 2022 validation split do not transfer: nominal vs realised 2021 review rate for all feature sets (class weight none). |
| 12 | `fig12_nodularia_detection.png` | *Nodularia spumigena* in the 2021 main series: true images per sample (bars) and predicted images (DINOv2, BioCLIP 2). All predicted images are routed to review by the high-risk rule, which removes every false detection. |
| 13 | `fig13_area_vs_count.png` | Area-weighted abundance as a biomass proxy. Top: ground truth by image count and by particle area. Middle and bottom: DINOv2 CC predictions of the N-fixing total weighted by count and by area. |

## Supplementary figures (proposed)

| No. | File | Content |
|---|---|---|
| S1 | `figS1_preprocessing_examples.png` | Pad-to-square preprocessing keeps whole filaments |
| S2 | `figS2_index_adjacency.png` | Index-adjacency check with 2021 positive control (validation split) |
| S3 | `figS3_target_f1_2021.png` | Target-class F1 on 2021 for all feature sets |
| S4 | `figS4_reliability_dinov2.png` | Reliability diagrams before and after temperature scaling (DINOv2) |
| S5 | `figS5_class_counts_train_vs_test.png` | Class distribution shift between training and 2021 |
| S6 | `figS6_sample_coverage.png` | Images per 2021 sample, classified vs unclassifiable |
| S7 | `figS7_threshold_filter_dinov2.png` | Validity check with class-specific probability thresholds |
| S8 | `figS8_rq3_triage_by_feature.png` | Triage policy across all feature sets and both weightings |
| S9 | `figS9_triage_curves_dinov2.png` | Curves before and after triage review at nominal 10% |
| S10 | `figS10_segmentation_check.png` | Particle segmentation used for the area proxy (training images) |

## Tables (source files)

| Table | Content | Source |
|---|---|---|
| 1 | RQ1: val and 2021 macro F1, ECE, temperature | `stage1_rq1_representation/outputs/rq1_summary/rq1_table.csv` |
| 2 | RQ2: MAE of the N-fixing total (CC, ACC, both weightings) | `summary_outputs/rq2_mae_by_feature.csv` |
| 3 | RQ3: realised review rate and MAE by policy at nominal 10% | `summary_outputs/rq3_summary.csv` |
