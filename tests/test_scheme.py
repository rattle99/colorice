"""Tests for ColorScheme and extended color generation.

Purpose: Verify the JSON output has the correct structure and all expected
keys. Without these, a template consuming the JSON could break silently
because a key was renamed or missing.
"""

import json
import os
import tempfile

from colorice.scheme import ColorScheme


def _sample_scheme() -> ColorScheme:
    """A scheme with 16 plausible hex colors."""
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


def test_special_keys():
    """Special dict should have background, foreground, cursor."""
    scheme = _sample_scheme()
    special = scheme.special
    assert "background" in special
    assert "foreground" in special
    assert "cursor" in special
    assert special["background"] == "#191724"
    assert special["foreground"] == "#ecf0f1"


def test_extended_has_ui_keys():
    """Extended colors should include all UI element keys."""
    scheme = _sample_scheme()
    ext = scheme.extended
    ui_keys = [
        "selection_bg", "selection_fg", "accent", "cursor",
        "url", "border", "split", "line_highlight",
    ]
    for key in ui_keys:
        assert key in ext, f"Missing UI key: {key}"
        assert ext[key].startswith("#") and len(ext[key]) == 7, f"Bad hex for {key}: {ext[key]}"


def test_extended_has_syntax_keys():
    """Extended colors should include all syntax highlighting keys."""
    scheme = _sample_scheme()
    ext = scheme.extended
    syntax_keys = [
        "keyword", "function", "type", "string", "number",
        "constant", "comment", "operator", "parameter",
        "property", "tag", "attribute", "decorator",
    ]
    for key in syntax_keys:
        assert key in ext, f"Missing syntax key: {key}"
        assert ext[key].startswith("#") and len(ext[key]) == 7, f"Bad hex for {key}: {ext[key]}"


def test_extended_has_diff_keys():
    """Extended colors should include diff foreground and background variants."""
    scheme = _sample_scheme()
    ext = scheme.extended
    diff_keys = [
        "diff_add", "diff_add_bg", "diff_delete", "diff_delete_bg",
        "diff_change", "diff_change_bg",
    ]
    for key in diff_keys:
        assert key in ext, f"Missing diff key: {key}"


def test_extended_has_diagnostic_keys():
    """Extended colors should include diagnostic keys."""
    scheme = _sample_scheme()
    ext = scheme.extended
    diag_keys = ["error", "warning", "info", "hint", "success"]
    for key in diag_keys:
        assert key in ext, f"Missing diagnostic key: {key}"


def test_extended_colors_are_unique():
    """Syntax colors should not all be the same — they should be derived differently."""
    scheme = _sample_scheme()
    ext = scheme.extended
    syntax_colors = [
        ext["keyword"], ext["function"], ext["type"],
        ext["string"], ext["number"], ext["constant"],
    ]
    unique = set(syntax_colors)
    assert len(unique) >= 4, f"Only {len(unique)} unique syntax colors — too few"


def test_colorice_json_structure():
    """Colorice JSON should have all top-level keys."""
    scheme = _sample_scheme()
    data = scheme.to_colorice_json()
    assert "wallpaper" in data
    assert "mood" in data
    assert "special" in data
    assert "colors" in data
    assert "extended" in data
    assert len(data["colors"]) == 16


def test_pywal_json_structure():
    """Pywal JSON should have the expected keys and no extended section."""
    scheme = _sample_scheme()
    data = scheme.to_pywal_json()
    assert "wallpaper" in data
    assert "alpha" in data
    assert "special" in data
    assert "colors" in data
    assert "extended" not in data
    assert len(data["colors"]) == 16


def test_write_creates_file():
    """Write should create the output file with valid JSON."""
    scheme = _sample_scheme()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "colors.json")
        scheme.write(path)
        assert os.path.isfile(path)
        with open(path) as f:
            data = json.load(f)
        assert data["mood"] == "vibrant"
        assert len(data["colors"]) == 16


def test_write_creates_parent_dirs():
    """Write should create parent directories if they don't exist."""
    scheme = _sample_scheme()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "nested", "deep", "colors.json")
        scheme.write(path)
        assert os.path.isfile(path)
