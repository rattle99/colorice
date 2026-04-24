"""Template variable resolver.

Builds a flat dict[str, str] from a ColorScheme for template substitution.
Supports pywal-compatible base variables, format modifiers, and Oklab
color manipulation filters.
"""

import re

from colorice.oklab import (
    gamut_clamp,
    hex_to_oklab,
    hex_to_srgb,
    oklab_chroma,
    oklab_from_lch,
    oklab_hue,
    oklab_lightness,
    oklab_to_hex,
)
from colorice.scheme import ColorScheme

# Color names that support modifiers/manipulations
_COLOR_NAMES = (
    [f"color{i}" for i in range(16)]
    + ["background", "foreground", "cursor"]
)

# Regex to find manipulation requests, supporting chains:
# {color0.lighten_20}, {color0.lighten_20.saturate_10}, {color0.lighten_20.strip}
# {color0.lighten_20.saturate_10.darken_5.strip}
_MANIPULATION_RE = re.compile(
    r"\{("
    r"(?:color\d+|background|foreground|cursor)"
    r"(?:\.(?:lighten|darken|saturate|desaturate)_\d+)+"
    r"(?:\.(?:strip|rgb|rgba|red|green|blue))?"
    r")\}"
)

_FORMAT_MODIFIERS = {"strip", "rgb", "rgba", "red", "green", "blue"}
_MANIPULATIONS = {"lighten", "darken", "saturate", "desaturate"}


def _format_modifiers(name: str, hex_color: str) -> dict[str, str]:
    """Generate format modifier variants for a color variable."""
    srgb = hex_to_srgb(hex_color)
    r, g, b = int(srgb[0] * 255), int(srgb[1] * 255), int(srgb[2] * 255)

    return {
        f"{name}.strip": hex_color.lstrip("#"),
        f"{name}.red": str(r),
        f"{name}.green": str(g),
        f"{name}.blue": str(b),
        f"{name}.rgb": f"rgb({r},{g},{b})",
        f"{name}.rgba": f"rgba({r},{g},{b},1.0)",
    }


def _compute_manipulation(hex_color: str, op: str, amount: int) -> str:
    """Apply a color manipulation in Oklab space.

    Args:
        hex_color: Source color as '#rrggbb'.
        op: One of 'lighten', 'darken', 'saturate', 'desaturate'.
        amount: Integer 0-100, treated as fraction of [0,1] range.

    Returns:
        Manipulated color as '#rrggbb', gamut clamped.
    """
    lab = hex_to_oklab(hex_color)
    L = oklab_lightness(lab)
    C = oklab_chroma(lab)
    h = oklab_hue(lab)
    frac = amount / 100.0

    if op == "lighten":
        L = min(1.0, L + frac)
    elif op == "darken":
        L = max(0.0, L - frac)
    elif op == "saturate":
        C = C + frac
    elif op == "desaturate":
        C = max(0.0, C - frac)

    return oklab_to_hex(gamut_clamp(oklab_from_lch(L, C, h)))


def _base_variables(scheme: ColorScheme) -> dict[str, str]:
    """Build base variables: color0-15, special names, wallpaper, alpha."""
    variables: dict[str, str] = {}

    for i, color in enumerate(scheme.colors):
        variables[f"color{i}"] = color

    variables["background"] = scheme.background
    variables["foreground"] = scheme.foreground
    variables["cursor"] = scheme.cursor
    variables["wallpaper"] = scheme.wallpaper
    variables["alpha"] = "100"

    return variables


def build_variables(scheme: ColorScheme, template_content: str) -> dict[str, str]:
    """Build the complete variable dictionary for template substitution.

    Args:
        scheme: The color scheme to resolve variables from.
        template_content: Raw template text, scanned for manipulation
            requests so only needed derivations are computed.

    Returns:
        Flat dict mapping variable names to string values.
    """
    variables = _base_variables(scheme)

    # Add format modifiers for all color names
    for name in _COLOR_NAMES:
        if name in variables:
            variables.update(_format_modifiers(name, variables[name]))

    # Scan template for manipulation requests and compute them lazily
    for match in _MANIPULATION_RE.finditer(template_content):
        full_key = match.group(1)
        if full_key in variables:
            continue  # already computed

        parts = full_key.split(".")
        base_name = parts[0]

        base_hex = variables.get(base_name)
        if base_hex is None or not base_hex.startswith("#"):
            continue

        # Separate manipulation ops from trailing format modifier
        manip_parts = []
        format_modifier = None
        for part in parts[1:]:
            op_name, _, _ = part.partition("_")
            if op_name in _MANIPULATIONS:
                manip_parts.append(part)
            else:
                format_modifier = part
                break

        # Apply manipulations left to right
        current_hex = base_hex
        for manip in manip_parts:
            op, _, amount_str = manip.partition("_")
            current_hex = _compute_manipulation(current_hex, op, int(amount_str))

        # Store the full manipulation chain result
        manip_key = base_name + "." + ".".join(manip_parts)
        if manip_key not in variables:
            variables[manip_key] = current_hex

        # Apply format modifier if present
        if format_modifier:
            mod_vars = _format_modifiers(manip_key, current_hex)
            variables.update(mod_vars)

    return variables
