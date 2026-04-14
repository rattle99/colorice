"""Pluggable mood system for palette variants."""

from abc import ABC, abstractmethod

import numpy as np

from .oklab import gamut_clamp, oklab_chroma, oklab_from_lch, oklab_hue


class BaseMood(ABC):
    """A mood transforms extracted Oklab colors into a palette variant."""

    name: str

    @abstractmethod
    def transform(self, colors: list[np.ndarray]) -> list[np.ndarray]:
        """Take extracted Oklab colors, return transformed Oklab colors."""
        ...


class MoodRegistry:
    """Registry for mood classes."""

    _moods: dict[str, type[BaseMood]] = {}

    @classmethod
    def register(cls, mood_cls: type[BaseMood]) -> type[BaseMood]:
        """Decorator to register a mood class."""
        cls._moods[mood_cls.name] = mood_cls
        return mood_cls

    @classmethod
    def get(cls, name: str) -> BaseMood:
        """Get a mood instance by name."""
        if name not in cls._moods:
            available = ", ".join(cls._moods.keys())
            raise ValueError(f"Unknown mood '{name}'. Available: {available}")
        return cls._moods[name]()

    @classmethod
    def list_names(cls) -> list[str]:
        """List all registered mood names."""
        return list(cls._moods.keys())


@MoodRegistry.register
class VibrantMood(BaseMood):
    """High saturation, wide lightness spread."""

    name = "vibrant"

    def transform(self, colors: list[np.ndarray]) -> list[np.ndarray]:
        result = []
        for c in colors:
            L = float(c[0])
            C = oklab_chroma(c)
            h = oklab_hue(c)
            new_C = min(C * 2.0, 0.35)
            if L > 0.5:
                new_L = min(L * 1.15, 0.95)
            else:
                new_L = max(L * 0.85, 0.15)
            result.append(gamut_clamp(oklab_from_lch(new_L, new_C, h)))
        return result


@MoodRegistry.register
class MutedMood(BaseMood):
    """Desaturated, pastel, compressed lightness range."""

    name = "muted"

    def transform(self, colors: list[np.ndarray]) -> list[np.ndarray]:
        result = []
        for c in colors:
            L = float(c[0])
            C = oklab_chroma(c)
            h = oklab_hue(c)
            new_C = C * 0.4
            new_L = L * 0.5 + 0.5 * 0.5
            result.append(gamut_clamp(oklab_from_lch(new_L, new_C, h)))
        return result


@MoodRegistry.register
class WarmMood(BaseMood):
    """Shift hues strongly toward warm tones."""

    name = "warm"

    def transform(self, colors: list[np.ndarray]) -> list[np.ndarray]:
        result = []
        for c in colors:
            L = float(c[0])
            C = oklab_chroma(c)
            h = oklab_hue(c)
            if 120 <= h <= 300:
                h = h - 60
                C = C * 0.7
            else:
                C = C * 1.4
            result.append(gamut_clamp(oklab_from_lch(L, min(C, 0.35), h % 360)))
        return result


@MoodRegistry.register
class CoolMood(BaseMood):
    """Shift hues strongly toward cool tones."""

    name = "cool"

    def transform(self, colors: list[np.ndarray]) -> list[np.ndarray]:
        result = []
        for c in colors:
            L = float(c[0])
            C = oklab_chroma(c)
            h = oklab_hue(c)
            if h >= 300 or h <= 120:
                h = h + 60
                C = C * 0.7
            else:
                C = C * 1.4
            result.append(gamut_clamp(oklab_from_lch(L, min(C, 0.35), h % 360)))
        return result
