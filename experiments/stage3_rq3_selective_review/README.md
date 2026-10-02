# Stage 3 (RQ3): Selective Human Review

Applies a rule-based triage policy (low confidence, kNN neighbour disagreement, kNN distance, high-risk taxa) that routes images to simulated expert review, and measures abundance error as a function of the realised review workload. Thresholds are set on the 2022 validation split only.

## Run (from repo root, inside `.venv`)

```bash
python experiments/stage3_rq3_selective_review/run_review.py --features dinov2_vitb14 --class-weight none
python experiments/stage3_rq3_selective_review/run_review.py --features dinov2_vitb14 --class-weight none --exclude-signal nn_distance   # post hoc diagnostic
```

kNN evidence is cached in `checkpoints/evidence/`; the first run per feature set takes a few minutes.

## Outputs (`outputs/<features>__<class weight>/`)

| File | Content |
|---|---|
| `t3_signal_auroc.csv` | AUROC of each signal on validation and on 2021; which signals are kept |
| `t4_thresholds_and_rates.csv` | Thresholds per nominal rate; realised 2021 review rates; share flagged by each rule |
| `review_curve_metrics.csv` | Curve metrics after review for triage, confidence-only and random review at matched workload |
| `nodularia_routing.csv` | *N. spumigena* images reviewed, missed and false positives removed |
| `mae_vs_review_rate.png`, `nominal_vs_realised_rate.png`, `curves_triage_10pct.png` | Figures |

## Results (all feature sets in `experiments/summary_outputs/rq3_*.csv`)

- Nominal review rates of 1, 5 and 10% on validation become 2 to 10%, 22 to 41% and 36 to 58% of 2021 images.
- DINOv2 at nominal 10% (45.8% reviewed): MAE 0.071 pp (triage), 0.124 (confidence only), 0.230 (random); ACC without review 0.385.
- Reviewing 2 to 10% of images beats ACC in all 14 configurations; triage beats random review in all 42 configuration-rate pairs.
- The high-risk rule flags 0.05 to 0.11% of images and removes every false *N. spumigena* detection; it cannot recover images predicted as another class.
