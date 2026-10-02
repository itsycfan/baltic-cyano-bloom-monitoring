"""RQ2 validity check: does the open-set error finding hold under class-specific probability thresholds?

Pre-registered in docs/ANALYSIS_PLAN.md (Addendum 1, plan A). Thresholds follow the idea of
Kraft et al. (2022): one threshold per class, chosen to maximise that class's F1 on validation data;
images whose calibrated top probability is below the threshold of their predicted class are left
unclassified. Only the 2022 validation split is used to set thresholds.

Usage (from repo root, inside .venv):
    python experiments/stage2_rq2_abundance/run_threshold_filter.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.classify import softmax  # noqa: E402
from src.ifcb_data import load_json  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402
from src.quantify import curve_metrics  # noqa: E402

STAGE0 = REPO_ROOT / "experiments/stage0_data_audit/outputs"
SPLIT_FILE = REPO_ROOT / "experiments/stage1_rq1_representation/outputs/train_val_split.csv.gz"
PRED_DIR = REPO_ROOT / "checkpoints/preds"
RQ2_DIR = Path(__file__).resolve().parent / "outputs"
OUT = RQ2_DIR / "threshold_filter"
CONFIGS = [("dinov2_vitb14", "none"), ("resnet18", "none"), ("dinov2_vitb14", "balanced"), ("resnet18", "balanced")]
GRID = np.round(np.arange(0.0, 1.0, 0.01), 2)
UNCLASS = "Unclassifiable"
SERIES = ["N_fixing_filamentous_total", "Aphanizomenon_flosaquae", "Dolichospermum_total", "Oscillatoriales"]
NOD = "Nodularia_spumigena"


def class_thresholds(pred, conf, y, classes):
    """Per-class threshold maximising that class's F1 on validation data (ties: lowest threshold)."""
    out = {}
    for c in classes:
        is_c, pred_c = y == c, pred == c
        n_true = int(is_c.sum())
        best_t, best_f1 = 0.0, -1.0
        for t in GRID:
            acc = pred_c & (conf >= t)
            tp = int((acc & is_c).sum())
            fp = int((acc & ~is_c).sum())
            f1 = 2 * tp / (2 * tp + fp + (n_true - tp)) if (2 * tp + fp + n_true - tp) else 0.0
            if f1 > best_f1 + 1e-12:
                best_t, best_f1 = float(t), f1
        out[c] = {"threshold": best_t, "val_f1": best_f1, "val_n": n_true}
    return out


def series_fractions(labels, sid, ids, n_img, groups):
    codes = pd.Index(ids).get_indexer(sid)
    keep = codes >= 0
    res = {}
    for name, members in groups.items():
        m = keep & np.isin(labels, members)
        res[name] = np.bincount(codes[m], minlength=len(ids)) / n_img
    return pd.DataFrame(res, index=ids)


def decomposition(labels, y, sid, ids, n_img, groups):
    keep = np.isin(sid, ids)
    rows = {}
    for s in SERIES:
        members = groups[s]
        p_in, t_in = np.isin(labels, members), np.isin(y, members)
        parts = {"fp_from_unclassifiable": p_in & (y == UNCLASS), "fp_from_known_classes": p_in & ~t_in & (y != UNCLASS),
                 "false_negatives": t_in & ~p_in}
        for k, m in parts.items():
            per = pd.Series(m[keep]).groupby(sid[keep]).sum().reindex(ids, fill_value=0) / n_img
            rows[(s, k)] = float(100 * per.mean())
    return rows


