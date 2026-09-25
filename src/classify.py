"""Decision layer: features loading, logistic regression, and image-level metrics."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURE_ROOT = REPO_ROOT / "features"


def load_features(models: list, dataset: str) -> tuple[np.ndarray, pd.DataFrame]:
    """L2-normalise each model's features and concatenate them (a single model is a special case).

    Rows are aligned through the index files written by extract_features.py.
    """
    blocks, index = [], None
    for m in models:
        X = np.load(FEATURE_ROOT / m / f"{dataset}.npy").astype(np.float32)
        X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
        idx = pd.read_csv(FEATURE_ROOT / m / f"{dataset}_index.csv")
        if index is None:
            index = idx
        elif not index.rel_path.equals(idx.rel_path):
            raise ValueError(f"row order of {m} differs from {models[0]}")
        blocks.append(X)
    return np.hstack(blocks), index


class LRClassifier:
    """Standardise, then multinomial logistic regression (lbfgs, L2)."""

    def __init__(self, C: float = 1.0, class_weight=None, max_iter: int = 2000, seed: int = 0):
        self.scaler = StandardScaler()
        self.lr = LogisticRegression(C=C, class_weight=class_weight, max_iter=max_iter, random_state=seed)

    def fit(self, X, y):
        self.lr.fit(self.scaler.fit_transform(X), y)
        return self

    @property
    def classes_(self):
        return self.lr.classes_

    def decision_function(self, X):
        return self.lr.decision_function(self.scaler.transform(X))

    def predict_proba(self, X):
        return self.lr.predict_proba(self.scaler.transform(X))


def expected_calibration_error(conf: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float:
    """Top-label ECE with equal-width confidence bins."""
    edges = np.linspace(0, 1, n_bins + 1)
    bins = np.clip(np.digitize(conf, edges[1:-1]), 0, n_bins - 1)
    ece = 0.0
    for b in range(n_bins):
        m = bins == b
        if m.any():
            ece += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return float(ece)


def image_metrics(y_true, proba: np.ndarray, classes: np.ndarray, target_classes: list) -> tuple[dict, pd.DataFrame]:
    """Macro F1 over the classes present in y_true, target-class P/R/F1, accuracy and ECE."""
    pred = classes[proba.argmax(1)]
    conf = proba.max(1)
    correct = pred == np.asarray(y_true)
    labels = sorted(set(y_true))
    p, r, f, s = precision_recall_fscore_support(y_true, pred, labels=labels, zero_division=0)
    per_class = pd.DataFrame({"class": labels, "precision": p, "recall": r, "f1": f, "support": s,
                              "n_predicted": [int((pred == c).sum()) for c in labels]})
    summary = {
        "accuracy": float(correct.mean()),
        "macro_f1": float(f1_score(y_true, pred, labels=labels, average="macro", zero_division=0)),
        "ece": expected_calibration_error(conf, correct),
        "mean_confidence": float(conf.mean()),
    }
    for c in target_classes:
        row = per_class[per_class["class"] == c]
        summary[f"f1_{c}"] = float(row.f1.iloc[0]) if len(row) else None
    return summary, per_class


def softmax(logits: np.ndarray, T: float = 1.0) -> np.ndarray:
    z = logits / T
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_temperature(logits: np.ndarray, y_idx: np.ndarray) -> float:
    """Temperature minimising the negative log-likelihood on held-out (validation) logits."""
    from scipy.optimize import minimize_scalar

    def nll(log_t):
        p = softmax(logits, float(np.exp(log_t)))
        return -np.mean(np.log(p[np.arange(len(y_idx)), y_idx] + 1e-12))

    res = minimize_scalar(nll, bounds=(np.log(0.05), np.log(20.0)), method="bounded")
    return float(np.exp(res.x))
