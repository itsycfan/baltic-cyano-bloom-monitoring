# Stage 1 (RQ1): Representation

Extracts frozen DINOv2, CLIP, BioCLIP 2 and ResNet-18 features and compares single and fused features for image-level classification under the temporal shift from 2022 training data to 2021 test samples. Includes the preliminary tests on feature fusion and confidence calibration.

## Run (from repo root, inside `.venv`)

```bash
python experiments/stage1_rq1_representation/extract_features.py --model resnet18 --limit 200   # smoke test
python experiments/stage1_rq1_representation/extract_features.py --model resnet18               # full, resumable
python experiments/stage1_rq1_representation/check_index_adjacency.py
python experiments/stage1_rq1_representation/make_split.py
python experiments/stage1_rq1_representation/train_classifier.py --features resnet18 --limit 100   # smoke test
python experiments/stage1_rq1_representation/train_classifier.py --features resnet18               # C grid x class weights
```

Models: `resnet18`, `dinov2_vitb14`, `clip_vitb16`, `bioclip2`. Features go to `features/<model>/{train,test}.npy` (float16, git-ignored) with row order in `{train,test}_index.csv`. Preprocessing (pad to square, 224 px, no crop) is in `src/features.py`.

## Results (final)

Feature extraction on an Apple M2 (8 GB), all 214,309 images:

| Model | Dim | Images per second (with I/O) | Total time |
|---|---|---|---|
| ResNet-18 | 512 | 202 | 0.3 h |
| DINOv2 ViT-B/14 | 768 | 24 | 2.5 h |
| CLIP ViT-B/16 (QuickGELU) | 512 | 24 | 2.5 h |
| BioCLIP 2 ViT-L/14 | 768 | 6 | 9.9 h |

Image-level results, class weight none (`outputs/rq1_summary/rq1_table.csv`; balanced rows in the same file):

| Features | Val macro F1 | 2021 macro F1 | 2021 ECE raw | 2021 ECE after T |
|---|---|---|---|---|
| dinov2_vitb14+bioclip2 | 0.950 | 0.728 | 0.064 | 0.024 |
| resnet18+dinov2_vitb14 | 0.947 | 0.704 | 0.090 | 0.030 |
| dinov2_vitb14 | 0.945 | 0.705 | 0.072 | 0.032 |
| resnet18+dinov2_vitb14+clip_vitb16+bioclip2 | 0.944 | 0.755 | 0.037 | 0.023 |
| bioclip2 | 0.931 | 0.705 | 0.028 | 0.028 |
| clip_vitb16 | 0.909 | 0.659 | 0.019 | 0.028 |
| resnet18 | 0.879 | 0.623 | 0.117 | 0.058 |

**T1 decision** (`outputs/rq1_summary/t1_decision.json`): no fusion gains +0.01 on validation, so DINOv2 is the primary feature set. The all-four fusion is best on 2021 and is reported as a finding.

## Scripts and outputs

| Script | Output |
|---|---|
| `extract_features.py` | `features/<model>/{train,test}.npy` (local), `outputs/extraction_log.csv` |
| `check_index_adjacency.py` | `outputs/index_adjacency*.csv`, `index_adjacency.png` (why the split is random) |
| `make_split.py` | `outputs/train_val_split.csv.gz` (fit 50,459 / val 12,615) |
| `train_classifier.py` | `outputs/classifier/val_results.csv`, per-class tables; models in `checkpoints/stage1/` |
| `evaluate_rq1.py` | `outputs/rq1_eval/` (2021 metrics, reliability diagrams, unclassifiable absorption); logits in `checkpoints/preds/` |
| `summarize_rq1.py` | `outputs/rq1_summary/` (table, T1 decision, figures) |
| `exploratory_size_ablation.py` | `outputs/exploratory_size_ablation/` (post hoc: adding size does not reduce absorption) |

Validation scores are optimistic (random split within the training years); the 2021 scores are the honest ones.
