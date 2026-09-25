"""Extract frozen features for every image in the Stage 0 image table (RQ1).

Features are written in shards so an interrupted run resumes where it stopped:
    features/<model>/<dataset>/shard_XXXX.npy   (float16, rows follow the index)
    features/<model>/<dataset>.npy + <dataset>_index.csv   (merged when all shards exist)

Usage (from repo root, inside .venv):
    python experiments/stage1_rq1_representation/extract_features.py --model resnet18 --limit 200   # smoke
    python experiments/stage1_rq1_representation/extract_features.py --model resnet18               # full
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.features import MODELS, get_device, load_extractor  # noqa: E402

IMAGE_TABLE = REPO_ROOT / "experiments/stage0_data_audit/outputs/image_table.csv.gz"
DATA_ROOT = REPO_ROOT / "data"
FEATURE_ROOT = REPO_ROOT / "features"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
SHARD_SIZE = 5000
SEED = 0


class ImageList(Dataset):
    def __init__(self, rel_paths, preprocess):
        self.rel_paths = list(rel_paths)
        self.preprocess = preprocess

    def __len__(self):
        return len(self.rel_paths)

    def __getitem__(self, i):
        try:
            with Image.open(DATA_ROOT / self.rel_paths[i]) as im:
                return self.preprocess(im), i, True
        except Exception:  # corrupt image: return a placeholder and flag it
            return torch.zeros(3, 224, 224), i, False


def extract_shard(ext, device, rel_paths, batch_size, workers):
    loader = DataLoader(ImageList(rel_paths, ext.preprocess), batch_size=batch_size,
                        num_workers=workers, persistent_workers=False)
    feats = np.zeros((len(rel_paths), ext.dim), dtype=np.float16)
    ok = np.ones(len(rel_paths), dtype=bool)
    with torch.inference_mode():
        for x, idx, good in loader:
            y = ext.forward(ext.model, x.to(device)).float().cpu().numpy()
            feats[idx.numpy()] = y.astype(np.float16)
            ok[idx.numpy()] = good.numpy()
    return feats, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=MODELS)
    ap.add_argument("--datasets", nargs="+", default=["train", "test"])
    ap.add_argument("--limit", type=int, default=None, help="first N images per dataset (smoke test)")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    torch.manual_seed(SEED)
    device = get_device()
    table = pd.read_csv(IMAGE_TABLE, usecols=["dataset", "class", "rel_path"])
    root = FEATURE_ROOT / ("smoke" if args.limit else "") / args.model
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    t_load = time.time()
    ext = load_extractor(args.model, device)
    print(f"{args.model} loaded on {device} in {time.time() - t_load:.0f}s, dim {ext.dim}", flush=True)

    log = []
    for ds in args.datasets:
        index = table[table.dataset == ds].reset_index(drop=True)
        if args.limit:
            index = index.sample(n=min(args.limit, len(index)), random_state=SEED).reset_index(drop=True)
        shard_dir = root / ds
        shard_dir.mkdir(parents=True, exist_ok=True)
        n_shards = (len(index) + SHARD_SIZE - 1) // SHARD_SIZE
        t0, n_done, bad = time.time(), 0, []
        for k in range(n_shards):
            f = shard_dir / f"shard_{k:04d}.npy"
            rows = index.iloc[k * SHARD_SIZE:(k + 1) * SHARD_SIZE]
            if f.exists():
                continue
            feats, ok = extract_shard(ext, device, rows.rel_path, args.batch_size, args.workers)
            np.save(f, feats)
            bad += rows.rel_path[~ok].tolist()
            n_done += len(rows)
            rate = n_done / (time.time() - t0)
            left = (len(index) - (k + 1) * SHARD_SIZE) / rate if rate else 0
            print(f"  [{ds}] shard {k + 1}/{n_shards}: {rate:.1f} img/s, ~{max(left, 0) / 60:.0f} min left",
                  flush=True)
        merged = np.concatenate([np.load(shard_dir / f"shard_{k:04d}.npy") for k in range(n_shards)])
        assert merged.shape == (len(index), ext.dim), merged.shape
        np.save(root / f"{ds}.npy", merged)
        index.to_csv(root / f"{ds}_index.csv", index=False)
        for k in range(n_shards):  # shards are only needed for resuming; free the disk space
            (shard_dir / f"shard_{k:04d}.npy").unlink()
        if bad:
            pd.DataFrame({"rel_path": bad}).to_csv(root / f"{ds}_corrupt.csv", index=False)
        elapsed = time.time() - t0
        log.append({"model": args.model, "dataset": ds, "n_images": len(index), "n_extracted_now": n_done,
                    "seconds": round(elapsed, 1), "img_per_s": round(n_done / elapsed, 1) if n_done else None,
                    "n_corrupt": len(bad), "nan_rows": int(np.isnan(merged.astype(np.float32)).any(1).sum()),
                    "smoke": bool(args.limit), "batch_size": args.batch_size, "workers": args.workers,
                    "device": str(device), "torch": torch.__version__})
        print(f"  [{ds}] done: {merged.shape}, {len(bad)} corrupt, {elapsed:.0f}s", flush=True)

    log_file = OUT_DIR / "extraction_log.csv"
    pd.DataFrame(log).to_csv(log_file, mode="a", header=not log_file.exists(), index=False)


if __name__ == "__main__":
    main()
