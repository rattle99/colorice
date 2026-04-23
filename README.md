# Colorice

Generate terminal color schemes from wallpaper images.

Colorice extracts dominant colors from an image using perceptually uniform Oklab color space, builds a complete 16-color ANSI palette, and enforces WCAG contrast ratios for readability. It generates multiple mood variants (vibrant, muted, warm, cool), lets you pick the one you like, and applies it directly to your tools via a pywal-compatible template engine.

## Install

```bash
pip install -e .

# With Felzenszwalb segmentation support
pip install -e ".[segment]"
```

## Quick start

```bash
# Install default templates for common tools
colorice --init

# Generate a scheme and apply to your configured tools
colorice ~/wallpapers/sunset.jpg --apply
```

This will:
1. Extract dominant colors using over-cluster + farthest-first diversity selection
2. Generate 4 palette variants (vibrant, muted, warm, cool)
3. Preview them in your terminal — pick one
4. Write the scheme to `~/.local/share/colorice/colors.json`
5. Render configured templates and reload your apps

## Options

```
colorice <image> [options]

Extraction:
  -c, --colors N            Dominant colors to extract (3-16, default: 8)
  --segment                 Region-aware extraction via Felzenszwalb segmentation
                            (requires scikit-image)

Palette:
  -m, --moods MOOD[,...]    Mood names (default: vibrant,muted,warm,cool)
  --min-contrast RATIO      Min fg/bg contrast ratio (default: 7.0)
  --semantic                Enforce ANSI color name conventions (red=red, etc.)
  --light                   Light theme

Output:
  -o, --output PATH         Output JSON path (default: ~/.local/share/colorice/colors.json)
                            Use -o - for stdout
  --no-preview              Skip preview, output first palette
  -q, --quiet               Suppress all output except errors

Templates:
  -a, --apply               Apply scheme to configured templates
  --config PATH             Path to config.toml
  --dry-run                 Preview template output without writing files
  --no-hooks                Skip post-apply hooks
  --init                    Install default templates and exit

Info:
  --list-moods              List available mood names and exit
  -v, --version             Show version and exit
```

## Examples

```bash
# Generate and interactively select a scheme
colorice ~/wallpapers/sunset.jpg

# Generate, select, and apply to all configured tools
colorice ~/wallpapers/sunset.jpg --apply

# Quiet mode, pipe JSON to stdout
colorice ~/wallpapers/ocean.png -q -o -

# Light theme with specific moods
colorice wallpaper.jpg --light -m vibrant,cool

# Region-aware extraction (better for complex images)
colorice wallpaper.jpg --segment --apply

# Re-apply existing scheme to templates (no image needed)
colorice --apply

# Preview template output without writing
colorice wallpaper.jpg --dry-run --apply
```

## Template system

Colorice includes a pywal-compatible template engine. Templates use `{color0}` through `{color15}`, `{background}`, `{foreground}`, `{cursor}`, and `{wallpaper}` placeholders.

### Setup

```bash
# Install bundled templates for common tools
colorice --init
```

This copies templates to `~/.config/colorice/templates/` for: kitty, alacritty, foot, ghostty, wezterm, hyprland, i3, sway, rofi, dunst, mako, waybar, polybar, swaylock, zellij, neovim, vim, xresources, and shell variables.

### Configuration

Edit `~/.config/colorice/config.toml` to map templates to output paths:

```toml
[[templates]]
name = "kitty"
input = "kitty.conf"
output = "~/.config/kitty/current-theme.conf"
hook = "killall -USR1 kitty"

[[templates]]
name = "hyprland"
input = "hyprland-colors.conf"
output = "~/.config/hypr/colorice-colors.conf"
```

Then add the include directive in your app config (one-time setup):
- Kitty: `include ~/.config/kitty/current-theme.conf`
- Alacritty: `import = ["~/.config/alacritty/colorice-theme.toml"]`
- Hyprland: `source = ~/.config/hypr/colorice-colors.conf`
- i3/Sway: `include ~/.config/i3/colorice-colors.conf`
- See each template file for tool-specific instructions.

### Color manipulation

Templates support Oklab color manipulation filters for deriving colors beyond the base 16:

```
{color4.lighten_20}           Increase lightness by 0.20
{color0.darken_10}            Decrease lightness by 0.10
{color1.saturate_15}          Increase chroma by 0.15
{color5.desaturate_10}        Decrease chroma by 0.10
{color4.lighten_20.strip}     Manipulation + format modifier
```

Manipulations can be chained — they apply left to right:

```
{color4.lighten_20.saturate_10.strip}
{color0.darken_10.desaturate_5}
```

Format modifiers (always last in the chain):
- `.strip` — hex without `#` (`1a2b3c`)
- `.red`, `.green`, `.blue` — integer channel value (0-255)
- `.rgb` — `rgb(26,43,60)`
- `.rgba` — `rgba(26,43,60,1.0)`

## How it works

1. **Extract** — loads the image, resizes for performance, runs KMeans clustering in Oklab color space. Over-clusters to 4x the requested count, then uses farthest-first selection for maximum perceptual diversity. Optionally uses Felzenszwalb segmentation for region-aware extraction.
2. **Cache** — extraction results are cached by image content hash + params in `~/.cache/colorice/`. Same wallpaper with same settings skips re-extraction.
3. **Mood transform** — adjusts chroma, lightness, and hue for the selected mood variant.
4. **Assign roles** — maps colors to 16 ANSI slots. In default (aesthetic) mode, sorts by chroma for wallpaper-matching palettes. In `--semantic` mode, enforces hue-zone mapping (red=slot 1, green=slot 2, etc.).
5. **Enforce contrast** — binary search on Oklab lightness to meet WCAG contrast ratios against the background.
6. **Validate** — warns about any ANSI color pairs that are too similar (pairwise Oklab distance check).
7. **Apply** — renders templates with the scheme and runs post-apply hooks.

## File locations (XDG-compliant)

```
~/.config/colorice/
  config.toml            Template configuration
  templates/             Template files

~/.local/share/colorice/
  colors.json            Generated scheme

~/.cache/colorice/
  <hash>.json            Extraction cache
```

Respects `$XDG_CONFIG_HOME`, `$XDG_DATA_HOME`, and `$XDG_CACHE_HOME`.

## Development

```bash
pip install -e ".[dev]"
pytest
```
