"""Tests for WCAG contrast ratio calculation."""

from colorice.contrast import contrast_ratio, enforce_contrast, relative_luminance
from colorice.oklab import hex_to_oklab, oklab_to_hex


def test_black_white_contrast():
    """Black vs white should be 21:1."""
    ratio = contrast_ratio("#000000", "#ffffff")
    assert abs(ratio - 21.0) < 0.1


def test_same_color_contrast():
    """Same color should have 1:1 contrast."""
    ratio = contrast_ratio("#888888", "#888888")
    assert abs(ratio - 1.0) < 0.01


def test_contrast_is_symmetric():
    """Contrast ratio should be the same regardless of order."""
    r1 = contrast_ratio("#ff0000", "#000000")
    r2 = contrast_ratio("#000000", "#ff0000")
    assert abs(r1 - r2) < 0.01


def test_relative_luminance_black():
    assert relative_luminance("#000000") < 0.01


def test_relative_luminance_white():
    assert relative_luminance("#ffffff") > 0.99


def test_enforce_contrast_meets_target():
    """Enforce contrast should produce a color meeting the target ratio."""
    bg = hex_to_oklab("#191724")
    fg = hex_to_oklab("#444444")  # low contrast against dark bg

    adjusted = enforce_contrast(fg, bg, min_ratio=7.0)
    adjusted_hex = oklab_to_hex(adjusted)
    bg_hex = oklab_to_hex(bg)

    ratio = contrast_ratio(adjusted_hex, bg_hex)
    assert ratio >= 6.9, f"Contrast ratio was {ratio}"


def test_enforce_contrast_preserves_good_contrast():
    """Colors already meeting contrast should not change much."""
    bg = hex_to_oklab("#000000")
    fg = hex_to_oklab("#ffffff")

    adjusted = enforce_contrast(fg, bg, min_ratio=7.0)
    adjusted_hex = oklab_to_hex(adjusted)
    assert adjusted_hex in ("#ffffff", "#fefefe", "#fdfdfd")  # minimal change
