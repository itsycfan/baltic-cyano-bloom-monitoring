#!/usr/bin/env bash
# Run the full RQ1 -> RQ2 -> RQ3 pipeline for one feature set (single backbone or fusion).
# Usage (from repo root): bash experiments/run_feature_pipeline.sh resnet18
#                         bash experiments/run_feature_pipeline.sh resnet18 dinov2_vitb14   # fusion
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
FEAT_ARGS=("$@")
FEAT_NAME=$(IFS=+; echo "$*")

echo "=== [$FEAT_NAME] $(date '+%H:%M') logistic regression grid (val)"
$PY experiments/stage1_rq1_representation/train_classifier.py --features "${FEAT_ARGS[@]}"
echo "=== [$FEAT_NAME] $(date '+%H:%M') RQ1 evaluation (T2, 2021 metrics)"
$PY experiments/stage1_rq1_representation/evaluate_rq1.py --features "${FEAT_ARGS[@]}"
echo "=== [$FEAT_NAME] $(date '+%H:%M') RQ2 abundance"
$PY experiments/stage2_rq2_abundance/run_abundance.py --features "$FEAT_NAME"
for CW in none balanced; do
  echo "=== [$FEAT_NAME] $(date '+%H:%M') RQ3 review, class weight $CW"
  $PY experiments/stage3_rq3_selective_review/run_review.py --features "$FEAT_NAME" --class-weight "$CW"
done
echo "=== [$FEAT_NAME] $(date '+%H:%M') done"
