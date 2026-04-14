"""Tests for color extraction."""

import numpy as np

from colorice.extraction import extract_dominant_colors, fill_color_gaps
from colorice.oklab import oklab_hue, srgb_to_oklab


def test_extract_returns_correct_count():
    """Should return the requested number of colors."""
    # Create fake pixel data: red, green, blue blobs
    pixels = np.vstack([
        np.tile([1.0, 0.0, 0.0], (100, 1)),  # red
        np.tile([0.0, 1.0, 0.0], (100, 1)),  # green
        np.tile([0.0, 0.0, 1.0], (100, 1)),  # blue
    ])
    colors = extract_dominant_colors(pixels, n_colors=3)
    assert len(colors) == 3


def test_extract_sorted_by_dominance():
    """Most dominant cluster should be first."""
    # More red pixels than others
    pixels = np.vstack([
        np.tile([1.0, 0.0, 0.0], (500, 1)),  # red (dominant)
        np.tile([0.0, 1.0, 0.0], (100, 1)),  # green
        np.tile([0.0, 0.0, 1.0], (100, 1)),  # blue
    ])
    colors = extract_dominant_colors(pixels, n_colors=3)
    # First color should be closest to red in Oklab
    red_oklab = srgb_to_oklab(np.array([[1.0, 0.0, 0.0]]))[0]
    dist = np.linalg.norm(colors[0] - red_oklab)
    assert dist < 0.1, "Most dominant color should be red"


def test_fill_color_gaps_adds_missing():
    """Should synthesize colors for missing hue sectors."""
    # Only provide red-ish colors
    red_colors = [
        srgb_to_oklab(np.array([[0.9, 0.1, 0.1]]))[0],
        srgb_to_oklab(np.array([[0.8, 0.2, 0.1]]))[0],
    ]
    filled = fill_color_gaps(red_colors)
    assert len(filled) > len(red_colors), "Should have added synthetic colors"


def test_fill_color_gaps_preserves_existing():
    """Should not remove existing colors."""
    colors = [
        srgb_to_oklab(np.array([[1.0, 0.0, 0.0]]))[0],
        srgb_to_oklab(np.array([[0.0, 1.0, 0.0]]))[0],
    ]
    filled = fill_color_gaps(colors)
    # Original colors should still be present
    for orig in colors:
        assert any(np.allclose(orig, f, atol=0.001) for f in filled)
