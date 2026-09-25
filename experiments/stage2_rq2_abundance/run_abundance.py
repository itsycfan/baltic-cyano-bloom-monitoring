"""RQ2: relative abundance curves from classify and count (CC) and adjusted classify and count (ACC).

Uses the cached logits from evaluate_rq1.py. ACC's misclassification matrix comes from the 2022
validation predictions of the same classifier. Rules follow docs/ANALYSIS_PLAN.md.

Usage (from repo root, inside .venv):
    python experiments/stage2_rq2_abundance/run_abundance.py --features resnet18
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.ifcb_data import load_json  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402
from src.quantify import (acc_proportions, count_matrix, curve_metrics,  # noqa: E402
                          misclassification_matrix, series_from_fractions)

STAGE0 = REPO_ROOT / "experiments/stage0_data_audit/outputs"
SPLIT_FILE = REPO_ROOT / "experiments/stage1_rq1_representation/outputs/train_val_split.csv.gz"
PRED_DIR = REPO_ROOT / "checkpoints/preds"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
SERIES = ["N_fixing_filamentous_total", "Aphanizomenon_flosaquae", "Dolichospermum_total", "Oscillatoriales"]
NOD = "Nodularia_spumigena"


def series_groups(taxa):
    g = {s: [s] for s in ["Aphanizomenon_flosaquae", "Oscillatoriales", NOD, "Dinophysis_acuminata"]}
    g.update(taxa["aggregates"])
    return g


def load_truth():
    samples = pd.read_csv(STAGE0 / "samples_2021.csv", parse_dates=["timestamp"]).set_index("sample_id")
    counts = pd.read_csv(STAGE0 / "sample_class_counts_2021.csv", index_col=0)
    return samples, counts


def sample_ids_from_paths(paths):
    return pd.Series(paths).str.split("/").str[-1].str.rsplit("_", n=1).str[0].to_numpy()


def predict_fractions(feat, cw, samples):
    """CC and ACC class fractions per sample (denominator: all images in the sample)."""
    z = np.load(PRED_DIR / f"{feat}__{cw}.npz", allow_pickle=True)
    classes = z["classes"]
    pred_idx = z["test_logits"].argmax(1)
    sid = sample_ids_from_paths(z["test_rel_path"])
    cc_counts = count_matrix(classes[pred_idx], sid, classes).reindex(samples.index)
    assert not cc_counts.isna().any().any(), "sample IDs of predictions do not match the sample table"
    assert (cc_counts.sum(axis=1).to_numpy() == samples["n_images"].to_numpy()).all()
    n = samples["n_images"].to_numpy()[:, None]
    cc = cc_counts / n

    split = pd.read_csv(SPLIT_FILE)
    val = split[split.split == "val"]
    assert np.array_equal(val.rel_path.to_numpy(), z["val_rel_path"])
    cidx = {c: i for i, c in enumerate(classes)}
    M = misclassification_matrix(np.array([cidx[c] for c in val["class"]]), z["val_logits"].argmax(1), len(classes))
    acc = pd.DataFrame(acc_proportions(cc.to_numpy(), M), index=cc.index, columns=classes)
    return {"CC": cc, "ACC": acc}, cc_counts


def error_decomposition(feat, cw, samples, groups, ids):
    """Split CC error per series into false positives from unclassifiable images, false positives
    from other known classes, and false negatives (percentage points, mean over samples)."""
    z = np.load(PRED_DIR / f"{feat}__{cw}.npz", allow_pickle=True)
    pred = z["classes"][z["test_logits"].argmax(1)]
    paths = pd.Series(z["test_rel_path"])
    true = paths.str.split("/").str[-2].to_numpy()
    sid = sample_ids_from_paths(z["test_rel_path"])
    keep = np.isin(sid, ids)
    n = samples.loc[ids, "n_images"]
    rows = []
    for s in SERIES:
        members = groups[s]
        p_in, t_in = np.isin(pred, members), np.isin(true, members)
        parts = {"fp_from_unclassifiable": p_in & (true == "Unclassifiable"),
                 "fp_from_known_classes": p_in & ~t_in & (true != "Unclassifiable"),
                 "false_negatives": t_in & ~p_in}
        row = {"features": feat, "class_weight": cw, "series": s}
        for k, m in parts.items():
            per_sample = pd.Series(m[keep]).groupby(sid[keep]).sum().reindex(ids, fill_value=0) / n
            row[f"{k}_pp"] = float(100 * per_sample.mean())
            row[f"{k}_images"] = int(m[keep].sum())
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", required=True, help="feature set name as used in checkpoints/preds")
    args = ap.parse_args()
    feat = args.features
    taxa = load_json("taxa.json")
    onset_cfg = taxa["onset"]
    window = (onset_cfg["search_window"]["start_month_day"], onset_cfg["search_window"]["end_month_day"])
    groups = series_groups(taxa)

    samples, counts = load_truth()
    samples = samples[samples.is_complete]
    true_frac = counts.reindex(samples.index) / samples["n_images"].to_numpy()[:, None]
    true_series = series_from_fractions(true_frac, groups)
    sets = {"main": samples.index[samples.in_main_series], "all_complete": samples.index}

    out = OUT_DIR / feat
    out.mkdir(parents=True, exist_ok=True)
    rows, det_rows, curves = [], [], {}
    for cw in ["none", "balanced"]:
        fr, cc_counts = predict_fractions(feat, cw, samples)
        for method, frac in fr.items():
            ps = series_from_fractions(frac, groups)
            curves[(cw, method)] = ps
            ps.add_prefix("pred_").join(true_series.add_prefix("true_")).to_csv(
                out / f"sample_series__{cw}__{method}.csv")
            for set_name, ids in sets.items():
                t = samples.loc[ids, "timestamp"]
                for s in SERIES:
                    m = curve_metrics(true_series.loc[ids, s].to_numpy(), ps.loc[ids, s].to_numpy(), t,
                                      onset_cfg["thresholds"], window)
                    rows.append({"features": feat, "class_weight": cw, "method": method, "sample_set": set_name,
                                 "series": s, "n_samples": len(ids), **m})
        # Nodularia detection per main-series sample (CC counts)
        ids = sets["main"]
        tn, pn = counts.reindex(ids)[NOD].to_numpy(), cc_counts.loc[ids, NOD].to_numpy()
        det_rows.append({"features": feat, "class_weight": cw, "method": "CC", "n_samples": len(ids),
                         "samples_true_present": int((tn > 0).sum()), "tp_samples": int(((tn > 0) & (pn > 0)).sum()),
                         "fp_samples": int(((tn == 0) & (pn > 0)).sum()), "fn_samples": int(((tn > 0) & (pn == 0)).sum()),
                         "true_images": int(tn.sum()), "pred_images": int(pn.sum()),
                         "excess_images": int(np.clip(pn - tn, 0, None).sum())})

    res = pd.DataFrame(rows)
    res.to_csv(out / "curve_metrics.csv", index=False)
    dec = pd.DataFrame([r for cw in ["none", "balanced"]
                        for r in error_decomposition(feat, cw, samples, groups, sets["main"])])
    dec.to_csv(out / "cc_error_decomposition.csv", index=False)
    print(dec.round(3).to_string(index=False))
    pd.DataFrame(det_rows).to_csv(out / "nodularia_detection.csv", index=False)

    # figure: main series curves, truth vs CC and ACC (class_weight none) and CC balanced
    apply_style()
    ids = sets["main"]
    t = samples.loc[ids, "timestamp"]
    names = taxa["display_names"]
    fig, axes = plt.subplots(len(SERIES), 1, figsize=(7.0, 8.0), sharex=True)
    for ax, s in zip(axes, SERIES):
        ax.plot(t, 100 * true_series.loc[ids, s], "-o", color="black", lw=1.6, ms=2.5, label="Ground truth")
        ax.plot(t, 100 * curves[("none", "CC")].loc[ids, s], "-", color=PALETTE[3], lw=1.1, label="CC")
        ax.plot(t, 100 * curves[("balanced", "CC")].loc[ids, s], ":", color=PALETTE[3], lw=1.1, label="CC, balanced")
        ax.plot(t, 100 * curves[("none", "ACC")].loc[ids, s], "-", color=PALETTE[0], lw=1.1, label="ACC")
        r = res[(res.class_weight == "none") & (res.sample_set == "main") & (res.series == s)].set_index("method")
        ax.set_title(f"{names.get(s, s)}   MAE: CC {r.loc['CC', 'mae_pp']:.2f} pp, ACC {r.loc['ACC', 'mae_pp']:.2f} pp",
                     loc="left", fontsize=8.5)
        ax.set_ylabel("Rel. abundance (%)")
    axes[0].legend(frameon=False, ncol=4, loc="lower left", bbox_to_anchor=(0, 1.2))
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    axes[-1].set_xlabel("2021 (Utö), main series")
    fig.suptitle(f"Predicted vs ground-truth abundance, {feat}", fontsize=9.5)
    save(fig, out / "curves_main_series.png")

    main_rows = res[(res.sample_set == "main")]
    print(main_rows.pivot_table(index=["series"], columns=["class_weight", "method"], values="mae_pp").round(3).to_string())
    print(pd.DataFrame(det_rows).to_string(index=False))


if __name__ == "__main__":
    main()
