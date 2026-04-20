"""Image color extraction using KMeans clustering in Oklab space."""

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from .oklab import oklab_chroma, oklab_from_lch, oklab_hue, srgb_to_oklab


def load_and_resize(path: str, max_pixels: int = 64_000) -> np.ndarray:
    """Load image, resize to ~max_pixels, return (N, 3) sRGB [0,1] array."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    total = w * h

    if total > max_pixels:
        scale = (max_pixels / total) ** 0.5
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)

    pixels = np.array(img).reshape(-1, 3) / 255.0
    return pixels


def _farthest_first(
    candidates: list[np.ndarray],
    n: int,
    seed_idx: int = 0,
) -> list[np.ndarray]:
    """Greedily pick n most spread-out colors from candidates.

    Starts with the seed, then repeatedly picks the candidate
    whose minimum distance to all already-picked colors is largest.
    """
    picked = [candidates[seed_idx]]
    remaining = [c for i, c in enumerate(candidates) if i != seed_idx]

    while len(picked) < n and remaining:
        best_idx = 0
        best_min_dist = -1.0

        for i, c in enumerate(remaining):
            min_dist = min(float(np.linalg.norm(c - p)) for p in picked)
            if min_dist > best_min_dist:
                best_min_dist = min_dist
                best_idx = i

        picked.append(remaining.pop(best_idx))

    return picked


def extract_dominant_colors(
    pixels: np.ndarray,
    n_colors: int = 8,
    random_state: int = 42,
) -> list[np.ndarray]:
    """Run KMeans in Oklab space with over-clustering + farthest-first selection.

    Over-clusters to 4x the requested count, then selects the most
    perceptually spread-out centroids. This reduces bias toward large
    uniform regions (e.g., sky) and surfaces accent colors.
    """
    oklab_pixels = srgb_to_oklab(pixels)

    n_over = min(n_colors * 4, len(oklab_pixels))
    kmeans = KMeans(
        n_clusters=n_over,
        random_state=random_state,
        n_init=10,
    )
    kmeans.fit(oklab_pixels)

    centroids = list(kmeans.cluster_centers_)

    # Seed farthest-first with the most dominant cluster
    labels = kmeans.labels_
    counts = np.bincount(labels, minlength=n_over)
    seed_idx = int(np.argmax(counts))

    return _farthest_first(centroids, n_colors, seed_idx)


# Hue sectors for ANSI color roles
HUE_SECTORS = {
    "red": [(330, 360), (0, 50)],
    "yellow": [(50, 120)],
    "green": [(120, 175)],
    "cyan": [(175, 240)],
    "blue": [(240, 300)],
    "magenta": [(300, 330)],
}

# Center hue for synthesis when a sector has no extracted color
HUE_CENTERS = {
    "red": 25,
    "yellow": 85,
    "green": 145,
    "cyan": 200,
    "blue": 265,
    "magenta": 315,
}


def _hue_in_sector(hue: float, ranges: list[tuple[float, float]]) -> bool:
    """Check if a hue angle falls within any of the given ranges."""
    return any(lo <= hue < hi for lo, hi in ranges)


def fill_color_gaps(
    colors: list[np.ndarray],
    min_colors: int = 8,
) -> list[np.ndarray]:
    """Ensure all hue sectors have at least one color.

    If a sector is missing, synthesize a color at the sector's center hue
    using the median lightness and chroma from existing colors.
    """
    result = list(colors)

    # Compute median L and C from extracted colors
    lightnesses = [float(c[0]) for c in colors]
    chromas = [oklab_chroma(c) for c in colors]
    median_L = float(np.median(lightnesses))
    median_C = float(np.median(chromas))

    for sector_name, ranges in HUE_SECTORS.items():
        has_color = any(_hue_in_sector(oklab_hue(c), ranges) for c in result)
        if not has_color:
            center_hue = HUE_CENTERS[sector_name]
            synthesized = oklab_from_lch(median_L, median_C, center_hue)
            result.append(synthesized)

    return result
