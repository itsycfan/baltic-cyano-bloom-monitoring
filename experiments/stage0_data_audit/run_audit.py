"""Stage 0 data audit.

Parses both SYKE IFCB datasets into an image table, checks class counts against the
dataset description, checks weekly coverage of the 2021 test samples, defines the
one-sample-per-week main series, checks train/test separation, and computes the
ground-truth relative abundance of target cyanobacteria per 2021 sample.

Usage (from repo root):
    python3 experiments/stage0_data_audit/run_audit.py --limit 20   # smoke test
    python3 experiments/stage0_data_audit/run_audit.py              # full run
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.ifcb_data import (  # noqa: E402
    dataset_dirs, list_class_images, load_json, parse_ifcb_filename,
    parse_legacy_filename, select_main_series,
)
from src.plot_style import PALETTE, apply_style, plt, save  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "outputs"


def scan_images(items: list, dataset: str) -> tuple[pd.DataFrame, list]:
    """Read each image once: hash, size, integrity check, filename parsing."""
    rows, corrupt = [], []
    t0 = time.time()
    for i, (cls, path) in enumerate(items):
        row = {"dataset": dataset, "class": cls, "filename": path.name,
               "rel_path": str(path.relative_to(REPO_ROOT / "data"))}
        try:
            raw = path.read_bytes()
            row["md5"] = hashlib.md5(raw).hexdigest()
            with Image.open(io.BytesIO(raw)) as im:
                row["width"], row["height"] = im.size
                im.verify()
        except Exception as e:  # corrupt or unreadable image: record and skip
            corrupt.append({"dataset": dataset, "rel_path": row["rel_path"], "error": repr(e)})
            continue
        parsed = parse_ifcb_filename(path.name) or {}
        row.update(parsed)
        if not parsed:
            row.update(parse_legacy_filename(path.name) or {})
        rows.append(row)
        if (i + 1) % 20000 == 0:
            print(f"  [{dataset}] {i + 1}/{len(items)} images, {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows), corrupt


def class_count_table(img: pd.DataFrame, pdf_counts: dict) -> pd.DataFrame:
    n_train = img[img.dataset == "train"].groupby("class").size()
    n_test = img[img.dataset == "test"].groupby("class").size()
    classes = sorted(set(pdf_counts) | set(n_train.index) | set(n_test.index))
    df = pd.DataFrame({"class": classes})
    df["n_train_pdf"] = df["class"].map(pdf_counts)
    df["n_train"] = df["class"].map(n_train).fillna(0).astype(int)
    df["train_minus_pdf"] = df["n_train"] - df["n_train_pdf"]
    df["n_test"] = df["class"].map(n_test).fillna(0).astype(int)
    return df.sort_values("n_train", ascending=False).reset_index(drop=True)


def sample_table(test: pd.DataFrame, taxa: dict, unclass: str, rule: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-sample counts of every class plus target relative abundances (all images as denominator)."""
    counts = test.pivot_table(index="sample_id", columns="class", values="filename",
                              aggfunc="count", fill_value=0)
    meta = test.groupby("sample_id").agg(timestamp=("timestamp", "first"), iso_year=("iso_year", "first"),
                                         iso_week=("iso_week", "first"), instrument=("instrument", "first"))
    s = meta.join(counts.sum(axis=1).rename("n_images"))
    s["n_unclassifiable"] = counts[unclass] if unclass in counts else 0
    s["n_classified"] = s["n_images"] - s["n_unclassifiable"]
    s["frac_unclassifiable"] = s["n_unclassifiable"] / s["n_images"]

    groups = {c: [c] for c in taxa["primary_targets"] + taxa["reported_separately"] + taxa["high_risk"]}
    groups.update(taxa["aggregates"])
    for name, members in groups.items():
        present = [m for m in members if m in counts.columns]
        n = counts[present].sum(axis=1) if present else 0
        s[f"n_{name}"] = n
        s[f"ra_{name}"] = n / s["n_images"]

    s = s.join(test.groupby("sample_id").particle_index.max().rename("max_particle_index"))
    s["particle_coverage"] = s["n_images"] / s["max_particle_index"]
    s["is_complete"] = s["particle_coverage"] >= rule["min_particle_coverage"]

    s = s.sort_values("timestamp").reset_index()
    s["in_main_series"] = False
    complete = s[s.is_complete]
    s.loc[complete.index, "in_main_series"] = select_main_series(
        complete, rule["reference_weekday"], rule["reference_hour"])
    s["n_samples_in_week"] = s.groupby(["iso_year", "iso_week"])["sample_id"].transform("count")
    return s, counts.loc[s["sample_id"]]


