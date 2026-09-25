"""Check whether training image indices follow acquisition order (RQ1, validation split).

Training filenames are <legacy name>_<index>.png without sample IDs. If indices follow
acquisition order, images with nearby indices come from the same sample more often and
should be more similar than random same-class pairs. Similarity as a function of index
lag also suggests a block size for the pseudo-sample split.

Usage (from repo root, inside .venv):
    python experiments/stage1_rq1_representation/check_index_adjacency.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.ifcb_data import parse_legacy_filename  # noqa: E402
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402

FEATURES = REPO_ROOT / "features/resnet18"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
LAGS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
N_RANDOM = 20000
MIN_GROUP = 30  # legacy-name groups smaller than this are skipped
SEED = 0


def positive_control(rng) -> pd.DataFrame:
    """Same lag-1 test on the 2021 set, sorted by (sample, particle index), where samples are known."""
    X = np.load(FEATURES / "test.npy").astype(np.float32)
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    idx = pd.read_csv(FEATURES / "test_index.csv")
    name = idx.rel_path.str.split("/").str[-1]
    idx["sample"] = name.str.slice(0, 16)
    idx["pi"] = name.str.extract(r"_(\d+)\.png$")[0].astype(int)
    idx["row"] = np.arange(len(idx))
    res = []
    for cls, g in idx[idx["class"] != "Unclassifiable"].groupby("class"):
        if len(g) < 100 or g["sample"].nunique() < 5:
            continue
        g = g.sort_values(["sample", "pi"])
        r, s = g.row.to_numpy(), g["sample"].to_numpy()
        a, b = rng.integers(0, len(r), (2, N_RANDOM))
        keep = a != b
        sim = np.sum(X[r[a[keep]]] * X[r[b[keep]]], axis=1)
        same = s[a[keep]] == s[b[keep]]
        res.append({"class": cls, "n": len(r), "lag1_minus_random":
                    float(np.sum(X[r[:-1]] * X[r[1:]], axis=1).mean() - sim.mean()),
                    "within_minus_across_sample": float(sim[same].mean() - sim[~same].mean())})
    return pd.DataFrame(res)


def main():
    rng = np.random.default_rng(SEED)
    X = np.load(FEATURES / "train.npy").astype(np.float32)
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    idx = pd.read_csv(FEATURES / "train_index.csv")
    parsed = idx.rel_path.str.split("/").str[-1].map(parse_legacy_filename)
    idx["legacy_name"] = parsed.str["legacy_name"]
    idx["legacy_index"] = parsed.str["legacy_index"]
    idx["row"] = np.arange(len(idx))

    rows, per_group = [], []
    for (cls, name), g in idx.groupby(["class", "legacy_name"]):
        if len(g) < MIN_GROUP:
            continue
        r = g.sort_values("legacy_index").row.to_numpy()
        # random same-class baseline within this group
        a, b = rng.integers(0, len(r), (2, min(N_RANDOM, 20 * len(r))))
        keep = a != b
        base = float(np.mean(np.sum(X[r[a[keep]]] * X[r[b[keep]]], axis=1)))
        rec = {"class": cls, "legacy_name": name, "n": len(r), "random": base}
        for lag in LAGS:
            if lag < len(r):
                sim = np.sum(X[r[:-lag]] * X[r[lag:]], axis=1)
                rec[f"lag_{lag}"] = float(sim.mean())
                rows.append({"class": cls, "legacy_name": name, "lag": lag, "n_pairs": len(sim),
                             "excess": float(sim.mean()) - base})
        per_group.append(rec)

    pg = pd.DataFrame(per_group)
    lag_df = pd.DataFrame(rows)
    # pair-weighted mean excess similarity over the random baseline, per lag
    summ = (lag_df.assign(w=lag_df.excess * lag_df.n_pairs).groupby("lag")
            .agg(excess=("w", "sum"), n_pairs=("n_pairs", "sum"), n_groups=("excess", "size")))
    summ["mean_excess"] = summ.excess / summ.n_pairs
    summ["share_groups_positive"] = lag_df.groupby("lag").excess.apply(lambda e: float((e > 0).mean()))
    summ = summ.drop(columns="excess").reset_index()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pg.to_csv(OUT_DIR / "index_adjacency_per_group.csv", index=False)
    summ.to_csv(OUT_DIR / "index_adjacency_summary.csv", index=False)
    with open(OUT_DIR / "index_adjacency_config.json", "w") as f:
        json.dump({"features": "resnet18", "lags": LAGS, "n_random": N_RANDOM, "min_group": MIN_GROUP,
                   "seed": SEED}, f, indent=2)

    pc = positive_control(rng)
    pc.to_csv(OUT_DIR / "index_adjacency_positive_control.csv", index=False)
    apply_style()
    fig, ax = plt.subplots(figsize=(4.5, 3.0))
    ax.plot(summ.lag, summ.mean_excess, "o-", color=PALETTE[0], ms=3.5, label="2022 train, sorted by index")
    ax.scatter([1], [pc.lag1_minus_random.mean()], color=PALETTE[3], marker="D", s=22, zorder=3,
               label="2021 test, sorted by sample (control)")
    ax.axhline(0, color="grey", lw=0.8, ls="--", label="Random same-class pairs")
    ax.set_xscale("log")
    ax.set_xlabel("Index lag within legacy name")
    ax.set_ylabel("Cosine similarity above random")
    ax.legend(frameon=False)
    save(fig, OUT_DIR / "index_adjacency.png")

    print(f"Positive control (2021, known samples): {len(pc)} classes, lag-1 excess "
          f"{pc.lag1_minus_random.mean():.4f} (share > 0: {(pc.lag1_minus_random > 0).mean():.2f}); "
          f"within minus across sample {pc.within_minus_across_sample.mean():.4f}")
    print(f"{len(pg)} legacy-name groups (>= {MIN_GROUP} images), {int(pg.n.sum())} images")
    print(summ.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
