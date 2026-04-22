"""CLI interface for colorice."""

import argparse
import json
import os
import sys

from . import __version__
from .display import interactive_select
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
    parser.add_argument("image", nargs="?", default=None, help="Path to wallpaper image (PNG, JPG, WEBP)")
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
        help="Number of dominant colors to extract (3-16, default: 8)",
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
        "-a", "--apply",
        action="store_true",
        help="Apply color scheme to configured templates",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to config.toml (default: ~/.config/colorice/config.toml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview template output without writing files",
    )
    parser.add_argument(
        "--no-hooks",
        action="store_true",
        help="Skip post-apply hooks",
    )
    parser.add_argument(
        "--list-moods",
        action="store_true",
        help="List available mood names and exit",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"colorice {__version__}",
    )
    return parser


def _load_scheme_from_file(path: str) -> ColorScheme:
    """Load a ColorScheme from an existing JSON file."""
    with open(path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Malformed JSON in {path}: {e}", file=sys.stderr)
            sys.exit(1)

    colors_data = data.get("colors", {})
    colors = []
    for i in range(16):
        key = f"color{i}"
        if key not in colors_data:
            print(f"Error: Missing '{key}' in {path}. Expected 16 colors (color0-color15).", file=sys.stderr)
            sys.exit(1)
        colors.append(colors_data[key])

    return ColorScheme(
        wallpaper=data.get("wallpaper", ""),
        mood=data.get("mood", "unknown"),
        colors=colors,
    )


def _apply_templates(scheme: ColorScheme, args: argparse.Namespace) -> None:
    """Apply scheme to configured templates."""
    from .config import load_config
    from .templates.applicator import apply_all_templates

    config = load_config(args.config)
    if not config.templates:
        if not args.quiet:
            print("  No templates configured. See ~/.config/colorice/config.toml")
        return

    if not args.quiet:
        print("  Applying templates...")
    apply_all_templates(
        scheme,
        config,
        dry_run=args.dry_run,
        no_hooks=args.no_hooks,
        quiet=args.quiet,
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # List moods and exit
    if args.list_moods:
        for name in MoodRegistry.list_names():
            print(name)
        return

    # Apply-only mode: no image, load existing scheme
    if args.image is None:
        if not (args.apply or args.dry_run):
            parser.error("image is required unless --apply or --dry-run is used")

        output_path = os.path.expanduser(args.output)
        if not os.path.isfile(output_path):
            print(f"Error: No scheme found at {output_path}. Generate one first.", file=sys.stderr)
            sys.exit(1)

        selected = _load_scheme_from_file(output_path)
        if not args.quiet:
            print(f"  Loaded scheme from {output_path}")
        _apply_templates(selected, args)
        return

    # Validate color count
    if args.colors < 3 or args.colors > 16:
        parser.error("--colors must be between 3 and 16")

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
        added = False
        for m in default_moods:
            if m not in mood_names and len(mood_names) < args.num_palettes:
                mood_names.append(m)
                added = True
        if not added:
            break

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

    # Write output (skip if --dry-run)
    if not args.dry_run:
        selected.write(args.output)

        if not args.quiet:
            print(f"\n  Scheme written to {args.output}")

    # Apply templates
    if args.apply or args.dry_run:
        _apply_templates(selected, args)
