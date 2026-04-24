"""WCAG contrast ratio calculation and enforcement."""

import numpy as np

from colorice.oklab import (
    hex_to_srgb,
    oklab_chroma,
    oklab_from_lch,
    oklab_hue,
    oklab_to_hex,
    srgb_to_linear,
)


def relative_luminance(hex_color: str) -> float:
    """WCAG 2.1 relative luminance from sRGB hex.

    L = 0.2126*R + 0.7152*G + 0.0722*B (in linear sRGB).
    """
    linear = srgb_to_linear(hex_to_srgb(hex_color))
    return float(0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2])


def contrast_ratio(hex1: str, hex2: str) -> float:
    """WCAG contrast ratio between two hex colors.

    Returns value in range [1.0, 21.0].
    """
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def enforce_contrast(
    fg_lab: np.ndarray,
    bg_lab: np.ndarray,
    min_ratio: float = 7.0,
) -> np.ndarray:
    """Adjust fg lightness in Oklab until contrast >= min_ratio against bg.

    Preserves hue and chroma, only adjusts L via binary search.
    """
    bg_hex = oklab_to_hex(bg_lab)
    C = oklab_chroma(fg_lab)
    h = oklab_hue(fg_lab)

    # Determine search direction based on bg lightness
    bg_L = float(bg_lab[0])
    if bg_L < 0.5:
        # Dark bg: increase fg lightness
        lo, hi = float(fg_lab[0]), 1.0
    else:
        # Light bg: decrease fg lightness
        lo, hi = 0.0, float(fg_lab[0])

    # Check if current color already meets contrast
    current_hex = oklab_to_hex(fg_lab)
    if contrast_ratio(current_hex, bg_hex) >= min_ratio:
        return fg_lab

    # Binary search on L
    best = fg_lab.copy()
    best_found = False
    for _ in range(32):
        mid = (lo + hi) / 2
        candidate = oklab_from_lch(mid, C, h)
        candidate_hex = oklab_to_hex(candidate)

        ratio = contrast_ratio(candidate_hex, bg_hex)
        if ratio >= min_ratio:
            best = candidate
            best_found = True
            if bg_L < 0.5:
                hi = mid  # try less lightness (closer to original)
            else:
                lo = mid
        else:
            if bg_L < 0.5:
                lo = mid  # need more lightness
            else:
                hi = mid

    # If no color met the target, fall back to max contrast (white or black)
    if not best_found:
        if bg_L < 0.5:
            best = oklab_from_lch(1.0, 0.0, 0.0)  # white
        else:
            best = oklab_from_lch(0.0, 0.0, 0.0)  # black

    return best


def ensure_distinguishable(
    colors: list[np.ndarray],
    min_delta: float = 0.05,
) -> list[np.ndarray]:
    """Nudge colors apart if their Oklab Euclidean distance < min_delta."""
    result = [c.copy() for c in colors]

    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            dist = float(np.linalg.norm(result[i] - result[j]))
            if dist < min_delta and dist > 0:
                # Push apart along the vector between them
                direction = (result[j] - result[i]) / dist
                nudge = (min_delta - dist) / 2
                result[i] = result[i] - direction * nudge
                result[j] = result[j] + direction * nudge

    return result
