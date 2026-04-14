"""Tests for Oklab color space conversions."""

import numpy as np
import pytest

from colorice.oklab import (
    gamut_clamp,
    hex_to_oklab,
    hex_to_srgb,
    oklab_chroma,
    oklab_from_lch,
    oklab_hue,
    oklab_lightness,
    oklab_to_hex,
    srgb_to_hex,
    srgb_to_oklab,
    oklab_to_srgb,
)


def test_hex_roundtrip():
    """Hex -> Oklab -> Hex should be identity (within rounding)."""
    colors = ["#ff0000", "#00ff00", "#0000ff", "#ffffff", "#000000", "#8897f4"]
    for hex_color in colors:
        lab = hex_to_oklab(hex_color)
        result = oklab_to_hex(lab)
        # Allow 1/255 rounding error per channel
        orig = hex_to_srgb(hex_color)
        back = hex_to_srgb(result)
        assert np.allclose(orig, back, atol=2 / 255), f"{hex_color} -> {result}"


def test_black_white_lightness():
    """Black should have L~0, white should have L~1."""
    black = hex_to_oklab("#000000")
    white = hex_to_oklab("#ffffff")
    assert oklab_lightness(black) < 0.01
    assert oklab_lightness(white) > 0.99


def test_chroma_gray_is_zero():
    """Gray colors should have near-zero chroma."""
    gray = hex_to_oklab("#808080")
    assert oklab_chroma(gray) < 0.01


def test_chroma_saturated_is_high():
    """Saturated colors should have high chroma."""
    red = hex_to_oklab("#ff0000")
    assert oklab_chroma(red) > 0.1


def test_hue_red():
    """Red should have hue near 30 degrees in Oklab."""
    red = hex_to_oklab("#ff0000")
    h = oklab_hue(red)
    assert 20 < h < 40, f"Red hue was {h}"


def test_hue_blue():
    """Blue should have hue around 265 degrees in Oklab."""
    blue = hex_to_oklab("#0000ff")
    h = oklab_hue(blue)
    assert 250 < h < 280, f"Blue hue was {h}"


def test_oklab_from_lch_roundtrip():
    """LCH construction should preserve L, C, H."""
    lab = oklab_from_lch(0.7, 0.15, 120.0)
    assert abs(oklab_lightness(lab) - 0.7) < 0.001
    assert abs(oklab_chroma(lab) - 0.15) < 0.001
    assert abs(oklab_hue(lab) - 120.0) < 0.1


def test_gamut_clamp_preserves_in_gamut():
    """Colors already in gamut should not change."""
    lab = hex_to_oklab("#884488")
    clamped = gamut_clamp(lab)
    assert np.allclose(lab, clamped, atol=0.01)


def test_gamut_clamp_reduces_chroma():
    """Out-of-gamut colors should have reduced chroma."""
    # Create a very saturated color that's likely out of gamut
    extreme = oklab_from_lch(0.5, 0.4, 120.0)
    clamped = gamut_clamp(extreme)
    assert oklab_chroma(clamped) <= oklab_chroma(extreme)


def test_srgb_batch_conversion():
    """Batch conversion should work for multiple colors."""
    srgb = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ])
    oklab = srgb_to_oklab(srgb)
    assert oklab.shape == (3, 3)
    back = oklab_to_srgb(oklab)
    assert np.allclose(srgb, back, atol=0.01)
