"""Tests for template rendering."""

from colorice.scheme import ColorScheme
from colorice.templates.pywal_compat import render


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


def test_basic_substitution():
    scheme = _sample_scheme()
    result = render(scheme, "bg={color0}")
    assert result == "bg=#191724"


def test_special_names():
    scheme = _sample_scheme()
    result = render(scheme, "{background} {foreground} {cursor}")
    assert result == "#191724 #ecf0f1 #3498db"


def test_escaped_braces_become_literal():
    """{{ and }} should become { and } in output."""
    scheme = _sample_scheme()
    result = render(scheme, '{{"key": "{color0}"}}')
    assert result == '{"key": "#191724"}'


def test_unknown_placeholder_unchanged():
    scheme = _sample_scheme()
    result = render(scheme, "{unknown_var}")
    assert result == "{unknown_var}"


def test_color10_not_clobbered_by_color1():
    """Regex approach should match full placeholder names."""
    scheme = _sample_scheme()
    result = render(scheme, "{color1} {color10}")
    assert result == "#ff4971 #27ae60"


def test_modifier_in_template():
    scheme = _sample_scheme()
    result = render(scheme, "{color0.strip}")
    assert result == "191724"


def test_rgb_in_template():
    scheme = _sample_scheme()
    result = render(scheme, "{color1.rgb}")
    assert result == "rgb(255,73,113)"


def test_manipulation_in_template():
    scheme = _sample_scheme()
    result = render(scheme, "{color0.lighten_20}")
    assert result.startswith("#") and len(result) == 7
    # Should be different from original (lighter)
    assert result != "#191724"


def test_wallpaper_substitution():
    scheme = _sample_scheme()
    result = render(scheme, "wallpaper={wallpaper}")
    assert result == "wallpaper=/tmp/test.jpg"


def test_mixed_content():
    """Template with regular text, placeholders, and escaped braces."""
    scheme = _sample_scheme()
    template = """config {{
  bg = "{color0}"
  fg = "{foreground.strip}"
  accent = "{color4.lighten_20}"
}}"""
    result = render(scheme, template)
    assert result.startswith("config {")
    assert result.endswith("}")
    assert '"#191724"' in result
    assert "ecf0f1" in result  # foreground.strip without #
