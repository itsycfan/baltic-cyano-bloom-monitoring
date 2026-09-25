"""Evidence layer: cosine kNN retrieval on the fit split."""
from __future__ import annotations

import numpy as np


def knn_signals(ref_X: np.ndarray, ref_y: np.ndarray, query_X: np.ndarray, pred_labels: np.ndarray,
                k: int = 7, chunk: int = 512) -> dict:
    """Neighbour label agreement with the predicted label and nearest-neighbour cosine distance.

    Inputs must be L2-normalised row-wise.
    """
    agree = np.zeros(len(query_X), dtype=np.float32)
    nn_dist = np.zeros(len(query_X), dtype=np.float32)
    ref_T = np.ascontiguousarray(ref_X.T)
    for s in range(0, len(query_X), chunk):
        sim = query_X[s:s + chunk] @ ref_T
        top = np.argpartition(-sim, k, axis=1)[:, :k]
        top_sim = np.take_along_axis(sim, top, axis=1)
        agree[s:s + chunk] = (ref_y[top] == pred_labels[s:s + chunk, None]).mean(axis=1)
        nn_dist[s:s + chunk] = 1.0 - top_sim.max(axis=1)
    return {"neighbour_agreement": agree, "nn_distance": nn_dist}
