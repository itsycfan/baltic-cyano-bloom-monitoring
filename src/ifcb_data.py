"""Shared helpers for locating and parsing the SYKE IFCB image datasets."""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = REPO_ROOT / "config"

# D20210601T120001_IFCB114_01623.png -> start time, instrument, particle index
IFCB_NAME_RE = re.compile(r"^D(\d{8}T\d{6})_(IFCB\d+)_(\d+)\.png$")
# Training images were renamed to <legacy class name>_<index>.png
LEGACY_NAME_RE = re.compile(r"^(.*)_(\d+)\.png$")


def load_json(name: str) -> dict:
    with open(CONFIG_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def dataset_dirs(cfg: Optional[dict] = None) -> dict:
    """Return absolute image roots for the train and test datasets."""
    cfg = cfg or load_json("datasets.json")
    root = REPO_ROOT / cfg["data_root"]
    return {"train": root / cfg["train"]["image_root"], "test": root / cfg["test"]["image_root"]}


def parse_ifcb_filename(name: str) -> Optional[dict]:
    """Parse an IFCB filename into sample ID, timestamp, instrument and particle index."""
    m = IFCB_NAME_RE.match(name)
    if m is None:
        return None
    stamp, instrument, particle = m.groups()
    t = datetime.strptime(stamp, "%Y%m%dT%H%M%S")
    iso = t.isocalendar()
    return {
        "sample_id": f"D{stamp}_{instrument}",
        "timestamp": t,
        "instrument": instrument,
        "particle_index": int(particle),
        "iso_year": iso[0],
        "iso_week": iso[1],
    }


def parse_legacy_filename(name: str) -> Optional[dict]:
    """Parse a renamed training filename into its legacy class name and index."""
    m = LEGACY_NAME_RE.match(name)
    if m is None:
        return None
    return {"legacy_name": m.group(1), "legacy_index": int(m.group(2))}


def list_class_images(image_root: Path, limit_per_class: Optional[int] = None) -> list:
    """List (class_folder, path) pairs for every PNG, sorted for determinism."""
    items = []
    for class_dir in sorted(p for p in image_root.iterdir() if p.is_dir()):
        files = sorted(class_dir.glob("*.png"))
        if limit_per_class is not None:
            files = files[:limit_per_class]
        items.extend((class_dir.name, f) for f in files)
    return items


def iso_week_reference(iso_year: int, iso_week: int, weekday: int, hour: int) -> datetime:
    """Datetime of a given weekday (Mon=0) and hour within an ISO week."""
    monday = datetime.fromisocalendar(int(iso_year), int(iso_week), 1)
    return monday + timedelta(days=weekday, hours=hour)


def select_main_series(samples: pd.DataFrame, weekday: int, hour: int) -> pd.Series:
    """Flag one sample per ISO week: the one closest to the regular weekly slot.

    The rule only looks at sample timestamps, never at sample content.
    """
    ref = samples.apply(lambda r: iso_week_reference(r.iso_year, r.iso_week, weekday, hour), axis=1)
    dist = (samples["timestamp"] - ref).abs()
    order = samples.assign(_dist=dist).sort_values(["iso_year", "iso_week", "_dist", "timestamp"])
    chosen = order.groupby(["iso_year", "iso_week"]).head(1).index
    return samples.index.isin(chosen)
