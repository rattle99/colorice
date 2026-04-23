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


def _shortest_hue_shift(h: float, target: float) -> float:
    """Compute the shortest signed rotation from h toward target on [0,360)."""
    diff = (target - h + 180) % 360 - 180
    return diff


@MoodRegistry.register
class WarmMood(BaseMood):
    """Shift hues toward warm tones (red/orange/yellow center ~30)."""

    name = "warm"
    _warm_center = 30.0  # red-orange

    def transform(self, colors: list[np.ndarray]) -> list[np.ndarray]:
        result = []
        for c in colors:
            L = float(c[0])
            C = oklab_chroma(c)
            h = oklab_hue(c)
            shift = _shortest_hue_shift(h, self._warm_center)
            # Pull 40% of the way toward warm center
            h = (h + shift * 0.4) % 360
            # Boost chroma for already-warm, reduce for cool
            if abs(shift) < 90:
                C = C * 1.4
            else:
                C = C * 0.7
            result.append(gamut_clamp(oklab_from_lch(L, min(C, 0.35), h)))
        return result


@MoodRegistry.register
class CoolMood(BaseMood):
    """Shift hues toward cool tones (blue/cyan center ~220)."""

    name = "cool"
    _cool_center = 220.0  # blue-cyan

    def transform(self, colors: list[np.ndarray]) -> list[np.ndarray]:
        result = []
        for c in colors:
            L = float(c[0])
            C = oklab_chroma(c)
            h = oklab_hue(c)
            shift = _shortest_hue_shift(h, self._cool_center)
            # Pull 40% of the way toward cool center
            h = (h + shift * 0.4) % 360
            # Boost chroma for already-cool, reduce for warm
            if abs(shift) < 90:
                C = C * 1.4
            else:
                C = C * 0.7
            result.append(gamut_clamp(oklab_from_lch(L, min(C, 0.35), h)))
        return result
