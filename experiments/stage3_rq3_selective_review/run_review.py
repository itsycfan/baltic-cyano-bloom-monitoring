"""RQ3: evidence signals (T3), review thresholds on validation (T4), and simulated expert review.

Follows docs/ANALYSIS_PLAN.md. Thresholds are set on the 2022 validation split only and applied
unchanged to 2021. Review replaces a prediction with its ground-truth label (unclassifiable
included). Curves are evaluated on the 2021 main series.

Usage (from repo root, inside .venv):
    python experiments/stage3_rq3_selective_review/run_review.py --features resnet18 --class-weight none
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.classify import load_features, softmax  # noqa: E402
from src.evidence import knn_signals  # noqa: E402
from src.ifcb_data import load_json  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402
from src.quantify import curve_metrics  # noqa: E402

STAGE0 = REPO_ROOT / "experiments/stage0_data_audit/outputs"
SPLIT_FILE = REPO_ROOT / "experiments/stage1_rq1_representation/outputs/train_val_split.csv.gz"
RQ2_DIR = REPO_ROOT / "experiments/stage2_rq2_abundance/outputs"
PRED_DIR = REPO_ROOT / "checkpoints/preds"
EVID_DIR = REPO_ROOT / "checkpoints/evidence"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
K = 7
AUROC_KEEP = 0.6
NOMINAL_RATES = [0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50]
N_RANDOM_DRAWS = 20
SEED = 0
UNCLASS = "Unclassifiable"
SERIES = ["N_fixing_filamentous_total", "Aphanizomenon_flosaquae", "Dolichospermum_total", "Oscillatoriales"]
NOD = "Nodularia_spumigena"
# suspicious scores: larger means more suspicious
SIGNALS = {"low_confidence": lambda d: 1 - d["confidence"],
           "neighbour_disagreement": lambda d: 1 - d["neighbour_agreement"],
           "nn_distance": lambda d: d["nn_distance"]}


def compute_signals(feat, cw):
    cache = EVID_DIR / f"{feat}__{cw}.npz"
    z = np.load(PRED_DIR / f"{feat}__{cw}.npz", allow_pickle=True)
    classes, T = z["classes"], float(z["T"])
    out = {"classes": classes, "T": T}
    for part in ["val", "test"]:
        p = softmax(z[f"{part}_logits"], T)
        out[f"{part}_pred"] = classes[p.argmax(1)]
        out[f"{part}_confidence"] = p.max(1)
        out[f"{part}_rel_path"] = z[f"{part}_rel_path"]
    if cache.exists():
        c = np.load(cache, allow_pickle=True)
        for part in ["val", "test"]:
            out[f"{part}_neighbour_agreement"] = c[f"{part}_neighbour_agreement"]
            out[f"{part}_nn_distance"] = c[f"{part}_nn_distance"]
        return out
    models = feat.split("+")
    Xtr, _ = load_features(models, "train")
    Xtr /= np.linalg.norm(Xtr, axis=1, keepdims=True)
    split = pd.read_csv(SPLIT_FILE)
    fit = (split.split == "fit").to_numpy()
    ref_X, ref_y = Xtr[fit], split["class"].to_numpy()[fit]
    val_X = Xtr[(split.split == "val").to_numpy()]
    del Xtr
    sv = knn_signals(ref_X, ref_y, val_X, out["val_pred"], k=K)
    del val_X
    Xte, _ = load_features(models, "test")
    Xte /= np.linalg.norm(Xte, axis=1, keepdims=True)
    st = knn_signals(ref_X, ref_y, Xte, out["test_pred"], k=K)
    EVID_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, **{f"val_{k}": v for k, v in sv.items()}, **{f"test_{k}": v for k, v in st.items()})
    for k, v in sv.items():
        out[f"val_{k}"] = v
    for k, v in st.items():
        out[f"test_{k}"] = v
    return out


def scores(sig, part):
    d = {k: sig[f"{part}_{k}"] for k in ["confidence", "neighbour_agreement", "nn_distance"]}
    return {name: f(d) for name, f in SIGNALS.items()}


def calibrate_alpha(val_scores, val_high_risk, rate):
    """Shared quantile level alpha such that the union of flags reaches `rate` on val."""
    def union_rate(alpha):
        flags = val_high_risk.copy()
        for s in val_scores.values():
            flags |= s > np.quantile(s, 1 - alpha)
        return flags.mean()

    lo, hi = 0.0, rate
    if union_rate(0.0) >= rate:
        return 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if union_rate(mid) < rate else (lo, mid)
    return hi


def abundance_series(labels, sid, ids, n_images, groups):
    """Series fractions per sample; vectorised counting (called many times in the simulation)."""
    s_codes = pd.Index(ids).get_indexer(sid)
    names = list(groups)
    out = np.zeros((len(ids), len(names)))
    for j, name in enumerate(names):
        m = np.isin(labels, groups[name])
        out[:, j] = np.bincount(s_codes[m], minlength=len(ids))
    return pd.DataFrame(out / n_images.to_numpy()[:, None], index=ids, columns=names)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", required=True)
    ap.add_argument("--class-weight", default="none", choices=["none", "balanced"])
    args = ap.parse_args()
    feat, cw = args.features, args.class_weight
    taxa = load_json("taxa.json")
    high_risk = taxa["high_risk"]
    onset_cfg = taxa["onset"]
    window = (onset_cfg["search_window"]["start_month_day"], onset_cfg["search_window"]["end_month_day"])
    groups = {s: [s] for s in ["Aphanizomenon_flosaquae", "Oscillatoriales", NOD]}
    groups.update(taxa["aggregates"])
    out = OUT_DIR / f"{feat}__{cw}"
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    sig = compute_signals(feat, cw)
    split = pd.read_csv(SPLIT_FILE)
    y_val = split.loc[split.split == "val", "class"].to_numpy()
    y_te = pd.Series(sig["test_rel_path"]).str.split("/").str[-2].to_numpy()
    sid = pd.Series(sig["test_rel_path"]).str.split("/").str[-1].str.rsplit("_", n=1).str[0].to_numpy()
    sv, st = scores(sig, "val"), scores(sig, "test")
    pred_val, pred_te = sig["val_pred"], sig["test_pred"]

    # ---- T3: signal validity
    err_val = pred_val != y_val
    err_te = pred_te != y_te  # unclassifiable images are always errors of a closed-set classifier
    cls_te = y_te != UNCLASS
    t3 = []
    for name in SIGNALS:
        t3.append({"signal": name,
                   "auroc_val_misclassified": roc_auc_score(err_val, sv[name]),
                   "auroc_2021_any_error": roc_auc_score(err_te, st[name]),
                   "auroc_2021_misclassified_among_classified": roc_auc_score(err_te[cls_te], st[name][cls_te]),
                   "auroc_2021_unclassifiable_vs_correct": roc_auc_score(
                       ~cls_te[(~cls_te) | (~err_te)], st[name][(~cls_te) | (~err_te)])})
    t3 = pd.DataFrame(t3)
    t3["kept"] = (t3.auroc_val_misclassified >= AUROC_KEEP) | (t3.signal == "nn_distance")
    t3.to_csv(out / "t3_signal_auroc.csv", index=False)
    kept = t3.loc[t3.kept, "signal"].tolist()
    print(t3.round(3).to_string(index=False), flush=True)

    # ---- T4: thresholds on val
    hr_val, hr_te = np.isin(pred_val, high_risk), np.isin(pred_te, high_risk)
    samples = pd.read_csv(STAGE0 / "samples_2021.csv", parse_dates=["timestamp"]).set_index("sample_id")
    main_ids = samples.index[samples.in_main_series]
    n_img = samples.loc[main_ids, "n_images"]
    times = samples.loc[main_ids, "timestamp"]
    in_main = np.isin(sid, main_ids)
    true_series = abundance_series(y_te[in_main], sid[in_main], main_ids, n_img, groups)

    def evaluate(labels, policy, nominal, n_reviewed, extra=None):
        ps = abundance_series(labels, sid[in_main], main_ids, n_img, groups)
        rows = []
        for s in SERIES:
            m = curve_metrics(true_series[s].to_numpy(), ps[s].to_numpy(), times, onset_cfg["thresholds"], window,
                              n_boot=500)
            rows.append({"policy": policy, "nominal_rate": nominal, "n_reviewed": n_reviewed,
                         "realised_rate_main": n_reviewed / in_main.sum(), "series": s, **m, **(extra or {})})
        return rows, ps

    thr_rows, curve_rows, nod_rows, ps_at = [], [], [], {}
    base_rows, ps0 = evaluate(pred_te[in_main], "no_review", 0.0, 0)
    curve_rows += base_rows
    conf_order = np.argsort(sig["test_confidence"][in_main])
    y_main, p_main = y_te[in_main], pred_te[in_main]
    for r in NOMINAL_RATES:
        alpha = calibrate_alpha({k: sv[k] for k in kept}, hr_val, r)
        thr = {k: float(np.quantile(sv[k], 1 - alpha)) for k in kept}
        flag_te = hr_te.copy()
        rule_hits = {"high_risk": hr_te}
        for k, t in thr.items():
            rule_hits[k] = st[k] > t
            flag_te |= rule_hits[k]
        thr_rows.append({"nominal_rate": r, "alpha": alpha, **{f"thr_{k}": v for k, v in thr.items()},
                         "val_rate": float((hr_val | np.column_stack([sv[k] > thr[k] for k in kept]).any(1)).mean()),
                         "realised_rate_2021_all": float(flag_te.mean()),
                         "realised_rate_2021_main": float(flag_te[in_main].mean()),
                         "realised_rate_2021_unclassifiable": float(flag_te[~cls_te].mean()),
                         "realised_rate_2021_classified": float(flag_te[cls_te].mean()),
                         **{f"share_flagged_by_{k}": float(v[in_main].mean()) for k, v in rule_hits.items()}})
        f_main = flag_te[in_main]
        n_rev = int(f_main.sum())
        lab = np.where(f_main, y_main, p_main)
        rows, ps = evaluate(lab, "triage_policy", r, n_rev)
        curve_rows += rows
        ps_at[r] = ps
        # confidence-only at the same realised workload
        lab_c = p_main.copy()
        lab_c[conf_order[:n_rev]] = y_main[conf_order[:n_rev]]
        curve_rows += evaluate(lab_c, "confidence_only_matched", r, n_rev)[0]
        # random review at the same realised workload
        rand = []
        for _ in range(N_RANDOM_DRAWS):
            pick = rng.choice(len(p_main), n_rev, replace=False)
            lab_r = p_main.copy()
            lab_r[pick] = y_main[pick]
            rand += evaluate(lab_r, "random_matched", r, n_rev)[0]
        rd = pd.DataFrame(rand)
        num = ["mae_pp", "mae_ci_low", "mae_ci_high", "bias_pp", "pearson_r", "spearman_r", "peak_offset_weeks"]
        curve_rows += rd.groupby("series")[num].mean().reset_index().assign(
            policy="random_matched", nominal_rate=r, n_reviewed=n_rev,
            realised_rate_main=n_rev / in_main.sum()).to_dict("records")
        # Nodularia: routing and detection after review (main series)
        is_nod, pred_nod = y_main == NOD, p_main == NOD
        nod_rows.append({"nominal_rate": r, "realised_rate_main": n_rev / in_main.sum(),
                         "true_nod_images": int(is_nod.sum()), "true_nod_reviewed": int((is_nod & f_main).sum()),
                         "true_nod_missed_after_review": int((is_nod & (lab != NOD)).sum()),
                         "pred_nod_images": int(pred_nod.sum()),
                         "pred_nod_false_before": int((pred_nod & ~is_nod).sum()),
                         "pred_nod_false_after": int(((lab == NOD) & ~is_nod).sum()),
                         "fp_samples_after": int(pd.Series((lab == NOD) & ~is_nod).groupby(sid[in_main]).any().sum())})

    pd.DataFrame(thr_rows).to_csv(out / "t4_thresholds_and_rates.csv", index=False)
    cr = pd.DataFrame(curve_rows)
    cr.to_csv(out / "review_curve_metrics.csv", index=False)
    pd.DataFrame(nod_rows).to_csv(out / "nodularia_routing.csv", index=False)
    with open(out / "config.json", "w") as f:
        json.dump({"features": feat, "class_weight": cw, "k": K, "auroc_keep": AUROC_KEEP, "kept_signals": kept,
                   "high_risk": high_risk, "nominal_rates": NOMINAL_RATES, "random_draws": N_RANDOM_DRAWS,
                   "seed": SEED, "reference_set": "fit split", "thresholds_from": "2022 validation split"}, f, indent=2)

    # ---- figures
    apply_style()
    rq2 = pd.read_csv(RQ2_DIR / feat / "curve_metrics.csv")
    rq2 = rq2[(rq2.sample_set == "main") & (rq2.class_weight == cw)]
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.2), sharex=True)
    names = taxa["display_names"]
    styles = {"triage_policy": ("-o", PALETTE[0], "Triage policy"),
              "confidence_only_matched": ("-s", PALETTE[2], "Confidence only"),
              "random_matched": ("-^", PALETTE[4], "Random")}
    for ax, s in zip(axes.flat, SERIES):
        d = cr[cr.series == s]
        for pol, (fmt, c, lab) in styles.items():
            e = pd.concat([d[d.policy == "no_review"], d[d.policy == pol]]).sort_values("realised_rate_main")
            ax.plot(100 * e.realised_rate_main, e.mae_pp, fmt, color=c, ms=3, lw=1.1, label=lab)
        acc = rq2[(rq2.series == s) & (rq2.method == "ACC")].mae_pp.iloc[0]
        ax.axhline(acc, color=PALETTE[3], ls="--", lw=0.9, label="ACC (no review)")
        ax.set_title(names.get(s, s), loc="left", fontsize=8.5)
        ax.set_ylim(bottom=0)
    for ax in axes[1]:
        ax.set_xlabel("Images reviewed, 2021 main series (%)")
    for ax in axes[:, 0]:
        ax.set_ylabel("MAE (pp)")
    axes[0, 0].legend(frameon=False, fontsize=7)
    fig.suptitle(f"Abundance error vs review workload, {feat}, class weight {cw}", fontsize=9)
    save(fig, out / "mae_vs_review_rate.png")

    tr = pd.DataFrame(thr_rows)
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.plot(100 * tr.nominal_rate, 100 * tr.realised_rate_2021_main, "o-", color=PALETTE[0], ms=3, label="All images")
    ax.plot(100 * tr.nominal_rate, 100 * tr.realised_rate_2021_classified, "s--", color=PALETTE[2], ms=3,
            label="Classified images")
    ax.plot(100 * tr.nominal_rate, 100 * tr.realised_rate_2021_unclassifiable, "^--", color=PALETTE[3], ms=3,
            label="Unclassifiable images")
    ax.plot([0, 50], [0, 50], ":", color="grey", lw=0.8)
    ax.set_xlabel("Nominal review rate on 2022 val (%)")
    ax.set_ylabel("Realised review rate on 2021 (%)")
    ax.legend(frameon=False, fontsize=7)
    save(fig, out / "nominal_vs_realised_rate.png")

    r10 = 0.10
    fig, axes = plt.subplots(len(SERIES), 1, figsize=(7.0, 7.5), sharex=True)
    for ax, s in zip(axes, SERIES):
        ax.plot(times, 100 * true_series[s], "-o", color="black", ms=2.5, lw=1.5, label="Ground truth")
        ax.plot(times, 100 * ps0[s], "-", color=PALETTE[3], lw=1.0, label="CC, no review")
        ax.plot(times, 100 * ps_at[r10][s], "-", color=PALETTE[0], lw=1.1, label="CC + triage (10% nominal)")
        ax.set_title(names.get(s, s), loc="left", fontsize=8.5)
        ax.set_ylabel("Rel. abundance (%)")
    axes[0].legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0, 1.15))
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    save(fig, out / "curves_triage_10pct.png")

    show = cr[(cr.series == "N_fixing_filamentous_total")].pivot_table(
        index="nominal_rate", columns="policy", values=["mae_pp", "realised_rate_main"]).round(3)
    print(show.to_string())
    print(pd.DataFrame(nod_rows).to_string(index=False))


if __name__ == "__main__":
    main()
