# Stage 1 (RQ1): Representation

Extracts frozen DINOv2, CLIP, BioCLIP 2 and ResNet-18 features and compares single and fused features for image-level classification under the temporal shift from 2022 training data to 2021 test samples. Includes the preliminary tests on feature fusion and confidence calibration.

## Run (from repo root, inside `.venv`)

```bash
python experiments/stage1_rq1_representation/extract_features.py --model resnet18 --limit 200   # smoke test
python experiments/stage1_rq1_representation/extract_features.py --model resnet18               # full, resumable
python experiments/stage1_rq1_representation/check_index_adjacency.py
python experiments/stage1_rq1_representation/make_split.py
```

Models: `resnet18`, `dinov2_vitb14`, `clip_vitb16`, `bioclip2`. Features go to `features/<model>/{train,test}.npy` (float16, git-ignored) with row order in `{train,test}_index.csv`. Preprocessing (pad to square, 224 px, no crop) is in `src/features.py`.

## Results so far

| Model | Dim | Throughput (img/s, M2 MPS, with I/O) | Full run |
|---|---|---|---|
| ResNet-18 | 512 | about 200 | 18 min |
| DINOv2 ViT-B/14 | 768 | about 25 | about 2.4 h (est.) |
| CLIP ViT-B/16 | 512 | about 30 | about 2 h (est.) |
| BioCLIP 2 (ViT-L/14) | 768 | 7 to 9 | about 7 to 8 h (est.) |

**Validation split.** Training filenames have no sample ID, and neighbouring indices are no more similar than random same-class pairs (`index_adjacency.png`; the 2021 control sorted by sample shows a clear effect). Indices do not follow acquisition order, so a per-class stratified random split (80/20, seed 0) is used: `outputs/train_val_split.csv.gz`.
