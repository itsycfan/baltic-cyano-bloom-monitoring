# RQ Mapping (live document, SOP-2)

> One row per research question from `02_proposal.md`. Update in the same commit as the work that changes a status. Status values: `OPEN` (not started), `TESTING` (Hypothesis, Method, Result, Decide cycle in progress), `CONCLUDE` (closed), or `CARRIED FORWARD` (deliberately deferred, with a reason).

| RQ | Status | Round / commit | Summary of latest result | Next action |
|---|---|---|---|---|
| RQ1 | OPEN | stage0 | Stage 0 done: 63,074 train / 151,235 test images (57,207 classified, 94,028 unclassifiable); 47-sample weekly main series. Training filenames lack sample IDs. | Set up environment and smoke-test the four feature extractors; extract ResNet-18 features; build pseudo-sample validation split and run the adjacency check; then DINOv2. |
| RQ2 | OPEN | stage0 | Ground truth ready: onset thresholds 1/2/5% fixed (June to September); *N. spumigena* evaluated as detection. | Waits for RQ1 classifier outputs. |
| RQ3 | OPEN | | | Waits for RQ1 outputs and T3 signal validity. Report *N. spumigena* images routed by the high-risk rule. |

## Findings flagged for the paper

Observations that should appear in the paper, with the stage that produced them.

- **Stage 0 (feeds RQ2, RQ3):** *Nodularia spumigena*, the most toxic target, is nearly invisible in abundance curves: 5 images across 47 main-series samples (at most 2 per sample, peak 0.03%) against 57 in supplementary samples. It is evaluated as a detection task, and the result motivates the high-risk review rule in the policy layer. RQ3 should report how many *N. spumigena* images the high-risk rule routes to review and how many would be missed without it.
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
