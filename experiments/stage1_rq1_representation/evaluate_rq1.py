"""RQ1 evaluation of one feature set: temperature scaling (T2) on val, then 2021 image-level metrics.

All choices come from the 2022 validation split (see docs/ANALYSIS_PLAN.md): C is the best
val macro F1 per class weighting from train_classifier.py; T is fitted on val logits.
Predictions (logits) are cached for Stage 2 and Stage 3.

Usage (from repo root, inside .venv):
    python experiments/stage1_rq1_representation/evaluate_rq1.py --features resnet18
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.classify import (expected_calibration_error, fit_temperature, image_metrics,  # noqa: E402
                          load_features, softmax)
from src.ifcb_data import load_json  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402

HERE = Path(__file__).resolve().parent
SPLIT_FILE = HERE / "outputs/train_val_split.csv.gz"
VAL_RESULTS = HERE / "outputs/classifier/val_results.csv"
OUT_DIR = HERE / "outputs/rq1_eval"
CKPT_DIR = REPO_ROOT / "checkpoints/stage1"
PRED_DIR = REPO_ROOT / "checkpoints/preds"
UNCLASS = "Unclassifiable"


def reliability(ax, conf, correct, title, n_bins=15):
    edges = np.linspace(0, 1, n_bins + 1)
    b = np.clip(np.digitize(conf, edges[1:-1]), 0, n_bins - 1)
    mids, accs, cnt = [], [], []
    for i in range(n_bins):
        m = b == i
        if m.sum() >= 10:
            mids.append(conf[m].mean())
            accs.append(correct[m].mean())
            cnt.append(m.sum())
    ax.plot([0, 1], [0, 1], "--", color="grey", lw=0.8)
    ax.plot(mids, accs, "o-", ms=3, color=PALETTE[0])
    ax.set_title(title, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", nargs="+", required=True)
    args = ap.parse_args()
    feat = "+".join(args.features)
    taxa = load_json("taxa.json")
    targets = list(dict.fromkeys(taxa["primary_targets"] + taxa["reported_separately"] + taxa["high_risk"]))

    Xtr, idx_tr = load_features(args.features, "train")
    split = pd.read_csv(SPLIT_FILE)
    assert idx_tr.rel_path.equals(split.rel_path)
    val = (split.split == "val").to_numpy()
    y_val = split["class"].to_numpy()[val]
    Xte, idx_te = load_features(args.features, "test")
    y_te = idx_te["class"].to_numpy()
    classified = y_te != UNCLASS

    vr = pd.read_csv(VAL_RESULTS)
    vr = vr[vr.features == feat]
    assert len(vr), f"run train_classifier.py for {feat} first"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    apply_style()

    rows = []
    fig, axes = plt.subplots(2, 4, figsize=(8.0, 4.3), sharex=True, sharey=True)
    for j, cw in enumerate(["none", "balanced"]):
        best = vr[vr.class_weight == cw].sort_values("macro_f1", ascending=False).iloc[0]
        clf = joblib.load(CKPT_DIR / f"lr__{feat}__{cw}__C{best.C:g}.joblib")
        classes = clf.classes_
        cidx = {c: i for i, c in enumerate(classes)}
        lv, lt = clf.decision_function(Xtr[val]), clf.decision_function(Xte)
        assert np.allclose(softmax(lv[:50]), clf.predict_proba(Xtr[val][:50]), atol=1e-5)
        T = fit_temperature(lv, np.array([cidx[c] for c in y_val]))
        np.savez_compressed(PRED_DIR / f"{feat}__{cw}.npz", classes=classes, T=T, C=best.C,
                            val_logits=lv.astype(np.float32), test_logits=lt.astype(np.float32),
                            val_rel_path=split.rel_path[val].to_numpy(), test_rel_path=idx_te.rel_path.to_numpy())

        pv_raw, pv = softmax(lv), softmax(lv, T)
        pt_raw, pt = softmax(lt), softmax(lt, T)
        sv, _ = image_metrics(y_val, pv, classes, targets)
        st, per_class = image_metrics(y_te[classified], pt[classified], classes, targets)
        per_class.to_csv(OUT_DIR / f"test_per_class__{feat}__{cw}.csv", index=False)

        pred_te = classes[pt.argmax(1)]
        unc_pred = pd.Series(pred_te[~classified]).value_counts()
        unc_pred.rename("n").to_csv(OUT_DIR / f"unclassifiable_absorption__{feat}__{cw}.csv")
        corr_v = classes[pv.argmax(1)] == y_val
        corr_t = pred_te[classified] == y_te[classified]
        row = {"features": feat, "class_weight": cw, "C": best.C, "T": round(T, 4),
               "val_macro_f1": sv["macro_f1"], "val_accuracy": sv["accuracy"],
               "val_ece_raw": expected_calibration_error(pv_raw.max(1), corr_v), "val_ece_cal": sv["ece"],
               "test_macro_f1": st["macro_f1"], "test_accuracy": st["accuracy"],
               "test_ece_raw": expected_calibration_error(pt_raw[classified].max(1), corr_t),
               "test_ece_cal": st["ece"],
               "test_mean_conf_classified": float(pt[classified].max(1).mean()),
               "test_mean_conf_unclassifiable": float(pt[~classified].max(1).mean()),
               "unclass_to_targets_share": float(np.isin(pred_te[~classified], taxa["primary_targets"]).mean()),
               "unclass_to_nfix_share": float(np.isin(pred_te[~classified],
                                                      taxa["aggregates"]["N_fixing_filamentous_total"]).mean())}
        for c in targets:
            row[f"val_f1_{c}"] = sv[f"f1_{c}"]
            row[f"test_f1_{c}"] = st[f"f1_{c}"]
        rows.append(row)

        reliability(axes[j, 0], pv_raw.max(1), corr_v, f"{cw}: val, raw")
        reliability(axes[j, 1], pv.max(1), corr_v, f"{cw}: val, T={T:.2f}")
        reliability(axes[j, 2], pt_raw[classified].max(1), corr_t, f"{cw}: 2021, raw")
        reliability(axes[j, 3], pt[classified].max(1), corr_t, f"{cw}: 2021, T={T:.2f}")
        print(f"{feat} [{cw}] C={best.C:g} T={T:.2f} | val macroF1 {sv['macro_f1']:.3f} ECE "
              f"{row['val_ece_raw']:.3f}->{sv['ece']:.3f} | 2021 macroF1 {st['macro_f1']:.3f} acc "
              f"{st['accuracy']:.3f} ECE {row['test_ece_raw']:.3f}->{st['ece']:.3f} | unclassifiable -> "
              f"N-fixing targets {row['unclass_to_nfix_share']:.1%}", flush=True)
    for a in axes[1]:
        a.set_xlabel("Confidence")
    for a in axes[:, 0]:
        a.set_ylabel("Accuracy")
    fig.suptitle(f"Reliability, {feat} (2021: classified images only)", fontsize=9)
    save(fig, OUT_DIR / f"reliability__{feat}.png")

    res_file = OUT_DIR / "test_results.csv"
    res = pd.DataFrame(rows)
    if res_file.exists():
        old = pd.read_csv(res_file)
        res = pd.concat([old[old.features != feat], res], ignore_index=True)
    res.to_csv(res_file, index=False)
    with open(OUT_DIR / f"config__{feat}.json", "w") as f:
        json.dump({"features": args.features, "selection": "C by val macro F1 per class weight",
                   "temperature": "fitted on val NLL", "ece_bins": 15,
                   "test_metrics_on": "classified 2021 images (Unclassifiable excluded)"}, f, indent=2)


if __name__ == "__main__":
    main()
