"""Oklab <-> sRGB color space conversion.

Oklab is a perceptually uniform color space where Euclidean distance
corresponds to perceived color difference. This makes it ideal for
clustering and palette generation.

Reference: https://bottosson.github.io/posts/oklab/
"""

import numpy as np


def srgb_to_linear(srgb: np.ndarray) -> np.ndarray:
    """Apply inverse sRGB companding (gamma decode).

    Input: sRGB values in [0, 1]
    Output: linear RGB values in [0, 1]
    """
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(linear: np.ndarray) -> np.ndarray:
    """Apply sRGB companding (gamma encode).

    Input: linear RGB values in [0, 1]
    Output: sRGB values in [0, 1]
    """
    linear = np.clip(linear, 0, None)  # avoid negative values in power
    return np.where(linear <= 0.0031308, 12.92 * linear, 1.055 * linear ** (1 / 2.4) - 0.055)


def linear_rgb_to_oklab(rgb: np.ndarray) -> np.ndarray:
    """Convert linear sRGB to Oklab.

    Input: (N, 3) linear RGB in [0, 1]
    Output: (N, 3) Oklab [L, a, b] where L in [0, 1]
    """
    # sRGB to LMS (approximate)
    m1 = np.array([
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ])
    lms = rgb @ m1.T
    lms_g = np.cbrt(lms)

    # LMS to Oklab
    m2 = np.array([
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ])
    return lms_g @ m2.T


def oklab_to_linear_rgb(lab: np.ndarray) -> np.ndarray:
    """Convert Oklab to linear sRGB.

    Input: (N, 3) Oklab [L, a, b]
    Output: (N, 3) linear RGB (may be out of [0, 1] gamut)
    """
    # Oklab to LMS
    m2_inv = np.array([
        [1.0, 0.3963377774, 0.2158037573],
        [1.0, -0.1055613458, -0.0638541728],
        [1.0, -0.0894841775, -1.2914855480],
    ])
    lms_g = lab @ m2_inv.T
    lms = lms_g ** 3

    # LMS to sRGB
    m1_inv = np.array([
        [4.0767416621, -3.3077115913, 0.2309699292],
        [-1.2684380046, 2.6097574011, -0.3413193965],
        [-0.0041960863, -0.7034186147, 1.7076147010],
    ])
    return lms @ m1_inv.T


def srgb_to_oklab(srgb: np.ndarray) -> np.ndarray:
    """Convert sRGB [0, 1] to Oklab."""
    return linear_rgb_to_oklab(srgb_to_linear(srgb))


def oklab_to_srgb(lab: np.ndarray) -> np.ndarray:
    """Convert Oklab to sRGB [0, 1], clamped to gamut."""
    return np.clip(linear_to_srgb(oklab_to_linear_rgb(lab)), 0, 1)


def hex_to_srgb(hex_color: str) -> np.ndarray:
    """Convert '#rrggbb' to sRGB [0, 1] array."""
    h = hex_color.lstrip("#")
    return np.array([int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)])


def srgb_to_hex(srgb: np.ndarray) -> str:
    """Convert sRGB [0, 1] array to '#rrggbb'."""
    rgb = np.clip(np.round(srgb * 255), 0, 255).astype(int)
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def hex_to_oklab(hex_color: str) -> np.ndarray:
    """Convert '#rrggbb' to Oklab [L, a, b]."""
    srgb = hex_to_srgb(hex_color)
    return srgb_to_oklab(srgb.reshape(1, 3))[0]


def oklab_to_hex(lab: np.ndarray) -> str:
    """Convert Oklab [L, a, b] to '#rrggbb', gamut clamped."""
    srgb = oklab_to_srgb(lab.reshape(1, 3))[0]
    return srgb_to_hex(srgb)


def oklab_lightness(lab: np.ndarray) -> float:
    """Get L component (perceived lightness, 0 to 1)."""
    return float(lab[0])


def oklab_chroma(lab: np.ndarray) -> float:
    """Get chroma (saturation proxy): sqrt(a² + b²)."""
    return float(np.sqrt(lab[1] ** 2 + lab[2] ** 2))


def oklab_hue(lab: np.ndarray) -> float:
    """Get hue angle in degrees [0, 360)."""
    return float(np.degrees(np.arctan2(lab[2], lab[1])) % 360)


def oklab_from_lch(L: float, C: float, h_deg: float) -> np.ndarray:
    """Create Oklab color from lightness, chroma, hue (degrees)."""
    h_rad = np.radians(h_deg)
    return np.array([L, C * np.cos(h_rad), C * np.sin(h_rad)])


def gamut_clamp(lab: np.ndarray) -> np.ndarray:
    """Reduce chroma until color is within sRGB gamut, preserving L and hue."""
    L = lab[0]
    C = oklab_chroma(lab)
    h = oklab_hue(lab)

    if C == 0:
        return lab

    # Binary search on chroma
    lo, hi = 0.0, C
    result = oklab_from_lch(L, 0, h)  # fallback: achromatic

    for _ in range(32):
        mid = (lo + hi) / 2
        candidate = oklab_from_lch(L, mid, h)
        rgb = oklab_to_linear_rgb(candidate.reshape(1, 3))[0]
        if np.all(rgb >= -0.001) and np.all(rgb <= 1.001):
            lo = mid
            result = candidate
        else:
            hi = mid

    return result
