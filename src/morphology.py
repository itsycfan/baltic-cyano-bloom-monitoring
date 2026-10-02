"""Particle segmentation for a size-based (area) biomass proxy."""
from __future__ import annotations

import numpy as np
from PIL import Image
from scipy import ndimage

MIN_CONTRAST = 8      # grey levels
MAD_FACTOR = 3.0      # robust noise multiplier
MIN_SPECK = 5         # pixels


def foreground_mask(im: Image.Image) -> np.ndarray:
    """Pixels differing from the median border value by more than a robust noise threshold."""
    g = np.asarray(im.convert("L"), dtype=np.float32)
    border = np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]])
    b = np.median(border)
    sigma = 1.4826 * np.median(np.abs(border - b))
    mask = np.abs(g - b) > max(MAD_FACTOR * sigma, MIN_CONTRAST)
    mask = ndimage.binary_fill_holes(mask)
    lab, n = ndimage.label(mask)
    if n:
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        mask = np.isin(lab, 1 + np.flatnonzero(sizes >= MIN_SPECK))
    return mask


def particle_area(im: Image.Image) -> int:
    return int(foreground_mask(im).sum())
