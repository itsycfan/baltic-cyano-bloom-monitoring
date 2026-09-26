"""Exploratory (post hoc) check: does adding absolute particle size reduce closed-set absorption?

Pad-to-square resizing removes absolute size. Finding F2 hypothesised that this is why small
unclassifiable particles are absorbed into small-cell classes. This script appends log width and
log height to the ResNet-18 features and compares against the same classifier without them.
It does not change the primary pipeline. C = 1 and class_weight none, as selected on val for ResNet-18.

Usage (from repo root, inside .venv):
    python experiments/stage1_rq1_representation/exploratory_size_ablation.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.classify import LRClassifier, image_metrics, load_features  # noqa: E402
from src.ifcb_data import load_json  # noqa: E402
from src.quantify import curve_metrics  # noqa: E402

HERE = Path(__file__).resolve().parent
STAGE0 = REPO_ROOT / "experiments/stage0_data_audit/outputs"
OUT = HERE / "outputs/exploratory_size_ablation"
SEED = 0


def main():
    taxa = load_json("taxa.json")
    nfix = taxa["aggregates"]["N_fixing_filamentous_total"]
    targets = list(dict.fromkeys(taxa["primary_targets"] + taxa["reported_separately"] + taxa["high_risk"]))
    img = pd.read_csv(STAGE0 / "image_table.csv.gz", usecols=["rel_path", "width", "height"]).set_index("rel_path")
    split = pd.read_csv(HERE / "outputs/train_val_split.csv.gz")
    Xtr, itr = load_features(["resnet18"], "train")
    Xte, ite = load_features(["resnet18"], "test")
    size_tr = np.log(img.loc[itr.rel_path, ["width", "height"]].to_numpy(float))
    size_te = np.log(img.loc[ite.rel_path, ["width", "height"]].to_numpy(float))
    fit, val = (split.split == "fit").to_numpy(), (split.split == "val").to_numpy()
    y = split["class"].to_numpy()
    y_te = ite["class"].to_numpy()
    cls = y_te != "Unclassifiable"

    samples = pd.read_csv(STAGE0 / "samples_2021.csv", parse_dates=["timestamp"]).set_index("sample_id")
    main_ids = samples.index[samples.in_main_series]
    sid = ite.rel_path.str.split("/").str[-1].str.rsplit("_", n=1).str[0].to_numpy()
    codes = pd.Index(main_ids).get_indexer(sid)
    n = samples.loc[main_ids, "n_images"].to_numpy()
    true_nfix = np.bincount(codes[(codes >= 0) & np.isin(y_te, nfix)], minlength=len(main_ids)) / n

    rows = []
    for name, (A, B) in {"resnet18": (Xtr, Xte),
                         "resnet18 + log size": (np.hstack([Xtr, size_tr]), np.hstack([Xte, size_te]))}.items():
        clf = LRClassifier(C=1.0, class_weight=None, seed=SEED).fit(A[fit], y[fit])
        sv, _ = image_metrics(y[val], clf.predict_proba(A[val]), clf.classes_, targets)
        p = clf.predict_proba(B)
        st, _ = image_metrics(y_te[cls], p[cls], clf.classes_, targets)
        pred = clf.classes_[p.argmax(1)]
        pred_nfix = np.bincount(codes[(codes >= 0) & np.isin(pred, nfix)], minlength=len(main_ids)) / n
        m = curve_metrics(true_nfix, pred_nfix, samples.loc[main_ids, "timestamp"], [0.02], ("06-01", "09-30"),
                          n_boot=500)
        unc = pd.Series(pred[~cls]).value_counts()
        rows.append({"features": name, "val_macro_f1": sv["macro_f1"], "test_macro_f1": st["macro_f1"],
                     "unclass_to_nfix_share": float(np.isin(pred[~cls], nfix).mean()),
                     "unclass_to_pyramimonas": int(unc.get("Pyramimonas_sp", 0)),
                     "unclass_to_beads": int(unc.get("Beads", 0)),
                     "cc_nfix_mae_pp": m["mae_pp"], "cc_nfix_bias_pp": m["bias_pp"], "onset_2pct": m["onset_2pct"]})
    OUT.mkdir(parents=True, exist_ok=True)
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "size_ablation.csv", index=False)
    with open(OUT / "config.json", "w") as f:
        json.dump({"status": "exploratory, post hoc", "C": 1.0, "class_weight": None, "seed": SEED,
                   "size_features": ["log width", "log height"]}, f, indent=2)
    print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
