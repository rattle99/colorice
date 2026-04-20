"""Tests for color extraction."""

import os
import tempfile

import numpy as np
from PIL import Image

from colorice.extraction import (
    extract_dominant_colors,
    extract_dominant_colors_segmented,
    fill_color_gaps,
)
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


def _make_test_image(path: str, regions: list[tuple[tuple[int,int,int], int]]) -> None:
    """Create a test image with colored blocks stacked vertically."""
    width = 100
    total_height = sum(h for _, h in regions)
    img = Image.new("RGB", (width, total_height))
    y = 0
    for color, height in regions:
        for row in range(y, y + height):
            for col in range(width):
                img.putpixel((col, row), color)
        y += height
    img.save(path)


def test_segmented_returns_correct_count():
    """Segmented extraction should return the requested number of colors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.png")
        _make_test_image(path, [
            ((255, 0, 0), 50),    # red
            ((0, 255, 0), 50),    # green
            ((0, 0, 255), 50),    # blue
            ((255, 255, 0), 50),  # yellow
        ])
        colors = extract_dominant_colors_segmented(path, n_colors=4)
        assert len(colors) == 4


def test_segmented_finds_small_regions():
    """Segmented extraction should surface colors from small regions.

    A tiny accent region that KMeans would ignore should get equal weight
    when each segment contributes independently.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.png")
        # 90% blue sky, 10% red subject
        _make_test_image(path, [
            ((30, 60, 150), 180),   # large blue region
            ((220, 40, 30), 20),    # small red region
        ])
        colors = extract_dominant_colors_segmented(path, n_colors=4)
        # Should have at least 2 distinct colors (not all blue)
        hexes = set()
        from colorice.oklab import oklab_to_hex
        for c in colors:
            hexes.add(oklab_to_hex(c))
        assert len(hexes) >= 2, f"Expected diverse colors, got {hexes}"


def test_segmented_all_colors_valid_oklab():
    """Segmented colors should be valid Oklab values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.png")
        _make_test_image(path, [
            ((200, 100, 50), 60),
            ((50, 100, 200), 60),
            ((100, 200, 50), 60),
        ])
        colors = extract_dominant_colors_segmented(path, n_colors=3)
        for c in colors:
            assert np.all(np.isfinite(c)), f"Non-finite color: {c}"
            assert 0.0 <= float(c[0]) <= 1.0, f"L out of range: {c[0]}"
