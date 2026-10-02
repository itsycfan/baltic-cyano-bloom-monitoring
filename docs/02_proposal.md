# Proposal (SOP-1 output)

## Research Questions

| ID | Question | Concluded when… |
|---|---|---|
| RQ1 | Under the temporal shift from 2022 training data to 2021 test samples, how do single features (DINOv2, CLIP, BioCLIP 2, ResNet-18) and fused features perform in image-level classification? | Macro F1 and target-class F1 on the 2021 test set are reported for all features, and decisions on fusion (T1) and calibration (T2) are recorded. |
| RQ2 | How large is the error of cyanobacteria relative abundance curves under classify-and-count, and does adjusted classify-and-count (ACC) reduce it? | MAE, correlation, peak-week offset and onset agreement are reported for classify-and-count and ACC, with and without class-balanced weights. |
| RQ3 | How does bloom curve error change with the proportion of images sent to human review, and how does review compare with ACC in workload versus error? | A review rate versus abundance error curve is reported, including 5%, 10% and 20% review, with thresholds set on the 2022 validation split and compared with ACC. |

Either outcome is informative. If foundation-model features classify worse but yield more stable abundance, evaluation should move from accuracy to abundance. If image-level gaps are amplified at the abundance level, model choice matters directly for operational monitoring.

## Methodological positioning

The contribution is an evaluation and decision methodology, not a better classifier: it traces image-level classification errors to errors in sample-level bloom curves (RQ1 to RQ2) and corrects them with evidence-based selective expert review (RQ3). The study is a retrospective evaluation in a near-real-time-capable setting: the Utö IFCB pipeline classifies images about two hours after capture (Kraft et al., 2022), and this work measures the quality of that observation layer and the review effort it needs, on weekly expert-verified samples.

## Scope rule

A comparison or experiment enters the study only if it meets one of two conditions:

1. **Required by a research question.** Examples: ACC (RQ2 asks whether it corrects abundance); random and confidence-only review (RQ3 asks whether the triage policy adds value); four backbones and fusion (RQ1).
2. **Needed to test whether a stated conclusion holds.** Example: class-specific probability thresholds, the open-set filter used operationally at Utö on the same data (Kraft et al., 2022), test whether the RQ2 conclusion "abundance error is dominated by unclassifiable particles" still holds when such a filter is applied.

Everything else (newer classifiers, other open-set methods, extra benchmarks) goes to discussion or future work. Post hoc analyses are allowed only as descriptive diagnostics, are labelled post hoc, and never change a pre-registered decision.

### Target classes

