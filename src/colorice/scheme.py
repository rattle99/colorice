"""ColorScheme dataclass and JSON serialization."""

import json
import os
from dataclasses import dataclass

from .oklab import (
    gamut_clamp,
    hex_to_oklab,
    oklab_chroma,
    oklab_from_lch,
    oklab_hue,
    oklab_lightness,
    oklab_to_hex,
)


def _derive_extended_colors(colors: list[str]) -> dict[str, str]:
    """Generate additional 24-bit true colors derived from the 16 ANSI base.

    These are unique colors for UI elements and editor syntax highlighting
    that go beyond the 16 ANSI slots.
    """
    bg = hex_to_oklab(colors[0])
    fg = hex_to_oklab(colors[7])
    bg_L = oklab_lightness(bg)

    # Selection: bg shifted toward fg
    sel_bg = bg.copy()
    sel_bg[0] = bg_L + 0.1 if bg_L < 0.5 else bg_L - 0.1

    # Accent: most chromatic of colors 1-6
    accent_idx = max(range(1, 7), key=lambda i: oklab_chroma(hex_to_oklab(colors[i])))
    accent = hex_to_oklab(colors[accent_idx])

    # Border/split: between bg and fg
    border = bg.copy()
    border[0] = bg_L + 0.2 if bg_L < 0.5 else bg_L - 0.2

    # Line highlight: very subtle bg shift
    line_hl = bg.copy()
    line_hl[0] = bg_L + 0.04 if bg_L < 0.5 else bg_L - 0.04

    # Generate distinct editor colors by shifting hues from ANSI base
    def _shift(base_hex: str, L_offset: float, C_scale: float, h_offset: float) -> str:
        lab = hex_to_oklab(base_hex)
        L = min(max(oklab_lightness(lab) + L_offset, 0.0), 1.0)
        C = oklab_chroma(lab) * C_scale
        h = (oklab_hue(lab) + h_offset) % 360
        return oklab_to_hex(gamut_clamp(oklab_from_lch(L, C, h)))

    return {
        # UI elements
        "selection_bg": oklab_to_hex(gamut_clamp(sel_bg)),
        "selection_fg": colors[7],
        "accent": colors[accent_idx],
        "cursor": colors[4],
        "url": colors[12],  # bright blue
        "border": oklab_to_hex(gamut_clamp(border)),
        "split": oklab_to_hex(gamut_clamp(border)),
        "line_highlight": oklab_to_hex(gamut_clamp(line_hl)),
        "visual": _shift(colors[5], 0.0, 0.6, 0),  # muted magenta for visual selection
        "search_match": _shift(colors[3], 0.05, 1.2, 0),  # brighter yellow for search
        # Editor syntax — distinct from ANSI, derived by shifting
        "keyword": _shift(colors[5], 0.05, 1.1, 0),       # magenta, slightly brighter
        "function": _shift(colors[4], 0.08, 1.0, 15),      # blue shifted toward cyan
        "type": _shift(colors[6], 0.05, 1.1, -15),         # cyan shifted toward blue
        "string": _shift(colors[2], 0.0, 0.9, 10),         # green shifted
        "number": _shift(colors[3], 0.05, 1.0, -10),       # yellow shifted toward orange
        "constant": _shift(colors[1], -0.05, 0.9, 15),     # red shifted toward orange
        "comment": _shift(colors[8], 0.0, 0.5, 0),         # muted bright black
        "operator": _shift(colors[6], -0.05, 0.8, 20),     # cyan shifted
        "parameter": _shift(colors[4], 0.0, 0.85, -20),    # blue shifted toward magenta
        "property": _shift(colors[6], 0.08, 0.9, 0),       # brighter cyan
        "tag": _shift(colors[1], 0.05, 1.0, 0),            # brighter red
        "attribute": _shift(colors[3], 0.0, 0.9, 0),       # yellow
        "decorator": _shift(colors[5], -0.05, 1.1, -20),   # magenta shifted
        "heading": _shift(colors[4], 0.1, 1.2, 0),         # bold blue
        "link": _shift(colors[4], 0.05, 0.9, 10),          # blue-cyan
        "bold": colors[15],                                  # bright white
        "italic": _shift(colors[6], 0.0, 1.0, 0),          # cyan
        # Diff
        "diff_add": _shift(colors[2], 0.0, 0.8, 0),
        "diff_add_bg": _shift(colors[2], -0.3, 0.3, 0),
        "diff_delete": _shift(colors[1], 0.0, 0.8, 0),
        "diff_delete_bg": _shift(colors[1], -0.3, 0.3, 0),
        "diff_change": _shift(colors[3], 0.0, 0.8, 0),
        "diff_change_bg": _shift(colors[3], -0.3, 0.3, 0),
        # Diagnostics
        "error": colors[1],
        "warning": colors[3],
        "info": colors[4],
        "hint": colors[6],
        "success": colors[2],
    }


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

    @property
    def extended(self) -> dict[str, str]:
        return _derive_extended_colors(self.colors)

    def to_colorice_json(self) -> dict:
        """Full colorice JSON format."""
        return {
            "wallpaper": self.wallpaper,
            "mood": self.mood,
            "special": self.special,
            "colors": {f"color{i}": c for i, c in enumerate(self.colors)},
            "extended": self.extended,
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
