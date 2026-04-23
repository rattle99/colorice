"""CLI interface for colorice."""

import argparse
import json
import os
import sys

from . import __version__
from .cache import get_cache_key, load_cached, save_cache
from .display import interactive_select
from .paths import default_config_path, default_output_path
from .extraction import (
    extract_dominant_colors,
    extract_dominant_colors_segmented,
    fill_color_gaps,
    load_and_resize,
)
from .moods import MoodRegistry
from .palette import assign_ansi_roles, validate_palette
from .scheme import ColorScheme


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="colorice",
        description="Generate terminal color schemes from wallpaper images.",
    )
    parser.add_argument("image", nargs="?", default=None, help="Path to wallpaper image (PNG, JPG, WEBP)")
    parser.add_argument(
        "-o", "--output",
        default=default_output_path(),
        help=f"Output JSON path (default: {default_output_path()})",
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
        help=f"Path to config.toml (default: {default_config_path()})",
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
        "--init",
        action="store_true",
        help="Install default templates to the template directory and exit",
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
            print(f"  No templates configured. See {default_config_path()}", file=sys.stderr)
        return

    if not args.quiet:
        print("  Applying templates...", file=sys.stderr)
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

    # Install default config and templates, then exit
    if args.init:
        from .init_templates import install_default_config, install_default_templates
        from .paths import default_template_dir
        install_default_config(quiet=args.quiet)
        install_default_templates(default_template_dir(), quiet=args.quiet)
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
            print(f"  Loaded scheme from {output_path}", file=sys.stderr)
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

    # Extract colors (with caching)
    cache_key = get_cache_key(
        args.image,
        n_colors=args.colors,
        segment=args.segment,
    )
    dominant = load_cached(cache_key)

    if dominant is not None:
        if not args.quiet:
            print(f"  Using cached extraction for {args.image}", file=sys.stderr)
    else:
        if not args.quiet:
            print(f"  Extracting colors from {args.image}...", file=sys.stderr)

        try:
            if args.segment:
                dominant = extract_dominant_colors_segmented(args.image, n_colors=args.colors)
            else:
                pixels = load_and_resize(args.image)
                dominant = extract_dominant_colors(pixels, n_colors=args.colors)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        save_cache(cache_key, dominant)

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

    # Validate palette
    if not args.quiet:
        warnings = validate_palette(selected.colors)
        for w in warnings:
            print(w, file=sys.stderr)

    # Write output (skip if --dry-run)
    if not args.dry_run:
        selected.write(args.output)

        if not args.quiet:
            print(f"\n  Scheme written to {args.output}", file=sys.stderr)

    # Apply templates
    if args.apply or args.dry_run:
        _apply_templates(selected, args)