def weekly_coverage(s: pd.DataFrame, year: int) -> pd.DataFrame:
    weeks = pd.DataFrame({"iso_week": range(1, datetime(year, 12, 28).isocalendar()[1] + 1)})
    s = s[s.is_complete]
    g = s.groupby("iso_week").agg(n_samples=("sample_id", "count"), sample_ids=("sample_id", " ".join))
    main = s[s.in_main_series].set_index("iso_week")["sample_id"].rename("main_sample_id")
    w = weeks.join(g, on="iso_week").join(main, on="iso_week")
    w["n_samples"] = w["n_samples"].fillna(0).astype(int)
    w["status"] = np.select([w.n_samples == 0, w.n_samples == 1], ["missing", "single"], "multiple")
    return w


def temporal_check(img: pd.DataFrame, cfg: dict) -> dict:
    test = img[img.dataset == "test"]
    train = img[img.dataset == "train"]
    train_md5, test_md5 = set(train.md5), set(test.md5)
    shared = train_md5 & test_md5
    return {
        "test_time_min": str(test.timestamp.min()),
        "test_time_max": str(test.timestamp.max()),
        "test_all_in_year": bool((test.timestamp.dt.year == cfg["test"]["year"]).all()),
        "train_images_with_ifcb_timestamp": int(train["timestamp"].notna().sum()) if "timestamp" in train else 0,
        "train_years_per_description": cfg["train"]["years_per_description"],
        "train_test_identical_images": len(shared),
        "train_duplicate_images_within": int(train.md5.duplicated().sum()),
        "test_duplicate_images_within": int(test.md5.duplicated().sum()),
        "note": ("Training filenames carry no IFCB timestamp, so separation is verified from the dataset "
                 "description (2016 to 2019) plus the absence of byte-identical images across sets."),
    }


