"""Cross-feature-set summary of RQ2 and RQ3 (tables and comparison figures for the report).

Usage (from repo root, inside .venv):
    python experiments/summarize_all.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402

RQ2 = REPO_ROOT / "experiments/stage2_rq2_abundance/outputs"
RQ3 = REPO_ROOT / "experiments/stage3_rq3_selective_review/outputs"
OUT = REPO_ROOT / "experiments/summary_outputs"
LABELS = {"resnet18": "ResNet-18", "dinov2_vitb14": "DINOv2", "clip_vitb16": "CLIP", "bioclip2": "BioCLIP 2"}
SERIES = ["N_fixing_filamentous_total", "Aphanizomenon_flosaquae", "Dolichospermum_total", "Oscillatoriales"]


def label(feat):
    return " + ".join(LABELS.get(f, f) for f in feat.split("+"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rq2 = pd.concat([pd.read_csv(f) for f in sorted(RQ2.glob("*/curve_metrics.csv"))], ignore_index=True)
    rq2m = rq2[rq2.sample_set == "main"]
    t2 = rq2m.pivot_table(index=["features", "series"], columns=["class_weight", "method"], values="mae_pp")
    t2.columns = [f"mae_{cw}_{m}" for cw, m in t2.columns]
    t2.round(4).to_csv(OUT / "rq2_mae_by_feature.csv")
    onset = rq2m[rq2m.series == "N_fixing_filamentous_total"][
        ["features", "class_weight", "method", "bias_pp", "pearson_r", "spearman_r", "peak_offset_weeks",
         "onset_1pct", "onset_2pct", "onset_5pct"]]
    onset.to_csv(OUT / "rq2_nfix_curve_properties.csv", index=False)
    sens = rq2[(rq2.series == "N_fixing_filamentous_total")].pivot_table(
        index=["features", "class_weight", "method"], columns="sample_set", values="mae_pp")
    sens.round(4).to_csv(OUT / "rq2_sensitivity_supplementary.csv")
    det = pd.concat([pd.read_csv(f) for f in sorted(RQ2.glob("*/nodularia_detection.csv"))], ignore_index=True)
    det.to_csv(OUT / "rq2_nodularia_detection.csv", index=False)
    dec = pd.concat([pd.read_csv(f) for f in sorted(RQ2.glob("*/cc_error_decomposition.csv"))], ignore_index=True)
    dec.to_csv(OUT / "rq2_cc_error_decomposition.csv", index=False)

    rows, t3s, curves = [], [], {}
    for d in sorted(RQ3.glob("*__*")):
        if "__without_" in d.name:  # post hoc diagnostics are summarised separately
            continue
        feat, cw = d.name.split("__")
        cr = pd.read_csv(d / "review_curve_metrics.csv")
        t4 = pd.read_csv(d / "t4_thresholds_and_rates.csv")
        t3 = pd.read_csv(d / "t3_signal_auroc.csv").assign(features=feat, class_weight=cw)
        t3s.append(t3)
        nod = pd.read_csv(d / "nodularia_routing.csv")
        curves[(feat, cw)] = cr[cr.series == "N_fixing_filamentous_total"]
        for r in [0.01, 0.05, 0.10]:
            sel = cr[(cr.nominal_rate == r) & (cr.series == "N_fixing_filamentous_total")].set_index("policy")
            rows.append({"features": feat, "class_weight": cw, "nominal_rate": r,
                         "realised_rate_main": float(t4.loc[t4.nominal_rate == r, "realised_rate_2021_main"].iloc[0]),
                         "mae_triage": sel.loc["triage_policy", "mae_pp"],
                         "mae_confidence_only": sel.loc["confidence_only_matched", "mae_pp"],
                         "mae_random": sel.loc["random_matched", "mae_pp"],
                         "onset_2pct_triage": sel.loc["triage_policy", "onset_2pct"],
                         "nod_false_images_after": int(nod.loc[nod.nominal_rate == r, "pred_nod_false_after"].iloc[0]),
                         "nod_true_missed_after": int(nod.loc[nod.nominal_rate == r,
                                                              "true_nod_missed_after_review"].iloc[0])})
    pd.DataFrame(rows).to_csv(OUT / "rq3_summary.csv", index=False)
    pd.concat(t3s).to_csv(OUT / "rq3_t3_auroc_all.csv", index=False)

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
    feats = sorted({f for f, _ in curves}, key=lambda f: (f.count("+"), f))
    for ax, cw in zip(axes, ["none", "balanced"]):
        for i, f in enumerate(feats):
            if (f, cw) not in curves:
                continue
            c = curves[(f, cw)]
            e = pd.concat([c[c.policy == "no_review"], c[c.policy == "triage_policy"]]).sort_values("realised_rate_main")
            ax.plot(100 * e.realised_rate_main, e.mae_pp, "-o", ms=2.5, lw=1.1, color=PALETTE[i % len(PALETTE)],
                    label=label(f))
            acc = rq2m[(rq2m.features == f) & (rq2m.class_weight == cw) & (rq2m.method == "ACC")
                       & (rq2m.series == "N_fixing_filamentous_total")].mae_pp
            if len(acc):
                ax.scatter([0], [acc.iloc[0]], marker="x", color=PALETTE[i % len(PALETTE)], s=22)
        ax.set_title(f"Class weight {cw}", loc="left", fontsize=8.5)
        ax.set_xlabel("Images reviewed, 2021 main series (%)")
    axes[0].set_ylabel("MAE, N-fixing total (pp)")
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Triage policy across feature sets (x at 0: ACC without review)", fontsize=9)
    save(fig, OUT / "rq3_triage_by_feature.png")

    print(t2.xs("N_fixing_filamentous_total", level="series").round(3).to_string())
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
