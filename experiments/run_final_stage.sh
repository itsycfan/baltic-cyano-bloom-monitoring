#!/usr/bin/env bash
# After all four single backbones are extracted: BioCLIP 2 pipeline, the two pre-registered
# fusion candidates (top-2 singles by val macro F1, and all four), then the T1 decision and summaries.
# Usage (from repo root): bash experiments/run_final_stage.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python

[ -f checkpoints/preds/bioclip2__none.npz ] || bash experiments/run_feature_pipeline.sh bioclip2

TOP2=$($PY - <<'E'
import pandas as pd
r = pd.read_csv("experiments/stage1_rq1_representation/outputs/classifier/val_results.csv")
r = r[(r.class_weight == "none") & ~r.features.str.contains(r"\+")]
best = r.groupby("features").macro_f1.max().sort_values(ascending=False)
order = ["resnet18", "dinov2_vitb14", "clip_vitb16", "bioclip2"]
print(" ".join(sorted(best.index[:2], key=order.index)))
E
)
echo "=== top-2 singles by val macro F1: $TOP2"
TOP2_NAME=$(echo "$TOP2" | tr ' ' '+')
[ -f "checkpoints/preds/${TOP2_NAME}__none.npz" ] || bash experiments/run_feature_pipeline.sh $TOP2
bash experiments/run_feature_pipeline.sh resnet18 dinov2_vitb14 clip_vitb16 bioclip2

$PY experiments/stage1_rq1_representation/summarize_rq1.py
$PY experiments/summarize_all.py
echo "=== final stage done $(date '+%H:%M')"
