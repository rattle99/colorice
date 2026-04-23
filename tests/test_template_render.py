"""Tests for template rendering."""

from colorice.templates.pywal_compat import render


def test_basic_substitution(sample_scheme):
    result = render(sample_scheme, "bg={color0}")
    assert result == "bg=#191724"


def test_special_names(sample_scheme):
    result = render(sample_scheme, "{background} {foreground} {cursor}")
    assert result == "#191724 #ecf0f1 #3498db"


def test_escaped_braces_become_literal(sample_scheme):
    """{{ and }} should become { and } in output."""
    result = render(sample_scheme, '{{"key": "{color0}"}}')
    assert result == '{"key": "#191724"}'


def test_unknown_placeholder_unchanged(sample_scheme):
    result = render(sample_scheme, "{unknown_var}")
    assert result == "{unknown_var}"


def test_color10_not_clobbered_by_color1(sample_scheme):
    """Regex approach should match full placeholder names."""
    result = render(sample_scheme, "{color1} {color10}")
    assert result == "#ff4971 #27ae60"


def test_modifier_in_template(sample_scheme):
    result = render(sample_scheme, "{color0.strip}")
    assert result == "191724"


def test_rgb_in_template(sample_scheme):
    result = render(sample_scheme, "{color1.rgb}")
    assert result == "rgb(255,73,113)"


def test_manipulation_in_template(sample_scheme):
    result = render(sample_scheme, "{color0.lighten_20}")
    assert result.startswith("#") and len(result) == 7
    # Should be different from original (lighter)
    assert result != "#191724"


def test_wallpaper_substitution(sample_scheme):
    result = render(sample_scheme, "wallpaper={wallpaper}")
    assert result == "wallpaper=/tmp/test.jpg"


def test_mixed_content(sample_scheme):
    """Template with regular text, placeholders, and escaped braces."""
    template = """config {{
  bg = "{color0}"
  fg = "{foreground.strip}"
  accent = "{color4.lighten_20}"
}}"""
    result = render(sample_scheme, template)
    assert result.startswith("config {")
    assert result.endswith("}")
    assert '"#191724"' in result
    assert "ecf0f1" in result  # foreground.strip without #
