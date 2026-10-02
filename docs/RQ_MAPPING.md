# RQ Mapping (live document, SOP-2)

> One row per research question from `02_proposal.md`. Update in the same commit as the work that changes a status. Status values: `OPEN` (not started), `TESTING` (Hypothesis, Method, Result, Decide cycle in progress), `CONCLUDE` (closed), or `CARRIED FORWARD` (deliberately deferred, with a reason).

| RQ | Status | Round / commit | Summary of latest result | Next action |
|---|---|---|---|---|
| RQ1 | CONCLUDE | tag `rq1-concluded` (2 Oct 2026) | 2021 macro F1: all-four fusion 0.755, DINOv2 + BioCLIP 2 0.728, DINOv2 0.705, BioCLIP 2 0.705, CLIP 0.659, ResNet-18 0.623 (val to 2021 drop 0.19 to 0.26). T1: no fusion reaches +0.01 on val; primary DINOv2. T2: val temperature helps only when T > 1. | None. |
| RQ2 | CONCLUDE | tag `rq2-concluded` (2 Oct 2026) | N-fixing MAE (DINOv2): CC 0.42 / ACC 0.38 pp (none), 0.21 / 0.19 pp (balanced). Unclassifiable particles cause 70 to 85% of CC bias; ACC removes 1 to 17%; balanced weights 44 to 66%. Peak weeks always right; 2% onset 3 to 4 weeks early in 9 of 14 configurations. N. spumigena: 11 to 20 false-positive samples. Holds under class thresholds and area weighting. | None. |
| RQ3 | CONCLUDE | tag `rq3-concluded` (2 Oct 2026) | Nominal 10% review on val becomes 36 to 58% on 2021. At nominal 10% (DINOv2, none): triage 0.071, confidence-only 0.124, random 0.230, ACC 0.385 pp. Nominal-1% triage beats ACC in 14 of 14 configurations. High-risk rule removes all false N. spumigena detections at 0.05 to 0.11% of images. | None. |

## Findings flagged for the paper

Observations that should appear in the paper, with the stage that produced them.

- **Stage 0 (feeds RQ2, RQ3):** *Nodularia spumigena*, the most toxic target, is nearly invisible in abundance curves: 5 images across 47 main-series samples (at most 2 per sample, peak 0.03%) against 57 in supplementary samples. It is evaluated as a detection task, and the result motivates the high-risk review rule in the policy layer. RQ3 should report how many *N. spumigena* images the high-risk rule routes to review and how many would be missed without it.
- **Stage 1 to 3 (key results, see `docs/PROJECT_REPORT.md`):** abundance error is dominated by unclassifiable particles (open-set); accuracy rankings do not predict abundance rankings; in-distribution validation does not select the most shift-robust model (all-four fusion); val-calibrated review budgets inflate by a factor of about 2 to 10 on 2021; evidence-based triage beats confidence-only where errors are confident (Oscillatoriales).
- **RQ2 validity check (2 Oct):** class-specific probability thresholds set on val (Kraft-style) reject only 8 to 12% of unclassifiable images; unclassifiable particles stay the largest error source; the open-set conclusion holds.
- **Stage 0 (external consistency, 2 Oct):** the weekly ground-truth curve reproduces the 2021 bloom sequence that Kraft et al. (2022) report from 20-minute biomass data (*Dolichospermum* late June, *Aphanizomenon* early and late July, *N. spumigena* sporadic); their 19 to 20 July secondary peak falls on our excluded week-29 sample.
- **RQ2 area-proxy check (2 Oct):** weighting images by particle area, unclassifiable particles cause 79 to 87% of the positive bias (70 to 80% by count); relative error halves and false onsets shrink to 1 week; one large aggregate predicted as *N. spumigena* creates a false area peak, which the high-risk rule would catch. Filamentous share of area in July to August (25%) is close to the biomass share reported by Kraft et al. (2022).
- **Stage 0 (method):** the 2021 set mixes regular weekly and rare-class supplementary samples; curve metrics use a one-sample-per-week main series to avoid over-weighting rare-class weeks.

## Closed RQs: detail

*For each RQ that reaches CONCLUDE, record the winning approach, the evidence, and any change to the Technical Framework.*

### RQ1
- **Concluded:** 2026-10-02, tag `rq1-concluded`
- **Result:** Frozen features with logistic regression lose 0.19 to 0.26 macro F1 from the 2022 validation split to 2021. DINOv2 is the best single backbone on validation (0.945) and ties with BioCLIP 2 on 2021 (0.705). No fusion meets the pre-registered +0.01 rule, so DINOv2 is the primary feature set; the all-four fusion is nevertheless best on 2021 (0.755), so validation from the training years does not identify the most shift-robust model. Validation temperature improves 2021 calibration only when T > 1. The closed-set classifier assigns most unclassifiable particles to small-cell classes and several hundred to the targets.
- **Framework impact:** Representation: DINOv2, no fusion. Decision layer unchanged (multinomial logistic regression, C from validation, temperature scaling); both class weightings kept, since RQ2 shows balanced weights halve abundance error.

### RQ2
- **Concluded:** 2026-10-02, tag `rq2-concluded`
- **Result:** Peak weeks are always correct, but CC over-estimates the off-season baseline; unclassifiable particles cause 70 to 85% of the bias, ACC removes only 1 to 17%, and the 2% onset is signalled 3 to 4 weeks early in 9 of 14 configurations. Image-level accuracy does not rank models by abundance error. Balanced weights reduce error by 44 to 66%. N. spumigena is evaluated as detection (11 to 20 false-positive samples). The open-set conclusion holds under class-specific thresholds and under area weighting.
- **Framework impact:** Evaluation moves from image accuracy to curve error, onset and peak timing, with an error decomposition. ACC is kept only as a reference; handling unknown particles (review now, open-set methods in future work) is the main lever.

### RQ3
- **Concluded:** 2026-10-02, tag `rq3-concluded`
- **Result:** Review rates set on validation inflate to 2 to 10%, 22 to 41% and 36 to 58% of 2021 images for nominal 1, 5 and 10%. At equal workload, triage beats random review in all 42 cases and confidence-only review in most; reviewing 2 to 10% of images beats ACC in all 14 configurations; evidence signals catch confident errors (Oscillatoriales). The high-risk rule removes every false N. spumigena detection at 0.05 to 0.11% of images but cannot recover missed ones.
- **Framework impact:** Policy layer kept as designed (three scores plus high-risk rule, shared quantile level); the distance signal is kept (post hoc check: removing it raises workload). Review budgets must be calibrated on deployment-period data (future work), and a two-stage alert workflow is proposed.
---

When every RQ is `CONCLUDE` or `CARRIED FORWARD`, move to Confirm: update the Roadmap and Framework in `02_proposal.md` to vFinal, log the change in `CHANGELOG.md`, and tag `vFinal`.
