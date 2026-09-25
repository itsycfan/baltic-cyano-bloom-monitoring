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
- [ ] RQ1 evaluation script (temperature scaling, 2021 metrics, reliability, unclassifiable absorption)
- [ ] RQ2 script (CC, ACC, curve metrics, Nodularia detection)
- [ ] RQ3 scripts (kNN evidence, T3, T4, simulated review, baselines)
- [ ] Full pipeline on ResNet-18
- [ ] DINOv2: LR grid + pipeline
- [ ] CLIP: LR grid + pipeline
- [ ] BioCLIP 2: LR grid + pipeline
- [ ] T1 fusion candidates and decision
- [ ] RQ2 and RQ3 on the primary feature set
- [ ] Summary report

## Log

- 00:26 Committed LR pipeline (6a01e2e). Wrote analysis plan and this tracker.

## Findings to report

## Needs Yuchen's decision
