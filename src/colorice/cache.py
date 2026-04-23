"""Extraction cache — skip re-extraction for the same image + params."""

import hashlib
import json
import os

import numpy as np

from .paths import cache_dir


def _cache_key(image_bytes: bytes, **params: object) -> str:
    """Compute cache key from image file bytes and extraction params."""
    h = hashlib.sha256(image_bytes)
    # Sort params for deterministic key
    for k in sorted(params):
        h.update(f"{k}={params[k]}".encode())
    return h.hexdigest()


def _cache_path(key: str) -> str:
    return os.path.join(cache_dir(), f"{key}.json")


def load_cached(key: str) -> list[np.ndarray] | None:
    """Load cached extraction result, or None on miss."""
    path = _cache_path(key)
    if not os.path.isfile(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return [np.array(c) for c in data]
    except (json.JSONDecodeError, ValueError, KeyError):
        return None


def save_cache(key: str, colors: list[np.ndarray]) -> None:
    """Save extraction result to cache."""
    path = _cache_path(key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = [c.tolist() for c in colors]
    with open(path, "w") as f:
        json.dump(data, f)


def get_cache_key_for_extraction(
    image_path: str,
    n_colors: int,
    segment: bool,
    random_state: int = 42,
    max_pixels: int = 64_000,
    scale: int = 100,
    min_size: int = 50,
) -> tuple[str, bytes]:
    """Read image file and compute cache key.

    Returns (cache_key, image_bytes) so the caller can pass bytes
    to extraction without re-reading the file.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    key = _cache_key(
        image_bytes,
        n_colors=n_colors,
        segment=segment,
        random_state=random_state,
        max_pixels=max_pixels,
        scale=scale,
        min_size=min_size,
    )
    return key, image_bytes
