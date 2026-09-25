"""Frozen feature extractors and the shared image preprocessing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import torch
from PIL import Image, ImageOps

IMAGENET_MEAN, IMAGENET_STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
CLIP_MEAN, CLIP_STD = (0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)
INPUT_SIZE = 224


def get_device() -> torch.device:
    return torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")


def pad_to_square(im: Image.Image) -> Image.Image:
    """Pad to a square with the median border intensity, keeping the whole particle.

    IFCB particles are often long filaments (median aspect ratio 7.3 for Aphanizomenon),
    so centre cropping would discard most of the object.
    """
    g = np.asarray(im.convert("L"))
    border = np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]])
    fill = int(np.median(border))
    w, h = im.size
    side = max(w, h)
    dx, dy = side - w, side - h
    return ImageOps.expand(im.convert("L"), (dx // 2, dy // 2, dx - dx // 2, dy - dy // 2), fill=fill)


class Preprocess:
    """Pad to square, resize, replicate grey to RGB, normalise with model statistics."""

    def __init__(self, mean, std, size: int = INPUT_SIZE):
        self.mean = torch.tensor(mean).view(3, 1, 1)
        self.std = torch.tensor(std).view(3, 1, 1)
        self.size = size

    def __call__(self, im: Image.Image) -> torch.Tensor:
        im = pad_to_square(im).resize((self.size, self.size), Image.BICUBIC)
        x = torch.from_numpy(np.asarray(im, dtype=np.float32) / 255.0).unsqueeze(0).expand(3, -1, -1)
        return (x - self.mean) / self.std


@dataclass
class Extractor:
    name: str
    model: torch.nn.Module
    forward: Callable
    preprocess: Preprocess
    dim: int


def load_extractor(name: str, device: torch.device) -> Extractor:
    """Load a frozen backbone. Output is the pooled/CLS (or CLIP image) embedding."""
    if name == "resnet18":
        import torchvision
        m = torchvision.models.resnet18(weights="IMAGENET1K_V1")
        m.fc = torch.nn.Identity()
        ext = Extractor(name, m, lambda m, x: m(x), Preprocess(IMAGENET_MEAN, IMAGENET_STD), 512)
    elif name == "dinov2_vitb14":
        m = torch.hub.load("facebookresearch/dinov2", "dinov2_vitb14", verbose=False)
        ext = Extractor(name, m, lambda m, x: m(x), Preprocess(IMAGENET_MEAN, IMAGENET_STD), 768)
    elif name == "clip_vitb16":
        import open_clip
        m, _, _ = open_clip.create_model_and_transforms("ViT-B-16", pretrained="openai")
        ext = Extractor(name, m, lambda m, x: m.encode_image(x), Preprocess(CLIP_MEAN, CLIP_STD), 512)
    elif name == "bioclip2":
        import open_clip
        m, _, _ = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip-2")
        ext = Extractor(name, m, lambda m, x: m.encode_image(x), Preprocess(CLIP_MEAN, CLIP_STD), 768)
    else:
        raise ValueError(f"unknown extractor {name}")
    ext.model = ext.model.eval().to(device)
    for p in ext.model.parameters():
        p.requires_grad_(False)
    return ext


MODELS = ["resnet18", "dinov2_vitb14", "clip_vitb16", "bioclip2"]
