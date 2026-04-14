"""Core ANSI role assignment algorithm.

Maps extracted Oklab colors to the 16 ANSI terminal color slots
with proper semantic roles.
"""

import numpy as np

from .contrast import enforce_contrast, ensure_distinguishable
from .extraction import HUE_CENTERS, HUE_SECTORS, _hue_in_sector
from .oklab import (
    gamut_clamp,
    oklab_chroma,
    oklab_from_lch,
    oklab_hue,
    oklab_to_hex,
)

# ANSI slot names
ANSI_ROLES = [
    "black",     # 0 - background
    "red",       # 1 - errors, deletions
    "green",     # 2 - success, additions
    "yellow",    # 3 - warnings
    "blue",      # 4 - info, links
    "magenta",   # 5 - keywords, special
    "cyan",      # 6 - strings, secondary
    "white",     # 7 - foreground
    # 8-15: bright variants
    "bright_black", "bright_red", "bright_green", "bright_yellow",
    "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
]


def _pick_background(colors: list[np.ndarray], light: bool = False) -> np.ndarray:
    """Pick background color: darkest (or lightest for light themes)."""
    if light:
        bg = max(colors, key=lambda c: float(c[0]))
        L = max(float(bg[0]), 0.93)
    else:
        bg = min(colors, key=lambda c: float(c[0]))
        L = min(float(bg[0]), 0.15)

    C = oklab_chroma(bg) * 0.5  # reduce chroma for bg
    h = oklab_hue(bg)
    return gamut_clamp(oklab_from_lch(L, C, h))


def _pick_foreground(
    colors: list[np.ndarray],
    bg: np.ndarray,
    min_contrast: float = 7.0,
    light: bool = False,
) -> np.ndarray:
    """Pick foreground: highest contrast against bg."""
    if light:
        candidates = sorted(colors, key=lambda c: float(c[0]))
    else:
        candidates = sorted(colors, key=lambda c: float(c[0]), reverse=True)

    # Start with the lightest/darkest candidate
    fg = candidates[0] if candidates else oklab_from_lch(0.95, 0.0, 0.0)
    return enforce_contrast(fg, bg, min_contrast)


def _classify_by_hue(colors: list[np.ndarray]) -> dict[str, list[np.ndarray]]:
    """Classify colors into hue sectors."""
    classified: dict[str, list[np.ndarray]] = {name: [] for name in HUE_SECTORS}

    for c in colors:
        h = oklab_hue(c)
        for sector_name, ranges in HUE_SECTORS.items():
            if _hue_in_sector(h, ranges):
                classified[sector_name].append(c)
                break

    return classified


def _select_or_synthesize(
    classified: dict[str, list[np.ndarray]],
    colors: list[np.ndarray],
) -> dict[str, np.ndarray]:
    """Select best candidate per sector, or synthesize if missing."""
    # Compute median L and C for synthesis fallback
    lightnesses = [float(c[0]) for c in colors]
    chromas = [oklab_chroma(c) for c in colors]
    median_L = float(np.median(lightnesses))
    median_C = float(np.median(chromas))

    selected = {}
    for sector_name in HUE_SECTORS:
        candidates = classified[sector_name]
        if candidates:
            # Pick most saturated
            selected[sector_name] = max(candidates, key=oklab_chroma)
        else:
            # Synthesize at sector center
            center_hue = HUE_CENTERS[sector_name]
            selected[sector_name] = gamut_clamp(
                oklab_from_lch(median_L, median_C, center_hue)
            )

    return selected


def assign_ansi_roles(
    colors: list[np.ndarray],
    min_contrast: float = 7.0,
    light: bool = False,
) -> list[str]:
    """Assign 16 ANSI colors from extracted Oklab colors.

    Returns list of 16 hex strings (color0 through color15).
    """
    # Step 1: Background and foreground
    bg = _pick_background(colors, light)
    fg = _pick_foreground(colors, bg, min_contrast, light)

    # Step 2: Classify remaining colors by hue
    # Exclude colors too close to bg/fg
    remaining = [
        c for c in colors
        if float(np.linalg.norm(c - bg)) > 0.05
        and float(np.linalg.norm(c - fg)) > 0.05
    ]
    if not remaining:
        remaining = list(colors)

    classified = _classify_by_hue(remaining)

    # Step 3: Select best per role
    selected = _select_or_synthesize(classified, colors)

    # Step 4: Enforce contrast
    ansi_colors_lab = [
        selected["red"],
        selected["green"],
        selected["yellow"],
        selected["blue"],
        selected["magenta"],
        selected["cyan"],
    ]

    contrast_min = min(min_contrast, 4.5)  # ANSI colors need at least 4.5:1
    for i in range(len(ansi_colors_lab)):
        ansi_colors_lab[i] = enforce_contrast(ansi_colors_lab[i], bg, contrast_min)

    ansi_colors_lab = ensure_distinguishable(ansi_colors_lab, min_delta=0.05)

    # Step 5: Generate bright variants
    bright_bg = bg.copy()
    if light:
        bright_bg[0] = max(0.0, bright_bg[0] - 0.15)
    else:
        bright_bg[0] = min(1.0, bright_bg[0] + 0.15)

    bright_colors = []
    for c in ansi_colors_lab:
        bc = c.copy()
        if light:
            bc[0] = max(0.0, bc[0] - 0.10)
        else:
            bc[0] = min(1.0, bc[0] + 0.10)
        # Boost chroma slightly
        C = oklab_chroma(bc)
        h = oklab_hue(bc)
        bc = oklab_from_lch(float(bc[0]), C * 1.1, h)
        bc = gamut_clamp(bc)
        bright_colors.append(enforce_contrast(bc, bg, contrast_min))

    bright_fg = fg.copy()
    if light:
        bright_fg[0] = max(0.0, bright_fg[0] - 0.08)
    else:
        bright_fg[0] = min(1.0, bright_fg[0] + 0.08)

    # Step 6: Assemble and convert to hex
    palette = [
        bg,                    # 0: black (background)
        ansi_colors_lab[0],    # 1: red
        ansi_colors_lab[1],    # 2: green
        ansi_colors_lab[2],    # 3: yellow
        ansi_colors_lab[3],    # 4: blue
        ansi_colors_lab[4],    # 5: magenta
        ansi_colors_lab[5],    # 6: cyan
        fg,                    # 7: white (foreground)
        bright_bg,             # 8: bright black
        bright_colors[0],      # 9: bright red
        bright_colors[1],      # 10: bright green
        bright_colors[2],      # 11: bright yellow
        bright_colors[3],      # 12: bright blue
        bright_colors[4],      # 13: bright magenta
        bright_colors[5],      # 14: bright cyan
        bright_fg,             # 15: bright white
    ]

    return [oklab_to_hex(gamut_clamp(c)) for c in palette]
