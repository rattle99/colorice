"""Tests for ANSI palette assignment."""

import numpy as np

from colorice.contrast import contrast_ratio
from colorice.extraction import extract_dominant_colors, fill_color_gaps
from colorice.palette import assign_ansi_roles
from colorice.oklab import srgb_to_oklab


def _make_diverse_colors() -> list[np.ndarray]:
    """Create a diverse set of test colors."""
    pixels = np.vstack([
        np.tile([0.9, 0.1, 0.1], (100, 1)),   # red
        np.tile([0.1, 0.8, 0.1], (100, 1)),    # green
        np.tile([0.9, 0.9, 0.1], (100, 1)),    # yellow
        np.tile([0.1, 0.2, 0.9], (100, 1)),    # blue
        np.tile([0.8, 0.1, 0.8], (100, 1)),    # magenta
        np.tile([0.1, 0.8, 0.8], (100, 1)),    # cyan
        np.tile([0.05, 0.05, 0.05], (100, 1)), # dark
        np.tile([0.95, 0.95, 0.95], (100, 1)), # light
    ])
    dominant = extract_dominant_colors(pixels, n_colors=8)
    return fill_color_gaps(dominant)


def test_assigns_16_colors():
    """Should return exactly 16 hex colors."""
    colors = _make_diverse_colors()
    palette = assign_ansi_roles(colors)
    assert len(palette) == 16
    assert all(c.startswith("#") and len(c) == 7 for c in palette)


def test_foreground_contrast():
    """Foreground (color7) should have good contrast against background (color0)."""
    colors = _make_diverse_colors()
    palette = assign_ansi_roles(colors, min_contrast=7.0)
    ratio = contrast_ratio(palette[7], palette[0])
    assert ratio >= 6.5, f"fg/bg contrast was {ratio}"


def test_colors_are_distinguishable():
    """Colors 1-6 should be visually distinct from each other."""
    colors = _make_diverse_colors()
    palette = assign_ansi_roles(colors)
    # Just check they're not all the same
    unique = set(palette[1:7])
    assert len(unique) >= 4, f"Only {len(unique)} unique colors in slots 1-6"


def test_light_theme():
    """Light theme should have light background and dark foreground."""
    colors = _make_diverse_colors()
    palette = assign_ansi_roles(colors, light=True)
    # Background should be lighter than foreground
    from colorice.contrast import relative_luminance
    bg_lum = relative_luminance(palette[0])
    fg_lum = relative_luminance(palette[7])
    assert bg_lum > fg_lum, "Light theme bg should be lighter than fg"


def test_monotone_image():
    """Should handle an image with very little color variety."""
    # All similar dark blue
    pixels = np.random.uniform(0.0, 0.15, (500, 3))
    pixels[:, 2] += 0.2  # slight blue tint
    dominant = extract_dominant_colors(pixels, n_colors=5)
    filled = fill_color_gaps(dominant)
    palette = assign_ansi_roles(filled)
    assert len(palette) == 16
