"""RQ1 summary across feature sets and the T1 fusion decision (pre-registered rule, val only).

T1 rule (docs/ANALYSIS_PLAN.md): a fusion is adopted if its val macro F1 (class_weight none)
exceeds the best single backbone by at least 0.01. The 2021 numbers are reported, never used.

Usage (from repo root, inside .venv):
    python experiments/stage1_rq1_representation/summarize_rq1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.ifcb_data import load_json  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402

HERE = Path(__file__).resolve().parent
RES = HERE / "outputs/rq1_eval/test_results.csv"
OUT = HERE / "outputs/rq1_summary"
SINGLES = ["resnet18", "dinov2_vitb14", "clip_vitb16", "bioclip2"]
LABELS = {"resnet18": "ResNet-18", "dinov2_vitb14": "DINOv2", "clip_vitb16": "CLIP", "bioclip2": "BioCLIP 2"}
T1_MARGIN = 0.01


def label(feat):
    return " + ".join(LABELS.get(f, f) for f in feat.split("+"))


def main():
    taxa = load_json("taxa.json")
    targets = list(dict.fromkeys(taxa["primary_targets"] + taxa["reported_separately"] + taxa["high_risk"]))
    r = pd.read_csv(RES)
    OUT.mkdir(parents=True, exist_ok=True)
    none = r[r.class_weight == "none"].set_index("features")

    singles = [f for f in SINGLES if f in none.index]
    fusions = [f for f in none.index if "+" in f]
    best_single = none.loc[singles, "val_macro_f1"].idxmax()
    decision = {"singles_available": singles, "best_single": best_single,
                "best_single_val_macro_f1": float(none.loc[best_single, "val_macro_f1"]),
                "fusions": {}, "all_four_available": len(singles) == 4}
    adopted = None
    for f in fusions:
        gain = float(none.loc[f, "val_macro_f1"] - none.loc[best_single, "val_macro_f1"])
        decision["fusions"][f] = {"val_macro_f1": float(none.loc[f, "val_macro_f1"]), "gain_over_best_single": gain,
                                  "adopted": gain >= T1_MARGIN}
        if gain >= T1_MARGIN and (adopted is None or none.loc[f, "val_macro_f1"] > none.loc[adopted, "val_macro_f1"]):
            adopted = f
    decision["primary_feature_set"] = adopted or best_single
    decision["rule"] = f"fusion adopted if val macro F1 (class_weight none) >= best single + {T1_MARGIN}"
    with open(OUT / "t1_decision.json", "w") as fh:
        json.dump(decision, fh, indent=2)

    cols = ["features", "class_weight", "C", "T", "val_macro_f1", "test_macro_f1", "val_accuracy", "test_accuracy",
            "val_ece_raw", "val_ece_cal", "test_ece_raw", "test_ece_cal", "unclass_to_nfix_share"]
    tab = r[cols + [f"test_f1_{c}" for c in targets]].copy()
    tab["macro_f1_drop"] = tab.val_macro_f1 - tab.test_macro_f1
    tab.sort_values(["class_weight", "val_macro_f1"], ascending=[True, False]).to_csv(OUT / "rq1_table.csv", index=False)

    apply_style()
    order = none.sort_values("val_macro_f1", ascending=False).index.tolist()
    x = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(max(4.5, 1.1 * len(order) + 1.5), 3.2))
    ax.bar(x - 0.2, none.loc[order, "val_macro_f1"], 0.4, color=PALETTE[0], label="2022 validation")
    ax.bar(x + 0.2, none.loc[order, "test_macro_f1"], 0.4, color=PALETTE[1], label="2021 test")
    for i, f in enumerate(order):
        ax.text(i + 0.2, none.loc[f, "test_macro_f1"] + 0.01, f"{none.loc[f, 'test_macro_f1']:.2f}", ha="center",
                fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([label(f) for f in order], rotation=20, ha="right", fontsize=7.5)
    ax.set_ylabel("Macro F1")
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend(frameon=False, loc="upper right", ncol=2)
    ax.set_title("Image-level macro F1 under the 2022 to 2021 shift (class weight none)", fontsize=8.5, loc="left")
    save(fig, OUT / "macro_f1_val_vs_2021.png")

    hm = none.loc[order, [f"test_f1_{c}" for c in targets]]
    fig, ax = plt.subplots(figsize=(6.2, 0.45 * len(order) + 1.6))
    im = ax.imshow(hm.to_numpy(), cmap="viridis", vmin=0.4, vmax=1.0, aspect="auto")
    for i in range(hm.shape[0]):
        for j in range(hm.shape[1]):
            v = hm.iat[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7, color="white" if v < 0.75 else "black")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([label(f) for f in order], fontsize=7.5)
    ax.set_xticks(range(len(targets)))
    ax.set_xticklabels([taxa["display_names"].get(c, c) for c in targets], rotation=30, ha="right", fontsize=7)
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="2021 F1", shrink=0.8)
    save(fig, OUT / "target_f1_2021.png")

    print(tab[tab.class_weight == "none"][["features", "val_macro_f1", "test_macro_f1", "macro_f1_drop",
                                           "test_ece_raw", "test_ece_cal", "unclass_to_nfix_share"]]
          .sort_values("val_macro_f1", ascending=False).round(3).to_string(index=False))
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
