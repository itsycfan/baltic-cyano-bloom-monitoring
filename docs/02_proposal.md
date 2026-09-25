# Proposal (SOP-1 output)

## Research Questions

| ID | Question | Concluded when… |
|---|---|---|
| RQ1 | Under the temporal shift from 2022 training data to 2021 test samples, how do single features (DINOv2, CLIP, BioCLIP 2, ResNet-18) and fused features perform in image-level classification? | Macro F1 and target-class F1 on the 2021 test set are reported for all features, and decisions on fusion (T1) and calibration (T2) are recorded. |
| RQ2 | How large is the error of cyanobacteria relative abundance curves under classify-and-count, and does adjusted classify-and-count (ACC) reduce it? | MAE, correlation, peak-week offset and onset agreement are reported for classify-and-count and ACC, with and without class-balanced weights. |
| RQ3 | How does bloom curve error change with the proportion of images sent to human review, and how does review compare with ACC in workload versus error? | A review rate versus abundance error curve is reported, including 5%, 10% and 20% review, with thresholds set on the 2022 validation split and compared with ACC. |

Either outcome is informative. If foundation-model features classify worse but yield more stable abundance, evaluation should move from accuracy to abundance. If image-level gaps are amplified at the abundance level, model choice matters directly for operational monitoring.

### Target classes

To be confirmed against Kraft et al. (2021, 2022). Training image counts in brackets.

- **Primary targets (nitrogen-fixing filamentous bloom taxa):** *Aphanizomenon flosaquae* (6,989); *Dolichospermum* sp./*Anabaenopsis* sp. (12,280) and its coiled form (2,504); *Nodularia spumigena* (169).
- **Reported separately:** Oscillatoriales (4,440), filamentous but not a primary bloom taxon.
- **High-risk taxa for the policy layer:** *Nodularia spumigena*; *Dinophysis acuminata* (217).

## Research Roadmap (v0)

1. **Stage 0, data audit:** parse file names into a sample table, count samples per ISO week (one sample per week for the main series, additional samples for sensitivity analysis), verify temporal separation of training and test data, and plot the ground-truth bloom curve.
2. **Stage 1, RQ1:** extract frozen features, train logistic regression, run T1 (fusion) and T2 (calibration).
3. **Stage 2, RQ2:** aggregate predictions per sample and compare classify-and-count with ACC.
4. **Stage 3, RQ3:** run T3 (signal validity) and T4 (thresholds), apply the triage policy with simulated review, and compare with ACC.
5. **Optional ablation:** BioCLIP 2 zero-shot classification with taxon names as text prompts.

RQ2 and RQ3 depend on the features and classifier from RQ1. RQ3 also depends on T3, which determines which signals enter the policy.

## Technical Framework (v0)

The framework adapts the author's layered design for weld defect detection.

- **Representation layer:** frozen features from DINOv2 ViT-B/14 (768-D), CLIP ViT-B/16, BioCLIP 2 and ImageNet ResNet-18 (512-D). Fusion by L2 normalizing each feature and concatenating; kept only if T1 shows a clear gain (about 1 point of macro F1 or more).
- **Decision layer:** multinomial logistic regression returning the predicted class, softmax confidence and top-2 classes. Trained with and without class-balanced weights, since balanced weights raise predicted proportions of rare classes and may inflate their abundance.
- **Evidence layer:** cosine kNN retrieval on the training set (k = 7 as a starting value), returning neighbour label agreement and nearest-neighbour distance. Distance flags out-of-distribution images, including unclassifiable particles that logistic regression cannot reject.
- **Policy layer:** an image is sent to human review if any rule fires: neighbour label disagreement, low confidence, large neighbour distance, or a prediction in a high-risk taxon. Other images keep the predicted label. Thresholds from the weld system are not reused; all thresholds are set on a validation split of the 2022 data for target review rates, never on the 2021 test set.
- **Simulated review:** reviewed images receive their ground-truth label (including unclassifiable), and abundance is recomputed.
- **Output:** per image, label, source (automatic or review), confidence and neighbour evidence; per sample, relative abundance of each taxon over all images in the sample, unclassifiable images included.

### Preliminary tests

- **T1, fusion:** compare macro F1 of single and fused features on the 2022 validation split and the labelled 2021 images.
- **T2, calibration:** reliability diagram and ECE on 2021 data; temperature scaling on the 2022 validation split if needed.
- **T3, signal validity:** AUROC of low confidence, neighbour disagreement and neighbour distance for detecting images that are misclassified or unclassifiable; signals near 0.5 are dropped.
- **T4, thresholds:** set on the 2022 validation split for target review rates.

### Evaluation metrics

- **Image level:** macro F1; precision, recall and F1 for target classes; ECE.
- **Sample level:** MAE of target relative abundance; correlation with the ground-truth curve; peak-week offset; onset agreement.
- **Policy level:** abundance error as a function of review rate.

## Out of scope

Carried from `00_project_definition.md` §4.3: VLM reasoning, end-to-end fine-tuning, biomass or concentration estimates, and bloom forecasting.

## Known limitations

- Review is simulated as a perfect taxonomist, which overstates its benefit; real review involves errors and time cost.
- The 2021 labels were corrected from CNN predictions and may be anchored to that model.
- Relative abundance counts images, not biomass: a filament counts once regardless of length. Summed pixel area may serve as a rough biovolume proxy.
- A single station and a single year.

---

When this is stable: commit, tag `v0-proposal`, and initialize `RQ_MAPPING.md` with the table above.
