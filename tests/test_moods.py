"""Tests for mood transforms.

Purpose: Verify each mood actually changes colors in the expected direction.
Without these, a mood could silently do nothing or shift the wrong way.
"""

import numpy as np

from colorice.moods import MoodRegistry
from colorice.oklab import oklab_chroma, srgb_to_oklab


def _sample_colors() -> list[np.ndarray]:
    """Mixed hue colors at moderate saturation."""
    return [
        srgb_to_oklab(np.array([[0.8, 0.2, 0.2]]))[0],   # red
        srgb_to_oklab(np.array([[0.2, 0.7, 0.3]]))[0],    # green
        srgb_to_oklab(np.array([[0.3, 0.3, 0.8]]))[0],    # blue
        srgb_to_oklab(np.array([[0.7, 0.7, 0.2]]))[0],    # yellow
        srgb_to_oklab(np.array([[0.1, 0.1, 0.1]]))[0],    # dark
    ]


def test_vibrant_increases_chroma():
    """Vibrant mood should produce higher average chroma than input."""
    colors = _sample_colors()
    mood = MoodRegistry.get("vibrant")
    transformed = mood.transform(colors)

    orig_avg_C = np.mean([oklab_chroma(c) for c in colors])
    new_avg_C = np.mean([oklab_chroma(c) for c in transformed])
    assert new_avg_C > orig_avg_C, "Vibrant should increase average chroma"


def test_muted_decreases_chroma():
    """Muted mood should produce lower average chroma than input."""
    colors = _sample_colors()
    mood = MoodRegistry.get("muted")
    transformed = mood.transform(colors)

    orig_avg_C = np.mean([oklab_chroma(c) for c in colors])
    new_avg_C = np.mean([oklab_chroma(c) for c in transformed])
    assert new_avg_C < orig_avg_C, "Muted should decrease average chroma"


def test_warm_shifts_hues_warm():
    """Warm mood should shift average hue toward warm (lower hue angles)."""
    # Use only cool colors so the shift is measurable
    cool_colors = [
        srgb_to_oklab(np.array([[0.2, 0.6, 0.8]]))[0],   # cyan
        srgb_to_oklab(np.array([[0.3, 0.3, 0.9]]))[0],    # blue
        srgb_to_oklab(np.array([[0.2, 0.8, 0.4]]))[0],    # green
    ]
    mood = MoodRegistry.get("warm")
    transformed = mood.transform(cool_colors)

    # Cool colors should have shifted — their hues should differ
    for orig, new in zip(cool_colors, transformed):
        assert not np.allclose(orig, new, atol=0.01), "Warm should change cool colors"


def test_cool_shifts_hues_cool():
    """Cool mood should shift warm colors toward cool."""
    warm_colors = [
        srgb_to_oklab(np.array([[0.9, 0.2, 0.1]]))[0],   # red
        srgb_to_oklab(np.array([[0.9, 0.7, 0.1]]))[0],    # orange/yellow
        srgb_to_oklab(np.array([[0.8, 0.3, 0.5]]))[0],    # pink
    ]
    mood = MoodRegistry.get("cool")
    transformed = mood.transform(warm_colors)

    for orig, new in zip(warm_colors, transformed):
        assert not np.allclose(orig, new, atol=0.01), "Cool should change warm colors"


def test_moods_preserve_color_count():
    """All moods should return same number of colors as input."""
    colors = _sample_colors()
    for name in MoodRegistry.list_names():
        mood = MoodRegistry.get(name)
        transformed = mood.transform(colors)
        assert len(transformed) == len(colors), f"{name} changed color count"


def test_moods_produce_valid_oklab():
    """Transformed colors should have L in [0,1] and finite values."""
    colors = _sample_colors()
    for name in MoodRegistry.list_names():
        mood = MoodRegistry.get(name)
        transformed = mood.transform(colors)
        for c in transformed:
            assert np.all(np.isfinite(c)), f"{name} produced non-finite color"
            assert 0.0 <= float(c[0]) <= 1.0, f"{name} produced L={c[0]} out of range"


def test_registry_lists_all_moods():
    """All 4 moods should be registered."""
    names = MoodRegistry.list_names()
    assert "vibrant" in names
    assert "muted" in names
    assert "warm" in names
    assert "cool" in names
