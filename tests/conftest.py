"""Shared test fixtures."""

import pytest

from colorice.scheme import ColorScheme


@pytest.fixture
def sample_scheme() -> ColorScheme:
    """A scheme with 16 plausible hex colors."""
    return ColorScheme(
        wallpaper="/tmp/test.jpg",
        mood="vibrant",
        colors=[
            "#191724",
            "#ff4971",
            "#2ecc71",
            "#f1c40f",
            "#3498db",
            "#9b59b6",
            "#1abc9c",
            "#ecf0f1",
            "#34495e",
            "#e74c3c",
            "#27ae60",
            "#f39c12",
            "#2980b9",
            "#8e44ad",
            "#16a085",
            "#ffffff",
        ],
    )
