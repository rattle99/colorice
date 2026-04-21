"""Tests for template variable resolution."""

from colorice.oklab import hex_to_oklab, oklab_chroma, oklab_lightness
from colorice.scheme import ColorScheme
from colorice.templates.variables import (
    _compute_manipulation,
    _format_modifiers,
    build_variables,
)


def _sample_scheme() -> ColorScheme:
    return ColorScheme(
        wallpaper="/tmp/test.jpg",
        mood="vibrant",
        colors=[
            "#191724", "#ff4971", "#2ecc71", "#f1c40f",
            "#3498db", "#9b59b6", "#1abc9c", "#ecf0f1",
            "#34495e", "#e74c3c", "#27ae60", "#f39c12",
            "#2980b9", "#8e44ad", "#16a085", "#ffffff",
        ],
    )


def test_base_variables_present():
    """Should have all 16 colors, special names, wallpaper, alpha."""
    scheme = _sample_scheme()
    variables = build_variables(scheme, "")
    for i in range(16):
        assert f"color{i}" in variables
    assert variables["background"] == "#191724"
    assert variables["foreground"] == "#ecf0f1"
    assert variables["cursor"] == "#3498db"
    assert variables["wallpaper"] == "/tmp/test.jpg"
    assert variables["alpha"] == "100"


def test_strip_modifier():
    """strip should remove the # prefix."""
    mods = _format_modifiers("color0", "#1a2b3c")
    assert mods["color0.strip"] == "1a2b3c"


def test_rgb_modifier():
    mods = _format_modifiers("color0", "#ff0000")
    assert mods["color0.rgb"] == "rgb(255,0,0)"


def test_rgba_modifier():
    mods = _format_modifiers("color0", "#ff0000")
    assert mods["color0.rgba"] == "rgba(255,0,0,1.0)"


def test_red_green_blue_modifiers():
    mods = _format_modifiers("color0", "#1a2b3c")
    assert mods["color0.red"] == "26"
    assert mods["color0.green"] == "43"
    assert mods["color0.blue"] == "60"


def test_lighten_produces_lighter():
    original = "#3498db"
    lightened = _compute_manipulation(original, "lighten", 20)
    orig_L = oklab_lightness(hex_to_oklab(original))
    new_L = oklab_lightness(hex_to_oklab(lightened))
    assert new_L > orig_L


def test_darken_produces_darker():
    original = "#3498db"
    darkened = _compute_manipulation(original, "darken", 20)
    orig_L = oklab_lightness(hex_to_oklab(original))
    new_L = oklab_lightness(hex_to_oklab(darkened))
    assert new_L < orig_L


def test_saturate_increases_chroma():
    original = "#808080"  # gray, low chroma
    saturated = _compute_manipulation(original, "saturate", 10)
    orig_C = oklab_chroma(hex_to_oklab(original))
    new_C = oklab_chroma(hex_to_oklab(saturated))
    assert new_C > orig_C


def test_desaturate_decreases_chroma():
    original = "#ff0000"  # vivid red, high chroma
    desaturated = _compute_manipulation(original, "desaturate", 10)
    orig_C = oklab_chroma(hex_to_oklab(original))
    new_C = oklab_chroma(hex_to_oklab(desaturated))
    assert new_C < orig_C


def test_extreme_manipulation_produces_valid_hex():
    """Extreme values should still produce valid 7-char hex."""
    result = _compute_manipulation("#000000", "lighten", 100)
    assert result.startswith("#") and len(result) == 7

    result = _compute_manipulation("#ffffff", "darken", 100)
    assert result.startswith("#") and len(result) == 7


def test_manipulation_resolved_from_template():
    """Manipulations should only be computed when found in template content."""
    scheme = _sample_scheme()
    content = "bg: {color0.lighten_20}"
    variables = build_variables(scheme, content)
    assert "color0.lighten_20" in variables
    # Manipulation not in template should not be computed
    assert "color0.darken_30" not in variables


def test_composition_manipulation_plus_strip():
    """Should resolve {color0.lighten_20.strip} correctly."""
    scheme = _sample_scheme()
    content = "val: {color0.lighten_20.strip}"
    variables = build_variables(scheme, content)
    assert "color0.lighten_20.strip" in variables
    assert not variables["color0.lighten_20.strip"].startswith("#")
