"""CLI interface for colorice."""

import argparse
import os
import sys

from . import __version__
from .display import interactive_select, preview_palette
from .extraction import (
    extract_dominant_colors,
    extract_dominant_colors_segmented,
    fill_color_gaps,
    load_and_resize,
)
from .moods import MoodRegistry
from .palette import assign_ansi_roles
from .scheme import ColorScheme


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="colorice",
        description="Generate terminal color schemes from wallpaper images.",
    )
    parser.add_argument("image", help="Path to wallpaper image (PNG, JPG, WEBP)")
    parser.add_argument(
        "-o", "--output",
        default=os.path.expanduser("~/.config/colorice/colors.json"),
        help="Output JSON path (default: ~/.config/colorice/colors.json)",
    )
    parser.add_argument(
        "-n", "--num-palettes",
        type=int,
        default=4,
        help="Number of palette variants to generate (default: 4)",
    )
    parser.add_argument(
        "-m", "--moods",
        default="vibrant,muted,warm,cool",
        help="Comma-separated mood names (default: vibrant,muted,warm,cool)",
    )
    parser.add_argument(
        "-c", "--colors",
        type=int,
        default=8,
        help="Number of dominant colors to extract (5-12, default: 8)",
    )
    parser.add_argument(
        "--min-contrast",
        type=float,
        default=7.0,
        help="Minimum fg/bg contrast ratio (default: 7.0)",
    )
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Semantic mode — enforce ANSI color name conventions (red looks red, etc.)",
    )
    parser.add_argument(
        "--format",
        choices=["colorice", "pywal"],
        default="colorice",
        help="Output format (default: colorice)",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Skip preview, output first palette",
    )
    parser.add_argument(
        "--light",
        action="store_true",
        help="Generate light theme",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress preview output",
    )
    parser.add_argument(
        "--segment",
        action="store_true",
        help="Use Felzenszwalb segmentation for region-aware extraction (requires scikit-image)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"colorice {__version__}",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Validate image path
    if not os.path.isfile(args.image):
        print(f"Error: Image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    # Parse moods
    mood_names = [m.strip() for m in args.moods.split(",")]
    mood_names = mood_names[: args.num_palettes]

    # Pad with defaults if fewer moods than requested palettes
    default_moods = ["vibrant", "muted", "warm", "cool"]
    while len(mood_names) < args.num_palettes:
        for m in default_moods:
            if m not in mood_names and len(mood_names) < args.num_palettes:
                mood_names.append(m)

    # Extract colors
    if not args.quiet:
        print(f"  Extracting colors from {args.image}...")

    if args.segment:
        dominant = extract_dominant_colors_segmented(args.image, n_colors=args.colors)
    else:
        pixels = load_and_resize(args.image)
        dominant = extract_dominant_colors(pixels, n_colors=args.colors)

    # Only fill hue gaps in semantic mode
    if args.semantic:
        dominant = fill_color_gaps(dominant)

    # Generate palettes for each mood
    schemes = []
    for mood_name in mood_names:
        mood = MoodRegistry.get(mood_name)
        transformed = mood.transform(dominant)
        ansi_colors = assign_ansi_roles(
            transformed,
            min_contrast=args.min_contrast,
            light=args.light,
            semantic=args.semantic,
        )
        scheme = ColorScheme(
            wallpaper=os.path.abspath(args.image),
            mood=mood_name,
            colors=ansi_colors,
        )
        schemes.append(scheme)

    # Select palette
    if args.no_preview or args.quiet:
        selected = schemes[0]
    else:
        selected = interactive_select(schemes)

    # Write output
    selected.write(args.output, fmt=args.format)

    if not args.quiet:
        print(f"\n  Scheme written to {args.output}")
