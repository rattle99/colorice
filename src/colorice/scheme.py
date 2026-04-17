"""ColorScheme dataclass and JSON serialization."""

import json
import os
from dataclasses import dataclass


@dataclass
class ColorScheme:
    """Complete color scheme output."""

    wallpaper: str
    mood: str
    colors: list[str]  # 16 hex colors, color0-color15

    @property
    def background(self) -> str:
        return self.colors[0]

    @property
    def foreground(self) -> str:
        return self.colors[7]

    @property
    def cursor(self) -> str:
        return self.colors[4]

    @property
    def special(self) -> dict[str, str]:
        return {
            "background": self.background,
            "foreground": self.foreground,
            "cursor": self.cursor,
        }

    def to_colorice_json(self) -> dict:
        """Full colorice JSON format."""
        return {
            "wallpaper": self.wallpaper,
            "mood": self.mood,
            "special": self.special,
            "colors": {f"color{i}": c for i, c in enumerate(self.colors)},
        }

    def to_pywal_json(self) -> dict:
        """Pywal-compatible JSON format."""
        return {
            "wallpaper": self.wallpaper,
            "alpha": "100",
            "special": self.special,
            "colors": {f"color{i}": c for i, c in enumerate(self.colors)},
        }

    def write(self, path: str, fmt: str = "colorice") -> None:
        """Write JSON to path."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        if fmt == "pywal":
            data = self.to_pywal_json()
        else:
            data = self.to_colorice_json()

        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
