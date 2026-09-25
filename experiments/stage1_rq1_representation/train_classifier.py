"""Train logistic regression on frozen features and evaluate on the 2022 validation split (RQ1).

Only the 2022 fit/val split is used here. The 2021 test set is evaluated once, later, by a
separate script after all choices (features, fusion, C, class weights, temperature) are fixed.

Usage (from repo root, inside .venv):
    python experiments/stage1_rq1_representation/train_classifier.py --features resnet18 --limit 100   # smoke
    python experiments/stage1_rq1_representation/train_classifier.py --features resnet18
    python experiments/stage1_rq1_representation/train_classifier.py --features resnet18 dinov2_vitb14  # fusion
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.classify import LRClassifier, image_metrics, load_features  # noqa: E402
from src.ifcb_data import load_json  # noqa: E402

SPLIT_FILE = Path(__file__).resolve().parent / "outputs/train_val_split.csv.gz"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
CKPT_DIR = REPO_ROOT / "checkpoints/stage1"
C_GRID = [0.1, 1.0, 10.0]
CLASS_WEIGHTS = {"none": None, "balanced": "balanced"}
SEED = 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", nargs="+", required=True)
    ap.add_argument("--C", nargs="+", type=float, default=C_GRID)
    ap.add_argument("--limit", type=int, default=None, help="max fit images per class (smoke test)")
    args = ap.parse_args()

    taxa = load_json("taxa.json")
    targets = list(dict.fromkeys(taxa["primary_targets"] + taxa["reported_separately"] + taxa["high_risk"]))
    feat_name = "+".join(args.features)

    X, index = load_features(args.features, "train")
    split = pd.read_csv(SPLIT_FILE)
    assert index.rel_path.equals(split.rel_path), "feature rows and split file are not aligned"
    y = split["class"].to_numpy()
    fit, val = (split.split == "fit").to_numpy(), (split.split == "val").to_numpy()
    if args.limit:
        rng = np.random.default_rng(SEED)
        keep = np.zeros(len(split), bool)
        for c in np.unique(y):
            rows = np.flatnonzero(fit & (y == c))
            keep[rng.choice(rows, min(args.limit, len(rows)), replace=False)] = True
        fit = keep
    print(f"features {feat_name}: dim {X.shape[1]}, fit {fit.sum()}, val {val.sum()}", flush=True)

    out = OUT_DIR / ("smoke" if args.limit else "") / "classifier"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for cw_name, cw in CLASS_WEIGHTS.items():
        for C in args.C:
            t0 = time.time()
            clf = LRClassifier(C=C, class_weight=cw, seed=SEED).fit(X[fit], y[fit])
            proba = clf.predict_proba(X[val])
            summ, per_class = image_metrics(y[val], proba, clf.classes_, targets)
            run = f"{feat_name}__{cw_name}__C{C:g}"
            rows.append({"features": feat_name, "class_weight": cw_name, "C": C, "dim": X.shape[1],
                         "n_iter": int(clf.lr.n_iter_.max()), "fit_seconds": round(time.time() - t0, 1), **summ})
            per_class.to_csv(out / f"val_per_class__{run}.csv", index=False)
            print(f"  {cw_name:8s} C={C:<5g} macro F1 {summ['macro_f1']:.4f}  acc {summ['accuracy']:.4f}  "
                  f"ECE {summ['ece']:.4f}  ({rows[-1]['fit_seconds']}s, {rows[-1]['n_iter']} iter)", flush=True)
            if not args.limit:
                CKPT_DIR.mkdir(parents=True, exist_ok=True)
                joblib.dump(clf, CKPT_DIR / f"lr__{run}.joblib")

    res = pd.DataFrame(rows)
    res_file = out / "val_results.csv"
    if res_file.exists():  # replace earlier rows of the same feature set
        old = pd.read_csv(res_file)
        res = pd.concat([old[old.features != feat_name], res], ignore_index=True)
    res.to_csv(res_file, index=False)
    with open(out / f"config__{feat_name}.json", "w") as f:
        json.dump({"features": args.features, "C_grid": args.C, "class_weights": list(CLASS_WEIGHTS),
                   "limit": args.limit, "seed": SEED, "split": "stratified random 80/20",
                   "scaler": "StandardScaler after per-model L2 normalisation"}, f, indent=2)

    # best C per class-weight setting, selected on validation macro F1
    cur = res[res.features == feat_name]
    best = cur.loc[cur.groupby("class_weight").macro_f1.idxmax()]
    cols = ["class_weight", "C", "macro_f1", "accuracy", "ece"] + [f"f1_{c}" for c in targets]
    print("\nBest C per setting (validation macro F1):")
    print(best[cols].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