Confirmed against Kraft et al. (2022), who published near-real-time biomass of the same three main bloom-forming cyanobacteria taxa of the Baltic Sea (*Dolichospermum*/*Anabaenopsis*, *Aphanizomenon flosaquae*, *Nodularia spumigena*) from Utö in summer 2021 (their section 3.2). Training image counts in brackets.

**Role of the other classes.** The classifier is trained on all 50 classes, and only the targets below are evaluated as curves. The remaining classes (diatoms, dinoflagellates, cryptophytes, green algae, ciliates and others) are kept because they give non-target particles somewhere to go: without them, every non-target image would be forced into a target class and target abundance would be inflated. Their errors are still analysed where they explain target errors (for example, unclassifiable particles absorbed into *Pyramimonas*).

- **Primary targets (nitrogen-fixing filamentous bloom taxa):** *Aphanizomenon flosaquae* (6,989); *Dolichospermum* sp./*Anabaenopsis* sp. (12,280) and its coiled form (2,504); *Nodularia spumigena* (169).
- **Reported separately:** Oscillatoriales (4,440), filamentous but not a primary bloom taxon.
- **High-risk taxa for the policy layer:** *Nodularia spumigena*; *Dinophysis acuminata* (217).

**Evaluation of *Nodularia spumigena* (revised after Stage 0).** *N. spumigena* remains a primary target and a high-risk taxon. In the 2021 main series it occurs in 4 of 47 samples with at most 2 images per sample (peak relative abundance 0.03%); 57 of its 62 test images come from supplementary samples. Curve metrics (MAE, correlation, peak week) are therefore not meaningful for it. It is evaluated as a per-sample detection and count task (detected or not, missed images, false-positive images). Curve metrics are reported for the N-fixing filamentous total, *Aphanizomenon flosaquae* and *Dolichospermum* (straight and coiled combined), with Oscillatoriales reported separately.

> **Finding to carry into the paper:** the most toxic target taxon is also the one least observable through abundance curves, because its images are too rare per sample. This motivates routing it to expert review through the high-risk rule of the policy layer rather than relying on automatic counts.

## Research Roadmap (vFinal)

Status on 2026-10-02: all stages complete; RQ1 to RQ3 concluded (tags `rq1-concluded` to `rq3-concluded`). The v0 roadmap is preserved at tag `v0-proposal`; differences are listed in `CHANGELOG.md`.

1. **Stage 0, data audit (done):** file names parsed into a sample table; class counts checked against the dataset description; train/test separation checked (MD5, no shared images); weekly coverage; ground-truth bloom curve.
   - **Main series:** the 2021 set combines regular weekly samples (Tuesday around 12:00) with supplementary samples chosen to enrich rare classes. Supplementary samples are not a random draw, so all curve metrics use a main series of one complete sample per ISO week, the sample closest to Tuesday 12:00 (timestamps only). A sample is complete if images / highest particle index is at least 0.5. Supplementary samples are used only for sensitivity analysis.
   - **Result:** 47 main-series samples, 11 supplementary, 1 incomplete sample excluded (week 29); weeks 1, 2, 29, 41 and 42 have no main-series sample. The seasonal sequence matches Kraft et al. (2022).
2. **Stage 1, RQ1 (done):** frozen features from four backbones, logistic regression, T1 (fusion) and T2 (calibration); 2021 evaluated once with pre-registered choices.
3. **Stage 2, RQ2 (done):** classify and count vs ACC, curve metrics, error decomposition, *N. spumigena* as detection; two pre-registered validity checks (class-specific probability thresholds; area-weighted abundance).
4. **Stage 3, RQ3 (done):** T3 (signal validity), T4 (thresholds on validation), simulated review against confidence-only and random review at matched workload, comparison with ACC.
5. **Optional ablation (not done):** BioCLIP 2 zero-shot classification; outside the scope rule, left as future work.
6. **Write-up (done):** project report (`docs/PROJECT_REPORT.md`) and manuscript draft (local `paper/`, not in the repository).

## Technical Framework (vFinal)

The framework adapts the author's layered design for weld defect detection. Every decision below was pre-registered in `ANALYSIS_PLAN.md` before the 2021 data were used.

- **Preprocessing:** each image is padded to a square with its median border grey and resized to 224 x 224 without cropping (filaments are elongated; median aspect ratio 7.3 for *Aphanizomenon*); grey copied to three channels; each backbone keeps its own normalisation.
- **Representation layer:** frozen ResNet-18 (512-D), DINOv2 ViT-B/14 (768-D), CLIP ViT-B/16 with QuickGELU (512-D) and BioCLIP 2 ViT-L/14 (768-D), each L2-normalised. Fusion candidates: the top two single backbones by validation macro F1 and all four. **Outcome: no fusion reached the +0.01 rule; the primary feature set is DINOv2.** The all-four fusion was best on 2021, reported as a finding (validation from the training years does not select the most shift-robust model).
- **Validation split:** stratified random 80/20 (seed 0). A pseudo-sample split by index blocks was planned but rejected, because training indices carry no acquisition order (index-adjacency check with a 2021 positive control).
- **Decision layer:** standardisation and multinomial logistic regression; C from {0.1, 1, 10} by validation macro F1; class weight none (primary) and balanced (reported throughout, since it halves abundance error); temperature fitted on validation. Closed set: no "unknown" output.
- **Abundance:** classify and count (CC) and adjusted classify and count (ACC, misclassification matrix from validation, constrained least squares). Denominator: all images in the sample, unclassifiable included.
- **Evidence layer:** cosine kNN on the fit split, k = 7; neighbour agreement and nearest-neighbour distance.
- **Policy layer:** review if any rule fires: low confidence, neighbour disagreement, large distance, or a prediction of *N. spumigena* or *D. acuminata* (high-risk rule). One shared quantile level per nominal rate, found by bisection on validation; thresholds applied unchanged to 2021. The distance signal is kept although weak (a post hoc check showed that removing it raises workload).
- **Simulated review:** reviewed images take their true label (including unclassifiable); comparison policies review the same number of images (confidence-only, random).
- **Validity checks:** class-specific probability thresholds set on validation (in the spirit of the Utö pipeline) and area-weighted abundance as a biomass proxy; both confirm that unclassifiable particles are the largest error source.

### Preliminary tests and outcomes

- **T1, fusion:** decided on validation only (the v0 wording also mentioned 2021 images; the project rule of no tuning on 2021 takes precedence). No fusion adopted.
- **T2, calibration:** temperature fitted on validation improves 2021 ECE only when T > 1; calibration from the training years does not reliably transfer.
- **T3, signal validity:** low confidence (validation AUROC 0.94 to 0.97) and neighbour disagreement (0.87 to 0.94) kept; distance kept by the pre-registered exception (validation contains no out-of-class particles), and turned out to be the weakest detector of unclassifiable particles on 2021.
- **T4, thresholds:** set on validation; nominal 1, 5 and 10% became 2 to 10%, 22 to 41% and 36 to 58% of 2021 images.

### Evaluation metrics

- **Image level:** macro F1 over the 48 classes present in 2021; precision, recall and F1 for targets; ECE (15 bins).
- **Sample level (47 main-series samples):** MAE in percentage points with bootstrap CI, bias, Pearson and Spearman correlation, peak-week offset, onset error; error decomposition; *N. spumigena* per-sample detection and false positives.
- **Onset definition:** the first main-series sample between 1 June and 30 September whose N-fixing filamentous total reaches 1%, 2% or 5% (all reported). The window is needed because the winter community is sparse, so a few large *Aphanizomenon* filaments make up 1 to 3% of images and 15 to 20% of particle area without forming a bloom. Ground-truth onsets: 8 June (1%), 29 June (2% and 5%).
- **Policy level:** abundance error against realised review rate, with matched-workload baselines.

## Out of scope

Carried from `00_project_definition.md` §4.3: VLM reasoning, end-to-end fine-tuning, absolute biomass or concentration estimates, and bloom forecasting. New comparisons follow the scope rule above.

## Known limitations

- Random validation split (no sample identifiers in the training data); validation scores are somewhat optimistic.
- One sample per week (the instrument samples about every 20 minutes); short peaks can be missed, as on 19 and 20 July 2021.
- Review is simulated as instant and always correct; review latency and expert error are not modelled.
- The 2021 labels were corrected from CNN predictions and may be anchored to that model.
- Abundance is counted in images; the area proxy is a simple segmentation, not a calibrated biovolume.
- A single station and a single year; *N. spumigena* conclusions rest on 5 main-series images.
- Frozen backbones and a linear classifier; fine-tuned networks were not tested.

## Future work (tentative, to be decided when writing)

Open-set methods (for example kNN-distance rejection or thresholds learned from deployment-period unclassifiable particles); review thresholds calibrated on the first weeks of a season (plan B); a two-stage alert workflow (automatic provisional alert, expert confirmation) with realistic review times; higher temporal resolution; a timing benchmark; BioCLIP 2 zero-shot ablation.
