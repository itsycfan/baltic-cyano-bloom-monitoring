"""Particle area (foreground pixel count) for every image, for the area-weighted biomass proxy.

Pre-registered in docs/ANALYSIS_PLAN.md (Addendum 2). Segmentation rule in src/morphology.py.

Usage (from repo root, inside .venv):
    python experiments/stage2_rq2_abundance/compute_particle_area.py --limit 500   # smoke test
    python experiments/stage2_rq2_abundance/compute_particle_area.py
"""
from __future__ import annotations

import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.morphology import particle_area  # noqa: E402

IMAGE_TABLE = REPO_ROOT / "experiments/stage0_data_audit/outputs/image_table.csv.gz"
OUT = Path(__file__).resolve().parent / "outputs"
WORKERS = 4


def area_of(rel_path: str) -> int:
    try:
        with Image.open(REPO_ROOT / "data" / rel_path) as im:
            return particle_area(im)
    except Exception:
        return -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    t = pd.read_csv(IMAGE_TABLE, usecols=["dataset", "class", "rel_path", "width", "height"])
    if args.limit:
        t = t.sample(args.limit, random_state=0)
    t0 = time.time()
    with Pool(WORKERS) as pool:
        t["area_px"] = pool.map(area_of, t.rel_path.tolist(), chunksize=500)
    t["bbox_px"] = t.width * t.height
    out = OUT / ("particle_area_smoke.csv.gz" if args.limit else "particle_area.csv.gz")
    t[["dataset", "class", "rel_path", "area_px", "bbox_px"]].to_csv(out, index=False, compression="gzip")
    print(f"{len(t)} images in {time.time() - t0:.0f}s; failed {(t.area_px < 0).sum()}; "
          f"zero-area {(t.area_px == 0).sum()}")
    print(t.groupby("class").area_px.median().sort_values().to_string())


if __name__ == "__main__":
    main()
