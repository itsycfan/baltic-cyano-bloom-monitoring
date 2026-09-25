# Analysis Plan (pre-registered before any 2021 test evaluation)

Written on 2026-09-26, 00:30, before any model was evaluated on the 2021 test set. Every choice below is made on the 2022 data (fit and validation splits) or fixed a priori. The 2021 set is used only to report outcomes; no rule here may be changed after seeing 2021 results. Any deviation is logged in `DEV_LOG.md` with its reason and marked as post hoc.

## Data

- Training: 2022 set, stratified random split 80/20 (seed 0): **fit** (50,459) and **val** (12,615).
- Test: 2021 set. Image-level metrics use all classified 2021 images (48 classes present). Sample-level metrics use the **main series** (47 complete weekly samples); the 11 supplementary samples are added only in a sensitivity analysis. The incomplete week-29 sample is never used for sample-level metrics.
- Relative abundance denominator: all images in a sample, unclassifiable included, for both truth and prediction.

## RQ1: representation and decision layer

- **Feature sets:** ResNet-18, DINOv2 ViT-B/14, CLIP ViT-B/16, BioCLIP 2 (each L2-normalised); fusions are concatenations of L2-normalised blocks.
- **Fusion candidates (T1):** (i) all four backbones; (ii) the two best single backbones by val macro F1. No other combinations.
- **Classifier:** standardisation, multinomial logistic regression; C in {0.1, 1, 10} chosen by val macro F1, separately for class_weight none and balanced.
- **T1 rule:** a fusion is adopted if its val macro F1 (class_weight none) exceeds the best single backbone by at least 0.01. The **primary feature set** for RQ2 and RQ3 is the adopted fusion, otherwise the best single backbone. ResNet-18 is always kept as the baseline.
- **T2 calibration:** a temperature T is fitted on val (minimum negative log-likelihood) for every feature set. Calibrated probabilities are used downstream. Reported: ECE (15 equal-width bins, top label) on val and on 2021 classified images, before and after scaling, with reliability diagrams.
- **2021 image-level reporting:** macro F1 over the 48 classes present, precision, recall and F1 for targets, accuracy, and the distribution of predicted classes for unclassifiable images (closed-set absorption).

## RQ2: abundance

- **Classify and count (CC):** predicted relative abundance = images predicted as the taxon / all images in the sample.
- **Adjusted classify and count (ACC):** misclassification matrix M[i, j] = P(pred = i | true = j) estimated on val predictions of the same classifier; per sample, class proportions q solve min ||M q - p_CC||² subject to q >= 0 and sum q = 1 (non-negative least squares with a sum constraint). The target relative abundance is q for that taxon. ACC is closed-set, like CC.
- **Both class weightings** (none, balanced) are evaluated for CC and ACC.
- **Series:** N-fixing filamentous total (primary), *Aphanizomenon flosaquae*, *Dolichospermum* total (straight and coiled), Oscillatoriales.
- **Metrics per series over the main series:** MAE in percentage points; Pearson and Spearman correlation with the ground truth; peak-week offset (predicted minus true week of maximum); onset agreement for thresholds 1%, 2% and 5% within 1 June to 30 September (difference in weeks, or missed or false). 95% confidence intervals for MAE by bootstrap over samples (2,000 resamples, seed 0).
- ***Nodularia spumigena*:** per-sample detection (present if at least one image) and count errors: true positive, false positive and false negative samples, and false-positive images.

## RQ3: selective review

- **Evidence layer:** cosine kNN on the **fit** split in the classifier's feature space, k = 7. Signals: (a) calibrated maximum probability (low = suspicious); (b) neighbour agreement, the share of the 7 neighbours whose label equals the predicted label (low = suspicious); (c) distance to the nearest neighbour, 1 minus cosine similarity (high = suspicious); (d) high-risk rule: predicted class is *N. spumigena* or *Dinophysis acuminata*.
- **T3 signal validity:** AUROC of (a) to (c) for detecting misclassified val images. A signal is kept if val AUROC >= 0.6. The distance signal (c) is kept regardless, because its purpose is to flag particles outside the training classes, which the val split cannot contain; its 2021 AUROC (errors including unclassifiable images) is reported as the test of that assumption. 2021 AUROCs are reported for all signals but do not change the selection.
- **T4 thresholds:** for a nominal review rate r in {1, 2, 5, 10, 20, 30, 50}%, one quantile level alpha is shared by the kept continuous signals (each signal flags its alpha most suspicious share of val images); alpha is found by bisection so that the union with the high-risk rule reaches r on val. The resulting thresholds are applied unchanged to 2021; the realised 2021 review rate is reported next to the nominal rate.
- **Simulated review:** reviewed images take their ground-truth label, including unclassifiable; abundances are recomputed with the same denominator.
- **Comparison policies at matched realised 2021 review rates:** random review (mean of 20 draws, seed 0) and confidence-only review. Reference lines: CC and ACC without review.
- **Primary configuration:** primary feature set with class_weight none. Class_weight balanced is a sensitivity analysis.
- **Reported:** MAE of each series versus realised review rate; onset and peak agreement at 10% nominal review; *N. spumigena* images routed by each rule and missed.