def main():
    taxa = load_json("taxa.json")
    onset_cfg = taxa["onset"]
    window = (onset_cfg["search_window"]["start_month_day"], onset_cfg["search_window"]["end_month_day"])
    groups = {s: [s] for s in ["Aphanizomenon_flosaquae", "Oscillatoriales", NOD, "Dinophysis_acuminata"]}
    groups.update(taxa["aggregates"])
    targets = list(dict.fromkeys(taxa["primary_targets"] + taxa["reported_separately"] + taxa["high_risk"]))

    split = pd.read_csv(SPLIT_FILE)
    y_val = split.loc[split.split == "val", "class"].to_numpy()
    samples = pd.read_csv(STAGE0 / "samples_2021.csv", parse_dates=["timestamp"]).set_index("sample_id")
    main_ids = samples.index[samples.in_main_series]
    n_img = samples.loc[main_ids, "n_images"].to_numpy()
    times = samples.loc[main_ids, "timestamp"]
    OUT.mkdir(parents=True, exist_ok=True)
    apply_style()

    summary, curve_rows, target_rows = [], [], []
    for feat, cw in CONFIGS:
        z = np.load(PRED_DIR / f"{feat}__{cw}.npz", allow_pickle=True)
        classes, T = z["classes"], float(z["T"])
        pv, pt = softmax(z["val_logits"], T), softmax(z["test_logits"], T)
        pred_v, conf_v = classes[pv.argmax(1)], pv.max(1)
        pred_t, conf_t = classes[pt.argmax(1)], pt.max(1)
        paths = pd.Series(z["test_rel_path"])
        y_te = paths.str.split("/").str[-2].to_numpy()
        sid = paths.str.split("/").str[-1].str.rsplit("_", n=1).str[0].to_numpy()

        thr = class_thresholds(pred_v, conf_v, y_val, classes)
        tvec = np.array([thr[c]["threshold"] for c in pred_t])
        accepted = conf_t >= tvec
        filt = np.where(accepted, pred_t, UNCLASS)
        tag = f"{feat}__{cw}"
        pd.DataFrame([{"class": c, **v} for c, v in thr.items()]).to_csv(OUT / f"thresholds__{tag}.csv", index=False)

        unc = y_te == UNCLASS
        rej = {"features": feat, "class_weight": cw,
               "rejected_share_unclassifiable": float((~accepted[unc]).mean()),
               "rejected_share_classified": float((~accepted[~unc]).mean()),
               "rejected_share_classified_correct": float((~accepted[~unc & (pred_t == y_te)]).mean()),
               "median_threshold": float(np.median([v["threshold"] for v in thr.values()])),
               "share_classes_threshold_zero": float(np.mean([v["threshold"] == 0 for v in thr.values()]))}
        for c in targets:
            is_c = y_te == c
            for name, lab in [("CC", pred_t), ("CC_filtered", filt)]:
                tp = int(((lab == c) & is_c).sum())
                fp = int(((lab == c) & ~is_c).sum())
                fn = int(is_c.sum()) - tp
                target_rows.append({"features": feat, "class_weight": cw, "method": name, "class": c,
                                    "threshold": thr[c]["threshold"], "tp": tp, "fp": fp, "fn": fn,
                                    "fp_from_unclassifiable": int(((lab == c) & unc).sum()),
                                    "precision": tp / (tp + fp) if tp + fp else float("nan"),
                                    "recall": tp / (tp + fn) if tp + fn else float("nan"),
                                    "f1": 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")})

        true_s = series_fractions(y_te, sid, main_ids, n_img, groups)
        dec = {}
        for name, lab in [("CC", pred_t), ("CC_filtered", filt)]:
            ps = series_fractions(lab, sid, main_ids, n_img, groups)
            dec[name] = decomposition(lab, y_te, sid, main_ids, n_img, groups)
            for s in SERIES:
                m = curve_metrics(true_s[s].to_numpy(), ps[s].to_numpy(), times, onset_cfg["thresholds"], window)
                curve_rows.append({"features": feat, "class_weight": cw, "method": name, "series": s, **m,
                                   **{k: dec[name][(s, k)] for k in
                                      ["fp_from_unclassifiable", "fp_from_known_classes", "false_negatives"]}})
            if name == "CC_filtered":
                ps_f = ps
        nod_t = series_fractions(y_te, sid, main_ids, np.ones(len(main_ids)), {NOD: [NOD]})[NOD].to_numpy()
        nod_f = series_fractions(filt, sid, main_ids, np.ones(len(main_ids)), {NOD: [NOD]})[NOD].to_numpy()
        rej.update({"nod_fp_samples_filtered": int(((nod_t == 0) & (nod_f > 0)).sum()),
                    "nod_tp_samples_filtered": int(((nod_t > 0) & (nod_f > 0)).sum()),
                    "nod_pred_images_filtered": int(nod_f.sum()), "nod_true_images": int(nod_t.sum())})
        d = dec["CC_filtered"]
        src = {k: d[("N_fixing_filamentous_total", k)] for k in ["fp_from_unclassifiable", "fp_from_known_classes"]}
        rej["nfix_largest_positive_source_after_filter"] = max(src, key=src.get)
        rej["nfix_unclassifiable_share_of_positive_bias_after_filter"] = (
            src["fp_from_unclassifiable"] / sum(src.values()) if sum(src.values()) else float("nan"))
        summary.append(rej)

        # figure: truth, CC, CC filtered, ACC for the N-fixing total and Oscillatoriales
        acc = pd.read_csv(RQ2_DIR / feat / f"sample_series__{cw}__ACC.csv", index_col=0)
        fig, axes = plt.subplots(2, 1, figsize=(7.0, 4.6), sharex=True)
        for ax, s in zip(axes, ["N_fixing_filamentous_total", "Oscillatoriales"]):
            ax.plot(times, 100 * true_s[s], "-o", color="black", ms=2.5, lw=1.5, label="Ground truth")
            ax.plot(times, 100 * series_fractions(pred_t, sid, main_ids, n_img, groups)[s], "-", color=PALETTE[3],
                    lw=1.0, label="CC")
            ax.plot(times, 100 * acc.loc[main_ids, f"pred_{s}"], ":", color=PALETTE[0], lw=1.1, label="ACC")
            ax.plot(times, 100 * ps_f[s], "-", color=PALETTE[2], lw=1.2, label="CC + class thresholds")
            ax.set_title(taxa["display_names"].get(s, s), loc="left", fontsize=8.5)
            ax.set_ylabel("Rel. abundance (%)")
        axes[0].legend(frameon=False, ncol=4, loc="lower left", bbox_to_anchor=(0, 1.15))
        axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        save(fig, OUT / f"curves__{tag}.png")

    sm = pd.DataFrame(summary)
    sm.to_csv(OUT / "summary.csv", index=False)
    cr = pd.DataFrame(curve_rows)
    cr.to_csv(OUT / "curve_metrics.csv", index=False)
    pd.DataFrame(target_rows).to_csv(OUT / "target_metrics.csv", index=False)
    primary = sm[sm.class_weight == "none"]
    verdict = {"rule": "holds if unclassifiable remains the largest positive source of N-fixing CC bias after "
                       "filtering for both backbones (class weight none)",
               "largest_source_per_backbone": dict(zip(primary.features, primary.nfix_largest_positive_source_after_filter)),
               "holds": bool((primary.nfix_largest_positive_source_after_filter == "fp_from_unclassifiable").all())}
    with open(OUT / "verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    with open(OUT / "config.json", "w") as f:
        json.dump({"preregistration": "docs/ANALYSIS_PLAN.md Addendum 1", "grid": [0.0, 0.99, 0.01],
                   "tie_break": "lowest threshold", "probabilities": "val temperature (T2)",
                   "threshold_data": "2022 validation split only", "configs": CONFIGS}, f, indent=2)

    print(sm.round(3).to_string(index=False))
    n = cr[cr.series == "N_fixing_filamentous_total"]
    print(n[["features", "class_weight", "method", "mae_pp", "bias_pp", "fp_from_unclassifiable",
             "fp_from_known_classes", "false_negatives", "onset_1pct", "onset_2pct", "onset_5pct"]].round(3).to_string(index=False))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
