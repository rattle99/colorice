"""Tests for ColorScheme and JSON serialization.

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


def test_json_structure():
    """JSON output should have all expected keys."""
    scheme = _sample_scheme()
    data = scheme.to_json()
    assert "wallpaper" in data
    assert "mood" in data
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