def plot_bloom_curve(s: pd.DataFrame, taxa: dict, path: Path) -> None:
    names = taxa["display_names"]
    panels = [
        ("Bloom-forming filamentous cyanobacteria",
         ["N_fixing_filamentous_total", "Aphanizomenon_flosaquae", "Dolichospermum_total", "Oscillatoriales"]),
        ("Low-abundance, high-risk taxa", ["Nodularia_spumigena", "Dinophysis_acuminata"]),
    ]
    main, extra = s[s.in_main_series], s[~s.in_main_series & s.is_complete]
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.2), sharex=True, gridspec_kw={"height_ratios": [1.6, 1]})
    for ax, (title, keys) in zip(axes, panels):
        for i, k in enumerate(keys):
            c = PALETTE[i]
            ls = "--" if k == "Oscillatoriales" else "-"
            lw = 1.8 if k == "N_fixing_filamentous_total" else 1.2
            ax.plot(main.timestamp, 100 * main[f"ra_{k}"], ls, color=c, lw=lw, marker="o", ms=2.8, label=names[k])
            ax.scatter(extra.timestamp, 100 * extra[f"ra_{k}"], s=14, facecolors="none", edgecolors=c, lw=0.8)
        ax.set_title(title, loc="left")
        ax.set_ylabel("Relative abundance (%)")
        ax.legend(frameon=False, ncol=2, loc="upper left")
    # mark weeks without any sample and anomalously small samples
    for ax in axes:
        ax.scatter([], [], s=14, facecolors="none", edgecolors="grey", label="Supplementary sample")
    axes[1].legend(frameon=False, ncol=2, loc="upper left")
    for _, r in s[~s.is_complete].iterrows():  # incomplete samples are excluded; mark the gap
        for ax in axes:
            ax.axvline(r.timestamp, color="grey", lw=0.6, ls=":")
        axes[0].annotate("incomplete\nsample", (r.timestamp, axes[0].get_ylim()[1] * 0.5),
                         fontsize=6.5, color="grey", ha="left", xytext=(2, 0), textcoords="offset points")
    axes[1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    axes[1].set_xlabel("2021 (Utö)")
    fig.align_ylabels(axes)
    save(fig, path)


def plot_coverage(s: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    groups = [(s.in_main_series, PALETTE[0], "Main series"),
              (~s.in_main_series & s.is_complete, PALETTE[1], "Supplementary"),
              (~s.is_complete, PALETTE[7], "Incomplete (excluded)")]
    for mask, c, lab in groups:
        d = s[mask]
        ax.bar(d.timestamp, d.n_classified, width=1.2, color=c, label=f"{lab}: classified")
        ax.bar(d.timestamp, d.n_unclassifiable, bottom=d.n_classified, width=1.2, color=c, alpha=0.35,
               label=f"{lab}: unclassifiable")
    ax.set_ylabel("Images per sample")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_xlabel("2021 (Utö)")
    ax.legend(frameon=False, ncol=2)
    save(fig, path)


def plot_class_counts(cc: pd.DataFrame, taxa: dict, unclass: str, path: Path) -> None:
    cc = cc[cc["class"] != unclass].sort_values("n_train")
    y = np.arange(len(cc))
    fig, ax = plt.subplots(figsize=(6.0, 8.0))
    ax.barh(y - 0.2, cc.n_train, height=0.4, color=PALETTE[0], label="Train (2016 to 2019)")
    ax.barh(y + 0.2, cc.n_test, height=0.4, color=PALETTE[1], label="Test (2021, classified)")
    ax.set_xscale("log")
    ax.set_yticks(y)
    targets = set(taxa["primary_targets"] + taxa["reported_separately"] + taxa["high_risk"])
    ax.set_yticklabels(cc["class"], fontsize=6.5)
    for lab in ax.get_yticklabels():
        if lab.get_text() in targets:
            lab.set_fontweight("bold")
    ax.set_xlabel("Images per class (log scale)")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="y", visible=False)
    save(fig, path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="max images per class folder (smoke test)")
    args = ap.parse_args()

    cfg, taxa = load_json("datasets.json"), load_json("taxa.json")
    if args.limit:  # partial folders make every sample look incomplete; skip that check in smoke mode
        cfg["main_series_rule"]["min_particle_coverage"] = 0.0
    unclass = cfg["test"]["unclassifiable_folder"]
    out = OUT_DIR / "smoke" if args.limit else OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    apply_style()

    t0 = time.time()
    dirs = dataset_dirs(cfg)
    frames, corrupt = [], []
    for ds in ("train", "test"):
        items = list_class_images(dirs[ds], args.limit)
        print(f"Scanning {ds}: {len(items)} images in {dirs[ds].relative_to(REPO_ROOT)}")
        df, bad = scan_images(items, ds)
        frames.append(df)
        corrupt += bad
    img = pd.concat(frames, ignore_index=True)
    img["legacy_name"] = img["legacy_name"].astype("string")
    img["is_unclassifiable"] = img["class"] == unclass

    test = img[img.dataset == "test"].copy()
    bad_names = int(test["sample_id"].isna().sum())
    assert bad_names == 0, f"{bad_names} test filenames do not match the IFCB pattern"
    test[["iso_year", "iso_week", "particle_index"]] = test[["iso_year", "iso_week", "particle_index"]].astype(int)

    cc = class_count_table(img, cfg["train_counts_from_pdf"])
    s, sample_class_counts = sample_table(test, taxa, unclass, cfg["main_series_rule"])
    wk = weekly_coverage(s, cfg["test"]["year"])
    tc = temporal_check(img, cfg)

    # save tables
    img.drop(columns=["md5"]).to_csv(out / "image_table.csv.gz", index=False, compression="gzip")
    cc.to_csv(out / "class_counts.csv", index=False)
    s.to_csv(out / "samples_2021.csv", index=False)
    sample_class_counts.to_csv(out / "sample_class_counts_2021.csv")
    wk.to_csv(out / "weekly_coverage_2021.csv", index=False)
    pd.DataFrame(corrupt, columns=["dataset", "rel_path", "error"]).to_csv(out / "corrupt_images.csv", index=False)

    main_s = s[s.in_main_series]
    train_classes = set(cc.loc[cc.n_train > 0, "class"])
    test_classes = set(cc.loc[cc.n_test > 0, "class"]) - {unclass}
    summary = {
        "run_time_s": round(time.time() - t0, 1),
        "limit_per_class": args.limit,
        "train": {
            "n_images": int((img.dataset == "train").sum()),
            "n_classes": len(train_classes),
            "n_images_pdf": int(sum(cfg["train_counts_from_pdf"].values())),
            "classes_count_mismatch_vs_pdf": cc.loc[cc.n_train_pdf.notna() & (cc.train_minus_pdf != 0), "class"].tolist(),
        },
        "test": {
            "n_images": int(len(test)),
            "n_classified": int((~test.is_unclassifiable).sum()),
            "n_unclassifiable": int(test.is_unclassifiable.sum()),
            "n_classes_present": len(test_classes),
            "train_classes_absent_in_test": sorted(train_classes - test_classes),
            "test_classes_absent_in_train": sorted(test_classes - train_classes),
            "n_samples": int(len(s)),
            "n_weeks_with_samples": int((wk.n_samples > 0).sum()),
            "weeks_missing": wk.loc[wk.status == "missing", "iso_week"].tolist(),
            "weeks_multiple": wk.loc[wk.status == "multiple", "iso_week"].tolist(),
            "n_main_series_samples": int(len(main_s)),
            "n_supplementary_samples": int((~s.in_main_series & s.is_complete).sum()),
            "incomplete_samples": s.loc[~s.is_complete, ["sample_id", "n_images", "particle_coverage"]]
                                   .round(4).to_dict("records"),
            "min_particle_coverage_complete": round(float(s.loc[s.is_complete, "particle_coverage"].min()), 4),
            "main_series_not_on_tuesday": main_s.loc[main_s.timestamp.dt.weekday != 1, "sample_id"].tolist(),
            "smallest_samples": s.nsmallest(3, "n_images")[["sample_id", "n_images"]].to_dict("records"),
        },
        "temporal_check": tc,
        "n_corrupt_images": len(corrupt),
        "bloom_main_series": {
            k: {"peak_ra": round(float(main_s[f"ra_{k}"].max()), 4),
                "peak_date": str(main_s.loc[main_s[f"ra_{k}"].idxmax(), "timestamp"].date()),
                "n_samples_present": int((main_s[f"n_{k}"] > 0).sum())}
            for k in ["N_fixing_filamentous_total", "Aphanizomenon_flosaquae", "Dolichospermum_total",
                      "Nodularia_spumigena", "Oscillatoriales", "Dinophysis_acuminata"]
        },
    }
    onset = taxa["onset"]
    win = onset["search_window"]
    in_win = main_s.timestamp.dt.strftime("%m-%d").between(win["start_month_day"], win["end_month_day"])
    summary["ground_truth_onset_no_window"] = {
        f"{t:.0%}": str(main_s.loc[main_s[f"ra_{onset['series']}"] >= t, "timestamp"].min().date())
        for t in onset["thresholds"]
    }
    summary["ground_truth_onset"] = {
        f"{t:.0%}": (lambda hit: {"sample_id": hit.iloc[0].sample_id, "date": str(hit.iloc[0].timestamp.date()),
                                  "iso_week": int(hit.iloc[0].iso_week)} if len(hit) else None)(
            main_s[in_win & (main_s[f"ra_{onset['series']}"] >= t)])
        for t in onset["thresholds"]
    }
    nod = "n_Nodularia_spumigena"
    summary["nodularia_images"] = {
        "main_series": int(main_s[nod].sum()),
        "main_series_max_per_sample": int(main_s[nod].max()),
        "supplementary": int(s.loc[~s.in_main_series & s.is_complete, nod].sum()),
        "total_test": int((test["class"] == "Nodularia_spumigena").sum()),
        "train": int(cc.loc[cc["class"] == "Nodularia_spumigena", "n_train"].sum()),
    }
    with open(out / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    with open(out / "run_config.json", "w") as f:
        json.dump({"args": vars(args), "datasets": cfg, "taxa": taxa,
                   "python": sys.version, "pandas": pd.__version__}, f, indent=2)

    plot_bloom_curve(s, taxa, out / "bloom_curve_2021_ground_truth.png")
    plot_coverage(s, out / "sample_coverage_2021.png")
    plot_class_counts(cc, taxa, unclass, out / "class_counts_train_vs_test.png")

    # terminal summary
    tr, te = summary["train"], summary["test"]
    print("\n=== Stage 0 summary ===")
    print(f"Train: {tr['n_images']} images, {tr['n_classes']} classes (PDF total {tr['n_images_pdf']}); "
          f"count mismatches vs PDF: {tr['classes_count_mismatch_vs_pdf'] or 'none'}")
    print(f"Test:  {te['n_images']} images = {te['n_classified']} classified + {te['n_unclassifiable']} "
          f"unclassifiable; {te['n_classes_present']} classes present")
    print(f"       train classes absent in test: {te['train_classes_absent_in_test']}")
    print(f"Samples: {te['n_samples']} in {te['n_weeks_with_samples']} ISO weeks; main series "
          f"{te['n_main_series_samples']}, supplementary {te['n_supplementary_samples']}")
    print(f"       weeks missing: {te['weeks_missing']}; weeks with >1 sample: {te['weeks_multiple']}")
    print(f"       main-series samples not on Tuesday: {te['main_series_not_on_tuesday']}")
    print(f"       incomplete samples (excluded): {te['incomplete_samples']}; "
          f"lowest coverage among complete: {te['min_particle_coverage_complete']}")
    print(f"Temporal: test {tc['test_time_min']} .. {tc['test_time_max']}; train timestamps in names: "
          f"{tc['train_images_with_ifcb_timestamp']}; identical train/test images: "
          f"{tc['train_test_identical_images']}; duplicates within train: {tc['train_duplicate_images_within']}")
    print(f"Corrupt images: {len(corrupt)}")
    print("Ground-truth peaks (main series):")
    for k, v in summary["bloom_main_series"].items():
        print(f"  {k:28s} peak {100 * v['peak_ra']:6.2f}% on {v['peak_date']}, present in "
              f"{v['n_samples_present']}/{len(main_s)} samples")
    print(f"Ground-truth onset ({onset['series']}): " + "; ".join(
        f"{k}: {v['date'] if v else 'never'}" for k, v in summary["ground_truth_onset"].items())
        + f"  (without season window: {summary['ground_truth_onset_no_window']})")
    print(f"Nodularia images: {summary['nodularia_images']}")
    print(f"Outputs: {out.relative_to(REPO_ROOT)}  ({summary['run_time_s']}s)")


if __name__ == "__main__":
    main()
