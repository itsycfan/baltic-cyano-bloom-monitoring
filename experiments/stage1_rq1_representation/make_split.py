"""Stratified train/validation split of the 2022 training set (RQ1, T1 to T4).

Training filenames carry no sample ID and their indices do not follow acquisition order
(see check_index_adjacency.py), so a sample-level split is not possible. A per-class
stratified random split is used; the leakage risk is reported as a limitation.

Usage (from repo root, inside .venv):
    python experiments/stage1_rq1_representation/make_split.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGE_TABLE = REPO_ROOT / "experiments/stage0_data_audit/outputs/image_table.csv.gz"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
VAL_FRACTION = 0.2
SEED = 0


def main():
    t = pd.read_csv(IMAGE_TABLE, usecols=["dataset", "class", "rel_path"])
    t = t[t.dataset == "train"].reset_index(drop=True)
    _, val_idx = train_test_split(t.index, test_size=VAL_FRACTION, stratify=t["class"], random_state=SEED)
    t["split"] = "fit"
    t.loc[val_idx, "split"] = "val"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t[["rel_path", "class", "split"]].to_csv(OUT_DIR / "train_val_split.csv.gz", index=False, compression="gzip")
    counts = t.groupby(["class", "split"]).size().unstack(fill_value=0)
    counts.to_csv(OUT_DIR / "train_val_split_counts.csv")
    with open(OUT_DIR / "train_val_split_config.json", "w") as f:
        json.dump({"method": "stratified random by class", "val_fraction": VAL_FRACTION, "seed": SEED}, f, indent=2)
    print(t.split.value_counts().to_string())
    print("smallest validation classes:\n" + counts.sort_values("val").head(5).to_string())


if __name__ == "__main__":
    main()
