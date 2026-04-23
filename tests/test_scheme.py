"""Tests for ColorScheme and JSON serialization.

Purpose: Verify the JSON output has the correct structure and all expected
keys. Without these, a template consuming the JSON could break silently
because a key was renamed or missing.
"""

import json
import os
import tempfile


def test_special_keys(sample_scheme):
    """Special dict should have background, foreground, cursor."""
    special = sample_scheme.special
    assert "background" in special
    assert "foreground" in special
    assert "cursor" in special
    assert special["background"] == "#191724"
    assert special["foreground"] == "#ecf0f1"


def test_json_structure(sample_scheme):
    """JSON output should have all expected keys."""
    data = sample_scheme.to_json()
    assert "wallpaper" in data
    assert "mood" in data
    assert "alpha" in data
    assert "special" in data
    assert "colors" in data
    assert "extended" not in data
    assert len(data["colors"]) == 16


def test_write_creates_file(sample_scheme):
    """Write should create the output file with valid JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "colors.json")
        sample_scheme.write(path)
        assert os.path.isfile(path)
        with open(path) as f:
            data = json.load(f)
        assert data["mood"] == "vibrant"
        assert len(data["colors"]) == 16


def test_write_creates_parent_dirs(sample_scheme):
    """Write should create parent directories if they don't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "nested", "deep", "colors.json")
        sample_scheme.write(path)
        assert os.path.isfile(path)
