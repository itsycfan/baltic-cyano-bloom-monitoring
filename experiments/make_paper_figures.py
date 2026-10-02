"""Paper figures that are not produced by the stage scripts (all from existing outputs, no new analysis).

Writes to experiments/paper_figures/. See experiments/paper_figures/FIGURES.md for the index and draft captions.

Usage (from repo root, inside .venv):
    python experiments/make_paper_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.ifcb_data import load_json  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402

EXP = REPO_ROOT / "experiments"
OUT = EXP / "paper_figures"
SUM = EXP / "summary_outputs"
LABELS = {"resnet18": "ResNet-18", "dinov2_vitb14": "DINOv2", "clip_vitb16": "CLIP", "bioclip2": "BioCLIP 2"}
ORDER = ["resnet18", "clip_vitb16", "bioclip2", "dinov2_vitb14", "resnet18+dinov2_vitb14", "dinov2_vitb14+bioclip2",
         "resnet18+dinov2_vitb14+clip_vitb16+bioclip2"]
SEED = 0


def label(feat):
    return "All four" if feat.count("+") == 3 else " + ".join(LABELS.get(f, f) for f in feat.split("+"))


def fig_framework():
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    ax.set_xlim(-1, 101)
    ax.set_ylim(-2, 36)
    ax.axis("off")
    w, gap, y, h = 12.0, 2.4, 16, 14
    texts = ["IFCB images\nUtö 2021\n(62% unclass.)",
             "Frozen\nbackbone\n(4 models)",
             "Logistic\nregression\n+ temperature",
             "kNN evidence\nagreement,\ndistance",
             "Policy rules\n(any fires\n= review)",
             "Simulated\nexpert\nreview",
             "Abundance\nand bloom\ncurve"]
    xs = [0.5 + i * (w + gap) for i in range(len(texts))]
    for x, t in zip(xs, texts):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="#eef3f8", ec="#335", lw=0.8))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.4)
    for i in range(len(xs) - 1):
        ax.annotate("", xy=(xs[i + 1] - 0.3, y + h / 2), xytext=(xs[i] + w + 0.3, y + h / 2),
                    arrowprops=dict(arrowstyle="->", lw=0.8, color="#335"))
    ax.annotate("", xy=(xs[6] + w / 2, y - 0.3), xytext=(xs[4] + w / 2, y - 0.3),
                arrowprops=dict(arrowstyle="->", lw=0.7, color="#777", connectionstyle="arc3,rad=0.35"))
    ax.text((xs[4] + xs[6]) / 2 + w / 2, y - 8.8, "not flagged: prediction kept", ha="center", fontsize=5.8, color="#555")
    for i0, i1, txt, c in [(1, 2, "RQ1 representation", PALETTE[0]), (3, 5, "RQ3 selective review", PALETTE[2]),
                           (6, 6, "RQ2 abundance", PALETTE[1])]:
        x0, x1 = xs[i0], xs[i1] + w
        ax.plot([x0, x1], [2, 2], color=c, lw=2.2)
        ax.text((x0 + x1) / 2, -1.8, txt, ha="center", fontsize=6.6, color=c)
    save(fig, OUT / "fig01_framework.png")


def fig_examples():
    t = pd.read_csv(EXP / "stage0_data_audit/outputs/image_table.csv.gz", usecols=["dataset", "class", "rel_path"])
    t = t[t.dataset == "test"]
    panels = [("Aphanizomenon_flosaquae", "(a) Aphanizomenon"), ("Dolichospermum-Anabaenopsis", "(b) Dolichospermum"),
              ("Dolichospermum-Anabaenopsis-coiled", "(c) Dolichospermum, coiled"),
              ("Nodularia_spumigena", "(d) Nodularia spumigena"), ("Oscillatoriales", "(e) Oscillatoriales"),
              ("Dinophysis_acuminata", "(f) Dinophysis acuminata"), ("Unclassifiable", "(g) Unclassifiable"),
              ("Unclassifiable", "(h) Unclassifiable")]
    fig, axes = plt.subplots(2, 4, figsize=(7.2, 3.2))
    rng = np.random.default_rng(SEED)
    used = set()
    for ax, (c, title) in zip(axes.flat, panels):
        rows = t[(t["class"] == c) & ~t.rel_path.isin(used)]
        r = rows.iloc[int(rng.integers(len(rows)))]
        used.add(r.rel_path)
        ax.imshow(Image.open(REPO_ROOT / "data" / r.rel_path).convert("L"), cmap="gray")
        ax.set_title(title, fontsize=7)
        ax.axis("off")
    save(fig, OUT / "fig02_example_images.png")


def fig_absorption():
    tg = set(load_json("taxa.json")["primary_targets"] + ["Oscillatoriales", "Dinophysis_acuminata"])
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"wspace": 1.15})
    for ax, feat in zip(axes, ["dinov2_vitb14", "resnet18"]):
        a = pd.read_csv(EXP / f"stage1_rq1_representation/outputs/rq1_eval/unclassifiable_absorption__{feat}__none.csv",
                        index_col=0)["n"]
        share = 100 * a / a.sum()
        top = share.sort_values(ascending=False).head(10)
        extra = share[[c for c in share.index if c in tg and c not in top.index]]
        s = pd.concat([top, extra])[::-1]
        ax.barh(range(len(s)), s.values, color=[PALETTE[3] if c in tg else "#9aa7b4" for c in s.index])
        ax.set_yticks(range(len(s)))
        ax.set_yticklabels([c.replace("_", " ") for c in s.index], fontsize=6.3)
        ax.set_xscale("log")
        ax.set_xlabel("Share of unclassifiable 2021 images (%)")
        ax.set_title(f"{LABELS[feat]}, class weight none", loc="left", fontsize=8.5)
        ax.grid(axis="y", visible=False)
    save(fig, OUT / "fig05_unclassifiable_absorption.png")


def fig_decomposition():
    d = pd.read_csv(SUM / "rq2_cc_error_decomposition.csv")
    d = d[d.series == "N_fixing_filamentous_total"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True, sharex=True)
    for ax, cw in zip(axes, ["none", "balanced"]):
        x = d[d.class_weight == cw].set_index("features").loc[ORDER]
        y = np.arange(len(x))
        ax.barh(y, x.fp_from_unclassifiable_pp, color=PALETTE[3], label="Unclassifiable predicted as N-fixing")
        ax.barh(y, x.fp_from_known_classes_pp, left=x.fp_from_unclassifiable_pp, color=PALETTE[0],
                label="Other known classes predicted as N-fixing")
        ax.barh(y, -x.false_negatives_pp, color=PALETTE[7], label="Missed N-fixing images")
        ax.axvline(0, color="black", lw=0.6)
        ax.set_yticks(y)
        ax.set_yticklabels([label(f) for f in x.index], fontsize=7)
        ax.set_xlabel("Contribution to CC bias (pp)")
        ax.set_title(f"Class weight {cw}", loc="left", fontsize=8.5)
        ax.grid(axis="y", visible=False)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=6.8, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.13))
    save(fig, OUT / "fig07_error_decomposition.png")


def fig_accuracy_vs_abundance():
    r = pd.read_csv(EXP / "stage1_rq1_representation/outputs/rq1_summary/rq1_table.csv")
    m = pd.read_csv(SUM / "rq2_mae_by_feature.csv")
    m = m[m.series == "N_fixing_filamentous_total"].set_index("features")
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    for cw, mk in [("none", "o"), ("balanced", "s")]:
        x = r[r.class_weight == cw].set_index("features")
        for i, f in enumerate(ORDER):
            ax.scatter(x.loc[f, "test_macro_f1"], m.loc[f, f"mae_{cw}_CC"], marker=mk, s=28,
                       color=PALETTE[i % len(PALETTE)], label=label(f) if cw == "none" else None,
                       edgecolor="black" if cw == "balanced" else "none", lw=0.5)
    ax.set_xlabel("2021 macro F1 (image level)")
    ax.set_ylabel("CC MAE, N-fixing total (pp)")
    ax.legend(frameon=False, fontsize=6.3, loc="upper right", title="circle: none, square: balanced",
              title_fontsize=6.3)
    save(fig, OUT / "fig08_accuracy_vs_abundance.png")


def fig_onset():
    c = pd.read_csv(SUM / "rq2_nfix_curve_properties.csv")
    c = c[c.method == "CC"]
    rows = [(f, cw) for cw in ["none", "balanced"] for f in ORDER]
    cols = ["onset_1pct", "onset_2pct", "onset_5pct"]
    M = np.array([[float(c[(c.features == f) & (c.class_weight == cw)][k].iloc[0]) for k in cols] for f, cw in rows])
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    im = ax.imshow(M, cmap="RdBu", vmin=-4, vmax=4, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]:+.0f}" if M[i, j] else "0", ha="center", va="center", fontsize=7)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["1%", "2%", "5%"])
    ax.set_xlabel("Onset threshold (N-fixing total)")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{label(f)} ({cw})" for f, cw in rows], fontsize=6.5)
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="Predicted minus true onset (weeks)", shrink=0.7)
    save(fig, OUT / "fig09_onset_error.png")


def fig_review_rates():
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    for i, f in enumerate(ORDER):
        t = pd.read_csv(EXP / f"stage3_rq3_selective_review/outputs/{f}__none/t4_thresholds_and_rates.csv")
        ax.plot(100 * t.nominal_rate, 100 * t.realised_rate_2021_main, "-o", ms=2.5, lw=1.0,
                color=PALETTE[i % len(PALETTE)], label=label(f))
    ax.plot([0, 50], [0, 50], ":", color="grey", lw=0.8, label="Nominal = realised")
    ax.set_xlabel("Nominal review rate set on 2022 validation (%)")
    ax.set_ylabel("Realised review rate, 2021 (%)")
    ax.legend(frameon=False, fontsize=6.3)
    save(fig, OUT / "fig11_nominal_vs_realised.png")


def fig_nodularia():
    stage0 = EXP / "stage0_data_audit/outputs"
    s = pd.read_csv(stage0 / "samples_2021.csv", parse_dates=["timestamp"]).set_index("sample_id")
    ids = s.index[s.in_main_series]
    true = pd.read_csv(stage0 / "sample_class_counts_2021.csv", index_col=0).reindex(ids)["Nodularia_spumigena"]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.bar(s.loc[ids, "timestamp"], true, width=3, color="black", label="True N. spumigena images")
    for k, (f, mk) in enumerate([("dinov2_vitb14", "o"), ("bioclip2", "^")]):
        z = np.load(REPO_ROOT / f"checkpoints/preds/{f}__none.npz", allow_pickle=True)
        p = pd.Series(z["test_rel_path"])
        sid = p.str.split("/").str[-1].str.rsplit("_", n=1).str[0]
        pred = pd.Series(z["classes"][z["test_logits"].argmax(1)] == "Nodularia_spumigena").groupby(sid.values).sum()
        pred = pred.reindex(ids, fill_value=0)
        nz = pred > 0
        ax.scatter(s.loc[ids, "timestamp"][nz] + pd.Timedelta(days=1.5 * (k + 1)), pred[nz], marker=mk, s=22,
                   color=PALETTE[3 + k], label=f"Predicted, {LABELS[f]} (all routed to review)")
    ax.set_ylabel("Images per sample")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    save(fig, OUT / "fig12_nodularia_detection.png")


EXISTING = {
    "fig03_ground_truth_bloom_curve.png": "stage0_data_audit/outputs/bloom_curve_2021_ground_truth.png",
    "fig04_macro_f1_val_vs_2021.png": "stage1_rq1_representation/outputs/rq1_summary/macro_f1_val_vs_2021.png",
    "fig06_rq2_curves_dinov2.png": "stage2_rq2_abundance/outputs/dinov2_vitb14/curves_main_series.png",
    "fig10_rq3_mae_vs_review_dinov2.png": "stage3_rq3_selective_review/outputs/dinov2_vitb14__none/mae_vs_review_rate.png",
    "fig13_area_vs_count.png": "stage2_rq2_abundance/outputs/area_proxy/area_vs_count_curves.png",
    "figS1_preprocessing_examples.png": "stage1_rq1_representation/outputs/preprocessing_examples.png",
    "figS2_index_adjacency.png": "stage1_rq1_representation/outputs/index_adjacency.png",
    "figS3_target_f1_2021.png": "stage1_rq1_representation/outputs/rq1_summary/target_f1_2021.png",
    "figS4_reliability_dinov2.png": "stage1_rq1_representation/outputs/rq1_eval/reliability__dinov2_vitb14.png",
    "figS5_class_counts_train_vs_test.png": "stage0_data_audit/outputs/class_counts_train_vs_test.png",
    "figS6_sample_coverage.png": "stage0_data_audit/outputs/sample_coverage_2021.png",
    "figS7_threshold_filter_dinov2.png": "stage2_rq2_abundance/outputs/threshold_filter/curves__dinov2_vitb14__none.png",
    "figS8_rq3_triage_by_feature.png": "summary_outputs/rq3_triage_by_feature.png",
    "figS9_triage_curves_dinov2.png": "stage3_rq3_selective_review/outputs/dinov2_vitb14__none/curves_triage_10pct.png",
    "figS10_segmentation_check.png": "stage2_rq2_abundance/outputs/segmentation_check_train.png",
}


def copy_existing():
    import shutil
    for dst, src in EXISTING.items():
        shutil.copy(EXP / src, OUT / dst)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    copy_existing()
    apply_style()
    for f in [fig_framework, fig_examples, fig_absorption, fig_decomposition, fig_accuracy_vs_abundance,
              fig_onset, fig_review_rates, fig_nodularia]:
        f()
        print("ok", f.__name__)


if __name__ == "__main__":
    main()
