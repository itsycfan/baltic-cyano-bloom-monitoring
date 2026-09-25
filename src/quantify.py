"""Sample-level abundance: classify and count, adjusted classify and count, curve metrics."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import nnls


def count_matrix(labels, sample_ids, columns) -> pd.DataFrame:
    """Samples x classes image counts."""
    df = pd.DataFrame({"sample_id": sample_ids, "label": labels})
    c = df.pivot_table(index="sample_id", columns="label", aggfunc="size", fill_value=0)
    return c.reindex(columns=columns, fill_value=0)


def misclassification_matrix(y_true_idx, y_pred_idx, n_classes: int) -> np.ndarray:
    """M[i, j] = P(pred = i | true = j), columns sum to 1 (identity column if class j is absent)."""
    M = np.zeros((n_classes, n_classes))
    np.add.at(M, (y_pred_idx, y_true_idx), 1)
    col = M.sum(axis=0)
    M[:, col == 0] = np.eye(n_classes)[:, col == 0]
    return M / M.sum(axis=0, keepdims=True)


def acc_proportions(p_cc: np.ndarray, M: np.ndarray, sum_weight: float = 100.0) -> np.ndarray:
    """Solve min ||M q - p||^2 s.t. q >= 0, sum q = 1, per row of p_cc (samples x classes)."""
    n = M.shape[0]
    A = np.vstack([M, sum_weight * np.ones((1, n))])
    out = np.zeros_like(p_cc, dtype=float)
    for s, p in enumerate(p_cc):
        q, _ = nnls(A, np.concatenate([p, [sum_weight]]))
        out[s] = q / q.sum() if q.sum() > 0 else q
    return out


def series_from_fractions(frac: pd.DataFrame, groups: dict) -> pd.DataFrame:
    """Aggregate class fractions (samples x classes) into named series."""
    return pd.DataFrame({name: frac.reindex(columns=members, fill_value=0).sum(axis=1)
                         for name, members in groups.items()})


def onset(values: np.ndarray, times: pd.Series, threshold: float, window: tuple) -> pd.Timestamp | None:
    md = times.dt.strftime("%m-%d")
    ok = (md >= window[0]) & (md <= window[1]) & (values >= threshold)
    return times[ok].min() if ok.any() else None


def curve_metrics(true: np.ndarray, pred: np.ndarray, times: pd.Series, thresholds, window,
                  n_boot: int = 2000, seed: int = 0) -> dict:
    """MAE (percentage points) with bootstrap CI, correlations, peak offset, onset agreement."""
    from scipy.stats import pearsonr, spearmanr

    err = np.abs(pred - true) * 100
    rng = np.random.default_rng(seed)
    boot = err[rng.integers(0, len(err), (n_boot, len(err)))].mean(axis=1)
    times = times.reset_index(drop=True)
    const = np.std(pred) == 0 or np.std(true) == 0
    out = {
        "mae_pp": float(err.mean()),
        "mae_ci_low": float(np.percentile(boot, 2.5)),
        "mae_ci_high": float(np.percentile(boot, 97.5)),
        "bias_pp": float(((pred - true) * 100).mean()),
        "pearson_r": float("nan") if const else float(pearsonr(true, pred)[0]),
        "spearman_r": float("nan") if const else float(spearmanr(true, pred)[0]),
        "peak_offset_weeks": round((times[int(np.argmax(pred))] - times[int(np.argmax(true))]).days / 7, 1),
    }
    for t in thresholds:
        ot, op = onset(true, times, t, window), onset(pred, times, t, window)
        key = f"onset_{int(t * 100)}pct"
        if ot is None and op is None:
            out[key] = "both_none"
        elif ot is None:
            out[key] = "false_onset"
        elif op is None:
            out[key] = "missed"
        else:
            out[key] = round((op - ot).days / 7, 1)
    return out
