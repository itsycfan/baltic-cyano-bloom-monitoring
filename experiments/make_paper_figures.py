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
    """Black-and-white technical schematic of the method (engineering-drawing style)."""
    from matplotlib.patches import Arc, Rectangle

    K = "black"
    LW = 0.6
    fig = plt.figure(figsize=(7.2, 5.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 155)
    ax.set_aspect("equal")
    ax.axis("off")
    fs, fs_s = 5.6, 4.8

    def box(x, y, w, h, txt="", ls="-", fsz=fs, hatch=None, lw=LW):
        ax.add_patch(Rectangle((x, y), w, h, fill=True, fc="white", ec=K, lw=lw, ls=ls, hatch=hatch))
        if txt:
            ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fsz)

    def arrow(p0, p1, ls="-", lw=LW):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", lw=lw, ls=ls, color=K, mutation_scale=5,
                                                        shrinkA=0, shrinkB=0))

    def route(points, ls="-"):
        """Orthogonal connector: straight segments, arrowhead on the last one."""
        for p0, p1 in zip(points[:-2], points[1:-1]):
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=K, lw=LW, ls=ls)
        arrow(points[-2], points[-1], ls=ls)

    def dim_h(x0, x1, y, txt, above=True, ext_from=None, fsz=fs_s):
        """Horizontal dimension line at height y with extension lines from ext_from."""
        if ext_from is not None:
            for x in (x0, x1):
                ax.plot([x, x], [ext_from, y + (0.8 if above else -0.8)], color=K, lw=0.35)
        ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="<|-|>", lw=0.4, color=K,
                                                                   mutation_scale=3.5, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, y + (0.9 if above else -0.9), txt, fontsize=fsz, ha="center",
                va="bottom" if above else "top")

    def dim_v(y0, y1, x, txt, right=True, ext_from=None, fsz=fs_s):
        if ext_from is not None:
            for y in (y0, y1):
                ax.plot([ext_from, x + (0.8 if right else -0.8)], [y, y], color=K, lw=0.35)
        ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="<|-|>", lw=0.4, color=K,
                                                                   mutation_scale=3.5, shrinkA=0, shrinkB=0))
        ax.text(x + (1.0 if right else -1.0), (y0 + y1) / 2, txt, fontsize=fsz, ha="left" if right else "right",
                va="center")

    def panel(x, y, w, h, title):
        ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=K, lw=0.9))
        ax.add_patch(Rectangle((x, y + h - 5), w, 5, fill=True, fc="#e6e6e6", ec=K, lw=0.9))
        ax.text(x + 1.5, y + h - 2.5, title, fontsize=6.0, va="center", weight="bold")

    # ---------------- data band ----------------
    box(2, 136, 96, 15, lw=0.9)
    ax.text(4, 148.2, "2022 TRAINING SET  (2016 to 2019, 50 classes)", fontsize=5.8, weight="bold", va="center")
    ax.text(4, 144.2, "63,074 images; no sample IDs  →  stratified random split 80/20 (seed 0)", fontsize=fs,
            va="center")
    box(4, 137.5, 64, 4.4, "fit: 50,459  (classifier; kNN reference set)")
    box(68, 137.5, 28, 4.4, "val: 12,615  (C, T, τ, M)", ls="--")
    ax.plot([100, 100], [134.5, 152.5], color=K, lw=1.0)
    ax.plot([101.4, 101.4], [134.5, 152.5], color=K, lw=1.0)
    ax.text(100.7, 133.6, "no tuning on 2021", fontsize=fs_s, ha="center", va="top", style="italic")
    box(103, 136, 95, 15, lw=0.9, ls=":")
    ax.text(105, 148.2, "2021 TEST SET  (Utö, expert-verified samples)", fontsize=5.8, weight="bold", va="center")
    ax.text(105, 144.2, "151,235 images = 57,207 classified (48 classes) + 94,028 unclassifiable", fontsize=fs,
            va="center")
    ax.text(105, 139.7, "59 samples → 47 weekly main-series samples (curves); 11 supplementary; 1 excluded",
            fontsize=fs, va="center")
    lx, ly = 113, 128.5
    for i, (ls, t) in enumerate([("-", "data flow"), ("--", "fitted on 2022 validation split"),
                                 (":", "2021 test set: evaluation only")]):
        x0 = lx + [0, 20, 56][i]
        ax.plot([x0, x0 + 5], [ly, ly], color=K, lw=0.8, ls=ls)
        ax.text(x0 + 6, ly, t, fontsize=fs_s, va="center")

    # ---------------- (A) preprocessing ----------------
    panel(2, 70, 60, 54, "(A) Preprocessing")
    rx, ry, rw, rh = 7, 106.5, 24, 3.3
    ax.text(rx, 117.4, "raw ROI (example: Aphanizomenon)", fontsize=fs_s, va="center")
    box(rx, ry, rw, rh)
    ax.plot([rx + 1.5, rx + rw - 1.5], [ry + rh / 2, ry + rh / 2 + 0.3], color=K, lw=1.1)
    dim_h(rx, rx + rw, ry + rh + 2.2, "W = 424 px", above=True, ext_from=ry + rh)
    dim_v(ry, ry + rh, rx + rw + 2.2, "H = 58 px", right=True, ext_from=rx + rw)
    sx, sy, ss = 9, 78, 20
    box(sx, sy, ss, ss, hatch="......")
    ax.add_patch(Rectangle((sx, sy + ss / 2 - 1.4), ss, 2.8, fc="white", ec=K, lw=LW))
    ax.plot([sx + 1.2, sx + ss - 1.2], [sy + ss / 2, sy + ss / 2 + 0.3], color=K, lw=1.0)
    dim_v(sy, sy + ss, sx - 2.2, "S", right=False, ext_from=sx)
    arrow((rx + rw / 2, ry - 0.4), (sx + ss / 2, sy + ss + 0.4))
    ax.text(sx + ss / 2 + 1.5, (ry + sy + ss) / 2, "pad to S × S,\nS = max(W, H)", fontsize=fs_s, va="center")
    ax.text(sx + ss / 2, sy - 1.5, "fill = median border grey", fontsize=fs_s, ha="center", va="top")
    tx, ty, ts = 42, 82, 12
    box(tx, ty, ts, ts, hatch="......")
    ax.add_patch(Rectangle((tx, ty + ts / 2 - 0.9), ts, 1.8, fc="white", ec=K, lw=LW))
    ax.plot([tx + 0.8, tx + ts - 0.8], [ty + ts / 2, ty + ts / 2 + 0.2], color=K, lw=0.9)
    arrow((sx + ss + 0.5, sy + ss / 2), (tx - 0.5, ty + ts / 2))
    ax.text((sx + ss + tx) / 2, sy + ss / 2 + 1.6, "bicubic", fontsize=fs_s, ha="center")
    dim_h(tx, tx + ts, ty + ts + 2.0, "224", above=True, ext_from=ty + ts)
    dim_v(ty, ty + ts, tx + ts + 2.0, "224", right=True, ext_from=tx + ts)
    ax.text(tx + ts / 2, ty - 1.5, "no crop\ngrey → 3 channels\nmodel mean / std", fontsize=fs_s, ha="center",
            va="top")

    # ---------------- (B) representation ----------------
    panel(66, 70, 46, 54, "(B) Frozen representation  [RQ1]")
    bb = [("ResNet-18", "ImageNet, supervised", 512), ("DINOv2 ViT-B/14", "self-supervised", 768),
          ("CLIP ViT-B/16", "image-text, QuickGELU", 512), ("BioCLIP 2 ViT-L/14", "TreeOfLife-200M", 768)]
    ax.text(103.7, 116.2, "L2-normalised", fontsize=fs_s, ha="center", va="center")
    for i, (n, src, d) in enumerate(bb):
        yy = 109 - i * 7.3
        box(68, yy, 26, 5.8, f"{n}\n{src}", fsz=fs_s)
        arrow((94.2, yy + 2.9), (97.5, yy + 2.9))
        box(97.5, yy + 1.4, 12.5, 3.0, f"{d}-D", fsz=fs_s)
    ax.text(89, 85.3, "weights frozen (no fine-tuning)", fontsize=fs_s, ha="center", style="italic")
    cx0, cy0 = 70, 78
    scale = 38 / 2560
    xcur = cx0
    for d, h in zip([512, 768, 512, 768], ["", "////", "", "\\\\\\\\"]):
        ax.add_patch(Rectangle((xcur, cy0), d * scale, 3, fc="white", ec=K, lw=LW, hatch=h))
        xcur += d * scale
    ax.text(cx0, cy0 + 4.0, "fusion x = [x₁; x₂; …] (concatenation)", fontsize=fs_s, va="bottom")
    dim_h(cx0, xcur, cy0 - 2.2, "D = 2560 for all four", above=False, ext_from=cy0)

    # ---------------- (C) decision ----------------
    panel(116, 70, 82, 54, "(C) Decision layer  [RQ1]")
    box(118, 100, 22, 8, "standardise\n(fit split)")
    box(145, 100, 30, 8, "multinomial LR\nz = W x + b,  W ∈ ℝ$^{50×D}$")
    box(180, 100, 16, 8, "softmax\np = σ(z / T)")
    arrow((140, 104), (145, 104))
    arrow((175, 104), (180, 104))
    route([(112, 97), (114, 97), (114, 104), (118, 104)])
    ax.text(160, 114.5, "C ∈ {0.1, 1, 10} by val macro F1\nclass weight: none | balanced", fontsize=fs_s,
            ha="center", va="center")
    arrow((160, 111.8), (160, 108.2), ls="--")
    ax.text(188, 114.5, "T: minimum\nNLL on val", fontsize=fs_s, ha="center", va="center")
    arrow((188, 111.8), (188, 108.2), ls="--")
    px0, py0 = 120, 77
    rng = np.random.default_rng(3)
    pv = rng.random(50) ** 6
    pv[31] = 2.2
    pv = pv / pv.max() * 11
    for i, v in enumerate(pv):
        ax.add_patch(Rectangle((px0 + i * 1.0, py0), 0.7, v, fc=K if i == 31 else "white", ec=K, lw=0.3))
    dim_h(px0, px0 + 49.7, py0 - 2.0, "p over 50 training classes", above=False)
    ax.text(px0 + 31.35, py0 + 11.8, "c = max p", fontsize=fs_s, ha="center", va="bottom")
    route([(188, 100), (188, 96), (178.5, 96), (178.5, 93.5)])
    ax.text(176.5, 92.5, "outputs\nŷ = argmax p\nc = max p\nclosed set: no\n'unknown' label",
            fontsize=fs_s, va="top")

    # ---------------- (D) evidence ----------------
    panel(2, 6, 62, 58, "(D) Evidence layer: cosine kNN  [RQ3]")
    ox, oy, R = 22, 25, 18
    ax.add_patch(Arc((ox, oy), 2 * R, 2 * R, theta1=15, theta2=165, lw=LW, color=K))
    ax.plot([ox - R - 1, ox + R + 1], [oy, oy], color=K, lw=0.3, ls="-.")
    ax.plot(ox, oy, "o", ms=1.6, color=K)
    ax.text(ox - 1.2, oy - 1.0, "O", fontsize=fs_s, ha="right", va="top")
    qa = 90.0
    q = (ox + R * np.cos(np.deg2rad(qa)), oy + R * np.sin(np.deg2rad(qa)))
    angles = [(72, "^"), (79, "o"), (83, "o"), (96, "o"), (101, "s"), (105, "o"), (111, "o"), (40, "s"),
              (132, "^"), (150, "s"), (55, "^"), (124, "o")]
    pts = [((ox + R * np.cos(np.deg2rad(a_)), oy + R * np.sin(np.deg2rad(a_))), m, a_) for a_, m in angles]
    near = sorted(pts, key=lambda t: abs(t[2] - qa))[:7]
    for t in pts:
        ax.plot(*t[0], t[1], ms=2.4, mfc=K if t in near else "white", mec=K, mew=0.5)
    for t in near:
        ax.plot([q[0], t[0][0]], [q[1], t[0][1]], color=K, lw=0.3)
    ax.plot(*q, marker="*", ms=6, mfc="white", mec=K, mew=0.6)
    ax.text(q[0], q[1] + 2.0, "query q", fontsize=fs_s, ha="center", va="bottom")
    nn = min(pts, key=lambda t: abs(t[2] - qa))
    ax.plot([ox, q[0]], [oy, q[1]], color=K, lw=0.5)
    ax.plot([ox, nn[0][0]], [oy, nn[0][1]], color=K, lw=0.5, ls="--")
    a0, a1 = sorted([qa, nn[2]])
    ax.add_patch(Arc((ox, oy), 14, 14, theta1=a0, theta2=a1, lw=0.5, color=K))
    ax.text(ox + 1.2, oy + 8.2, "θ$_{min}$", fontsize=fs_s, va="bottom")
    dim_h(ox, ox + R, oy - 3.2, "‖x‖ = 1", above=False, ext_from=oy)
    ax.text(43, 51, "reference set:\nfit split (50,459)", fontsize=fs_s, va="center")
    ax.text(43, 42.5, "●  7 nearest (k = 7)\n○ △ □  other images;\nmarker = class",
            fontsize=fs_s, va="center")
    ax.text(4, 14.0, "d$_{NN}$ = 1 − cos θ$_{min}$   (large: unlike any training image)", fontsize=fs_s)
    ax.text(4, 9.5, "a = (1/7) Σ$_j$ 1[y$_j$ = ŷ]   (neighbour agreement)", fontsize=fs_s)

    # ---------------- (E) policy ----------------
    panel(68, 6, 64, 58, "(E) Policy layer: triage rules  [RQ3]")
    xs_ = np.linspace(0, 1, 80)
    dens = np.exp(-((xs_ - 0.3) / 0.2) ** 2)
    cut = 0.6
    gate_in = []
    for k, (lab, yb) in enumerate([("s₁ = 1 − c  (low confidence)", 47.5),
                                   ("s₂ = 1 − a  (neighbours disagree)", 36.5),
                                   ("s₃ = d$_{NN}$  (far from training set)", 25.5)]):
        X = 71 + xs_ * 26
        ax.plot(X, yb + dens * 5.5, color=K, lw=0.5)
        ax.plot([71, 97], [yb, yb], color=K, lw=0.4)
        m = xs_ >= cut
        ax.fill_between(X[m], yb, yb + dens[m] * 5.5, facecolor="none", hatch="//////", edgecolor=K, lw=0)
        ax.plot([71 + cut * 26] * 2, [yb, yb + 6.2], color=K, lw=0.6, ls="--")
        ax.text(71 + cut * 26 + 0.5, yb + 6.2, "τ", fontsize=fs_s, va="center")
        ax.text(71, yb + 7.3, lab, fontsize=fs_s, va="bottom")
        gate_in.append(yb + 1.5)
    gx0, gy0 = 112, 25
    box(gx0, gy0, 9, 22, "≥1", fsz=7)
    for k, yb in enumerate(gate_in):
        route([(97.5, yb), (104 + k, yb), (104 + k, gy0 + 18 - k * 4.5), (gx0, gy0 + 18 - k * 4.5)])
    ax.text(71, 18.2, "r: ŷ ∈ {N. spumigena, D. acuminata}", fontsize=fs_s, va="center")
    route([(106, 18.2), (108, 18.2), (108, gy0 + 3.5), (gx0, gy0 + 3.5)])
    route([(gx0 + 9, gy0 + 11), (gx0 + 16, gy0 + 11)])
    ax.text(gx0 + 12.5, gy0 + 12.5, "review", fontsize=fs_s, ha="center", va="bottom")
    ax.text(71, 13.0, "τ$_i$ = (1−α)-quantile of val scores (hatched tail = α),", fontsize=fs_s)
    ax.text(71, 9.6, "one α for s₁–s₃, set by bisection so that", fontsize=fs_s)
    ax.text(71, 6.9, "P$_{val}$(any rule) = nominal rate ∈ {1, 2, 5, 10, 20, 30, 50}%", fontsize=fs_s,
            va="bottom")

    # ---------------- (F) review and abundance ----------------
    panel(136, 6, 62, 58, "(F) Review and abundance  [RQ2, RQ3]")
    box(138, 48.5, 28, 7, "flagged: expert label\n(true; may be unclassifiable)", fsz=fs_s)
    box(169, 48.5, 27, 7, "not flagged:\nkeep ŷ", fsz=fs_s)
    box(138, 39.5, 58, 6, "per sample: n$_c$ = images labelled c;  N = all images", fsz=fs_s)
    arrow((152, 48.5), (152, 45.5))
    arrow((182.5, 48.5), (182.5, 45.5))
    ax.text(139, 35.8, "CC:   p̂$_c$ = n$_c$ / N   (unclassifiable stay in N)", fontsize=fs_s, va="center")
    ax.text(139, 31.6, "ACC:  q* = argmin$_{q ≥ 0, Σq = 1}$ ‖M q − p̂‖²,  with", fontsize=fs_s,
            va="center")
    box(150, 25.2, 27, 4.4, "M$_{ij}$ = P$_{val}$(ŷ = i | y = j)", ls="--", fsz=fs_s)
    ax.text(139, 22.6, "metrics on 47 weekly samples: MAE, Pearson, Spearman,\npeak offset, onset at 1 / 2 / 5% "
            "(1 Jun–30 Sep)", fontsize=fs_s, va="top")
    gx, gy = 140, 9.2
    tt = np.linspace(0, 1, 80)
    truth = 5.6 * np.exp(-((tt - 0.62) / 0.08) ** 2) + 0.2
    pred = truth + 1.6 * np.exp(-((tt - 0.42) / 0.07) ** 2)
    X = gx + tt * 52
    ax.plot(X, gy + truth, color=K, lw=0.9)
    ax.plot(X, gy + pred, color=K, lw=0.7, ls=":")
    ax.plot([gx, gx + 52], [gy, gy], color=K, lw=0.4)
    thr = 1.6
    ax.plot([gx, gx + 52], [gy + thr, gy + thr], color=K, lw=0.4, ls="--")
    ax.text(gx + 52.6, gy + thr, "2%", fontsize=fs_s, va="center")
    on_t, on_p = X[np.argmax(truth >= thr)], X[np.argmax(pred >= thr)]
    for x in (on_p, on_t):
        ax.plot([x, x], [gy + thr, gy - 1.6], color=K, lw=0.35)
    ax.annotate("", xy=(on_t, gy - 1.2), xytext=(on_p, gy - 1.2), arrowprops=dict(
        arrowstyle="<|-|>", lw=0.4, color=K, mutation_scale=3.5, shrinkA=0, shrinkB=0))
    ax.text(on_t + 1.0, gy - 1.2, "Δ onset (early alarm)", fontsize=fs_s, va="center")
    ax.text(gx + 1, gy + 5.0, "solid: truth\ndotted: prediction", fontsize=fs_s, va="center")

    # ---------------- inter-panel connectors ----------------
    arrow((62.2, 97), (65.8, 97))
    route([(80, 70), (80, 67), (33, 67), (33, 64.2)])
    ax.text(81, 67.6, "x", fontsize=fs_s, va="bottom")
    route([(176, 70), (176, 67), (90, 67.0), (90, 64.2)])
    ax.text(177, 67.6, "ŷ, c", fontsize=fs_s, va="bottom")
    route([(64, 35), (66, 35), (66, 30.5), (69.5, 30.5)])
    ax.text(63.5, 37.0, "a, d$_{NN}$", fontsize=fs_s, ha="right", va="center")
    route([(gx0 + 16, gy0 + 11), (134, gy0 + 11), (134, 52), (137.6, 52)])
    fig.savefig(OUT / "fig01_framework.svg", bbox_inches="tight")  # vector copy for the manuscript
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
