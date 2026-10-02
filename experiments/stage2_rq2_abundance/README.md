# Stage 2 (RQ2): Abundance Estimation

Aggregates predictions per sample and measures the error of relative abundance curves against the 2021 ground truth, for classify and count (CC) and adjusted classify and count (ACC), with and without class-balanced weights.

## Run (from repo root, inside `.venv`; needs `checkpoints/preds/` from Stage 1)

```bash
python experiments/stage2_rq2_abundance/run_abundance.py --features dinov2_vitb14
python experiments/stage2_rq2_abundance/run_threshold_filter.py      # validity check 1 (pre-registered)
python experiments/stage2_rq2_abundance/compute_particle_area.py     # particle areas for check 2
python experiments/stage2_rq2_abundance/run_area_proxy.py            # validity check 2 (pre-registered)
```

## Outputs

| Path | Content |
|---|---|
| `outputs/<features>/curve_metrics.csv` | MAE (pp) with bootstrap CI, bias, Pearson, Spearman, peak offset, onset error; main series and all complete samples |
| `outputs/<features>/cc_error_decomposition.csv` | CC bias split into unclassifiable, other known classes, missed targets (post hoc, descriptive) |
| `outputs/<features>/sample_series__<weight>__<method>.csv` | Predicted and true series per sample |
| `outputs/<features>/nodularia_detection.csv` | *N. spumigena* as a detection task |
| `outputs/<features>/curves_main_series.png` | Predicted vs true curves |
| `outputs/threshold_filter/` | Class-specific thresholds check; `verdict.json` |
| `outputs/particle_area.csv.gz`, `outputs/area_proxy/` | Particle areas and area-weighted check; `verdict.json` |
| `outputs/segmentation_check_train.png` | Visual check of the segmentation rule |

## Results (DINOv2 primary; all feature sets in `experiments/summary_outputs/rq2_*.csv`)

- N-fixing total MAE: CC 0.42 pp, ACC 0.38 pp (class weight none); CC 0.21 pp, ACC 0.19 pp (balanced). Peak week always correct.
- Unclassifiable particles cause 70 to 85% of the CC over-estimation in every configuration; ACC removes 1 to 17%; balanced weights 44 to 66%.
- Without review, the 2% onset is 3 to 4 weeks early in 9 of 14 configurations.
- *N. spumigena*: all 4 true samples detected; 11 to 20 false-positive samples.
- Both validity checks confirm the open-set conclusion (thresholds reject only 8 to 12% of unclassifiable images; by area, unclassifiable share of bias rises to 79 to 87%).
