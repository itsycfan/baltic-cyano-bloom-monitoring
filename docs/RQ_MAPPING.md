# RQ Mapping (live document, SOP-2)

> One row per research question from `02_proposal.md`. Update in the same commit as the work that changes a status. Status values: `OPEN` (not started), `TESTING` (Hypothesis, Method, Result, Decide cycle in progress), `CONCLUDE` (closed), or `CARRIED FORWARD` (deliberately deferred, with a reason).

| RQ | Status | Round / commit | Summary of latest result | Next action |
|---|---|---|---|---|
| RQ1 | TESTING (criteria met, awaiting review) | stage1, final stage 26 Sep | 2021 macro F1: all-four fusion 0.755, DINOv2 + BioCLIP 2 0.728, DINOv2 0.705, BioCLIP 2 0.705, CLIP 0.659, ResNet-18 0.623 (val to 2021 drop 0.19 to 0.26). T1: no fusion reaches +0.01 on val; primary DINOv2. T2: val temperature helps only when T > 1. | Yuchen: review, then CONCLUDE and tag rq1-concluded. |
| RQ2 | TESTING (criteria met, awaiting review) | stage2 | N-fixing MAE (DINOv2): CC 0.42 / ACC 0.39 pp (none), 0.21 / 0.19 pp (balanced). Unclassifiable particles cause 70 to 85% of CC bias; ACC removes 1 to 17%; balanced weights 44 to 66%. Peak weeks always right; 2% onset 3 to 4 weeks early in 9 of 14 configurations. N. spumigena: 11 to 20 false-positive samples. | Yuchen: review, then CONCLUDE and tag rq2-concluded. |
| RQ3 | TESTING (criteria met, awaiting review) | stage3 | Nominal 10% review on val becomes 36 to 58% on 2021. At nominal 10% (DINOv2, none): triage 0.071, confidence-only 0.124, random 0.230, ACC 0.385 pp. Nominal-1% triage beats ACC in 14 of 14 configurations. High-risk rule removes all false N. spumigena detections at 0.05 to 0.11% of images. | Yuchen: review, then CONCLUDE and tag rq3-concluded. |

## Findings flagged for the paper

Observations that should appear in the paper, with the stage that produced them.

- **Stage 0 (feeds RQ2, RQ3):** *Nodularia spumigena*, the most toxic target, is nearly invisible in abundance curves: 5 images across 47 main-series samples (at most 2 per sample, peak 0.03%) against 57 in supplementary samples. It is evaluated as a detection task, and the result motivates the high-risk review rule in the policy layer. RQ3 should report how many *N. spumigena* images the high-risk rule routes to review and how many would be missed without it.
- **Stage 1 to 3 (key results, see `docs/PROJECT_REPORT.md`):** abundance error is dominated by unclassifiable particles (open-set); accuracy rankings do not predict abundance rankings; in-distribution validation does not select the most shift-robust model (all-four fusion); val-calibrated review budgets inflate by a factor of about 2 to 10 on 2021; evidence-based triage beats confidence-only where errors are confident (Oscillatoriales).
- **RQ2 validity check (2 Oct):** class-specific probability thresholds set on val (Kraft-style) reject only 8 to 12% of unclassifiable images; unclassifiable particles stay the largest error source; the open-set conclusion holds.
- **Stage 0 (method):** the 2021 set mixes regular weekly and rare-class supplementary samples; curve metrics use a one-sample-per-week main series to avoid over-weighting rare-class weeks.

## Closed RQs: detail

*For each RQ that reaches CONCLUDE, record the winning approach, the evidence, and any change to the Technical Framework.*

### RQ1
- **Concluded:** _(date / commit)_
- **Result:**
- **Framework impact:**

### RQ2
- **Concluded:** _(date / commit)_
- **Result:**
- **Framework impact:**

### RQ3
- **Concluded:** _(date / commit)_
- **Result:**
- **Framework impact:**

---

When every RQ is `CONCLUDE` or `CARRIED FORWARD`, move to Confirm: update the Roadmap and Framework in `02_proposal.md` to vFinal, log the change in `CHANGELOG.md`, and tag `vFinal`.
