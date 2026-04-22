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

    def to_json(self) -> dict:
        """JSON output format (compatible with pywal)."""
        return {
            "wallpaper": self.wallpaper,
            "mood": self.mood,
            "alpha": "100",
            "special": self.special,
            "colors": {f"color{i}": c for i, c in enumerate(self.colors)},
        }

    def write(self, path: str) -> None:
        """Write JSON to path, or stdout if path is '-'."""
        import sys

        data = self.to_json()

        if path == "-":
            json.dump(data, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
