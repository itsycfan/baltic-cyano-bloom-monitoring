"""RQ2 validity check: area-weighted relative abundance as a biomass proxy.

Pre-registered in docs/ANALYSIS_PLAN.md (Addendum 2). Each image is weighted by its particle area
(foreground pixels, from compute_particle_area.py); bounding-box area is a sensitivity variant.
Counts and areas are compared with relative MAE (MAE / mean true value).

Usage (from repo root, inside .venv):
    python experiments/stage2_rq2_abundance/run_area_proxy.py
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

from src.ifcb_data import load_json  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402
from src.quantify import curve_metrics  # noqa: E402

STAGE0 = REPO_ROOT / "experiments/stage0_data_audit/outputs"
PRED_DIR = REPO_ROOT / "checkpoints/preds"
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs/area_proxy"
CONFIGS = [("dinov2_vitb14", "none"), ("resnet18", "none"), ("dinov2_vitb14", "balanced"), ("resnet18", "balanced")]
WEIGHTS = {"count": None, "area": "area_px", "bbox": "bbox_px"}
SERIES = ["N_fixing_filamentous_total", "Aphanizomenon_flosaquae", "Dolichospermum_total", "Oscillatoriales"]
UNCLASS = "Unclassifiable"


def weighted_series(labels, sid, w, ids, groups):
    codes = pd.Index(ids).get_indexer(sid)
    keep = codes >= 0
    total = np.bincount(codes[keep], weights=w[keep], minlength=len(ids))
    out = {}
    for name, members in groups.items():
        m = keep & np.isin(labels, members)
        out[name] = np.bincount(codes[m], weights=w[m], minlength=len(ids)) / total
    return pd.DataFrame(out, index=ids)


def main():
    taxa = load_json("taxa.json")
    onset_cfg = taxa["onset"]
    window = (onset_cfg["search_window"]["start_month_day"], onset_cfg["search_window"]["end_month_day"])
    groups = {s: [s] for s in ["Aphanizomenon_flosaquae", "Oscillatoriales"]}
    groups.update(taxa["aggregates"])
    groups["Filamentous_cyanobacteria_total"] = taxa["aggregates"]["N_fixing_filamentous_total"] + ["Oscillatoriales"]

    area = pd.read_csv(HERE / "outputs/particle_area.csv.gz").set_index("rel_path")
    samples = pd.read_csv(STAGE0 / "samples_2021.csv", parse_dates=["timestamp"]).set_index("sample_id")
    main_ids = samples.index[samples.in_main_series]
    times = samples.loc[main_ids, "timestamp"]
    OUT.mkdir(parents=True, exist_ok=True)

    rows, dec_rows, truth_curves, pred_curves = [], [], {}, {}
    for feat, cw in CONFIGS:
        z = np.load(PRED_DIR / f"{feat}__{cw}.npz", allow_pickle=True)
        paths = pd.Series(z["test_rel_path"])
        pred = z["classes"][z["test_logits"].argmax(1)]
        y = paths.str.split("/").str[-2].to_numpy()
        sid = paths.str.split("/").str[-1].str.rsplit("_", n=1).str[0].to_numpy()
        a = area.loc[paths]
        for wname, col in WEIGHTS.items():
            w = np.ones(len(paths)) if col is None else np.maximum(a[col].to_numpy(float), 1.0)
            ts = weighted_series(y, sid, w, main_ids, groups)
            ps = weighted_series(pred, sid, w, main_ids, groups)
            truth_curves[wname] = ts
            pred_curves[(feat, cw, wname)] = ps
            codes = pd.Index(main_ids).get_indexer(sid)
            keep = codes >= 0
            tot = np.bincount(codes[keep], weights=w[keep], minlength=len(main_ids))
            for s in SERIES:
                m = curve_metrics(ts[s].to_numpy(), ps[s].to_numpy(), times, onset_cfg["thresholds"], window, n_boot=500)
                rows.append({"features": feat, "class_weight": cw, "weight": wname, "series": s,
                             "mean_true_pp": float(100 * ts[s].mean()), "rel_mae": m["mae_pp"] / (100 * ts[s].mean()),
                             **m})
                mem = groups[s]
                p_in, t_in = np.isin(pred, mem), np.isin(y, mem)
                parts = {"fp_from_unclassifiable": p_in & (y == UNCLASS),
                         "fp_from_known_classes": p_in & ~t_in & (y != UNCLASS), "false_negatives": t_in & ~p_in}
                d = {"features": feat, "class_weight": cw, "weight": wname, "series": s}
                for k, mk in parts.items():
                    mm = keep & mk
                    d[f"{k}_pp"] = float(100 * (np.bincount(codes[mm], weights=w[mm], minlength=len(main_ids)) / tot).mean())
                dec_rows.append(d)

    res = pd.DataFrame(rows)
    res.to_csv(OUT / "curve_metrics.csv", index=False)
    dec = pd.DataFrame(dec_rows)
    dec["unclassifiable_share_of_positive_bias"] = dec.fp_from_unclassifiable_pp / (
        dec.fp_from_unclassifiable_pp + dec.fp_from_known_classes_pp)
    dec.to_csv(OUT / "cc_error_decomposition.csv", index=False)

    # pre-registered decision (area weights, N-fixing total, class weight none)
    d = dec[(dec.weight == "area") & (dec.series == "N_fixing_filamentous_total") & (dec.class_weight == "none")]
    largest = {r.features: ("fp_from_unclassifiable" if r.fp_from_unclassifiable_pp >= r.fp_from_known_classes_pp
                            else "fp_from_known_classes") for r in d.itertuples()}
    verdict = {"rule": "holds if unclassifiable particles remain the largest positive source of area-weighted N-fixing "
                       "CC bias for both backbones (class weight none)",
               "largest_source_per_backbone": largest,
               "holds": all(v == "fp_from_unclassifiable" for v in largest.values())}
    # descriptive check against Kraft et al. (2022): filamentous share of total in July-August
    ja = truth_curves["area"].loc[main_ids[(times.dt.month >= 7) & (times.dt.month <= 8)]]
    verdict["descriptive_filamentous_area_share_jul_aug"] = {
        "mean": float(ja["Filamentous_cyanobacteria_total"].mean()),
        "max": float(ja["Filamentous_cyanobacteria_total"].max()),
        "count_based_mean": float(truth_curves["count"].loc[ja.index, "Filamentous_cyanobacteria_total"].mean()),
        "note": "Kraft et al. (2022) report filamentous cyanobacteria at about a third of total phytoplankton biomass "
                "in the 2021 bloom season (biovolume-based, high frequency); this is image area, weekly."}
    with open(OUT / "verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    with open(OUT / "config.json", "w") as f:
        json.dump({"preregistration": "docs/ANALYSIS_PLAN.md Addendum 2", "configs": CONFIGS,
                   "weights": WEIGHTS, "segmentation": "src/morphology.py"}, f, indent=2)

    # figure: count vs area truth, and area-weighted predictions (DINOv2)
    apply_style()
    names = taxa["display_names"]
    fig, axes = plt.subplots(3, 1, figsize=(7.0, 6.6), sharex=True)
    ax = axes[0]
    for i, (w, lab) in enumerate([("count", "image count"), ("area", "particle area")]):
        ax.plot(times, 100 * truth_curves[w]["N_fixing_filamentous_total"], "-o", ms=2.5, lw=1.3,
                color=PALETTE[i], label=f"N-fixing total, {lab}")
        ax.plot(times, 100 * truth_curves[w]["Oscillatoriales"], "--", lw=1.0, color=PALETTE[i],
                label=f"Oscillatoriales, {lab}")
    ax.set_title("Ground truth: image count vs particle area", loc="left", fontsize=8.5)
    ax.set_ylabel("Share (%)")
    ax.legend(frameon=False, ncol=2, fontsize=7, loc="upper left")
    for ax, w in zip(axes[1:], ["count", "area"]):
        ax.plot(times, 100 * truth_curves[w]["N_fixing_filamentous_total"], "-o", color="black", ms=2.5, lw=1.5,
                label="Ground truth")
        for i, cw in enumerate(["none", "balanced"]):
            ax.plot(times, 100 * pred_curves[("dinov2_vitb14", cw, w)]["N_fixing_filamentous_total"], "-",
                    color=PALETTE[3 + i * 2], lw=1.0, label=f"CC, DINOv2, class weight {cw}")
        r = res[(res.features == "dinov2_vitb14") & (res.weight == w) & (res.series == "N_fixing_filamentous_total")]
        ax.set_title(f"N-fixing total weighted by {w}: relative MAE " + ", ".join(
            f"{x.class_weight} {x.rel_mae:.2f}" for x in r.itertuples()), loc="left", fontsize=8.5)
        ax.set_ylabel("Share (%)")
    axes[1].legend(frameon=False, ncol=3, fontsize=7, loc="upper left")
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    save(fig, OUT / "area_vs_count_curves.png")

    show = res[res.series == "N_fixing_filamentous_total"].pivot_table(
        index=["features", "class_weight"], columns="weight", values=["rel_mae", "mae_pp"]).round(3)
    print(show.to_string())
    dd = dec[dec.series == "N_fixing_filamentous_total"].pivot_table(
        index=["features", "class_weight"], columns="weight", values="unclassifiable_share_of_positive_bias").round(3)
    print(dd.to_string())
    on = res[(res.series == "N_fixing_filamentous_total")][["features", "class_weight", "weight", "peak_offset_weeks",
                                                             "onset_1pct", "onset_2pct", "onset_5pct"]]
    print(on.to_string(index=False))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
