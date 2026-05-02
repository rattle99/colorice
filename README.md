# Colorice

[![PyPI](https://img.shields.io/pypi/v/colorice?style=for-the-badge&logo=pypi&logoColor=white&color=bd93f9)](https://pypi.org/project/colorice/)
[![Python](https://img.shields.io/pypi/pyversions/colorice?style=for-the-badge&logo=python&logoColor=white&color=bd93f9)](https://pypi.org/project/colorice/)
[![License](https://img.shields.io/badge/license-GPL--3.0-bd93f9?style=for-the-badge)](LICENSE)

Colorice is a modern alternative to pywal that uses Oklab color space for perceptually accurate color extraction, generates multiple mood variants (vibrant, muted, warm, cool) to preview and select from, enforces WCAG contrast ratios, and applies schemes across your full desktop rice via a pywal-compatible template engine(yes existing pywal templates work) with color manipulation filters.

### 📸 In Action
<p align="center">
  <img width="99%" alt="Hero" src="https://github.com/user-attachments/assets/39fe3af7-aea9-4107-b697-b3ec0b3cb5e2" />
</p>
<br><br>

<details>
  <summary>More Examples! ✨ </summary>
  
  <p align="center">
    <img width="49%" alt="image3" src="https://github.com/user-attachments/assets/d1a260b9-b547-4fe6-97c7-5c6243deb82b" />
    <img width="49%" alt="image1" src="https://github.com/user-attachments/assets/cc4babb2-9e72-4a1a-a45c-c539d9617de9" />
  </p>
  
  <p align="center">
    <img width="49%" alt="image4" src="https://github.com/user-attachments/assets/fdabeb25-ac64-483e-9bdd-8eebec100fb4" />
    <img width="49%" alt="image2" src="https://github.com/user-attachments/assets/9f8480f9-303e-422f-b470-34b2f4d26154" />
  </p>
  <p align="center"><em>From image → a complete desktop theme</em></p>
  <p></p>
  <br><br>
  
   
  <p align="center">
    <img width="49%" alt="Monochrome_A" src="https://github.com/user-attachments/assets/74c87089-565d-4318-9ae6-7eae472851b5" />
    <img width="49%" alt="Monochrome_B" src="https://github.com/user-attachments/assets/a1483904-12a7-4f7c-b3ae-ca6aae8dce0f" />
  </p>
  <p align="center"><em>Respects contrast ratios even for palettes sourced from mostly monochrome or flat images.</em></p>
  <p></p>
  <br><br>
  
  <p align="center">
    <img width="49%" alt="2026-05-02_05-50" src="https://github.com/user-attachments/assets/15af6d3e-0110-4ee5-ae5c-c51b739596e6" />
    <img width="49%" alt="2026-05-02_05-50_1" src="https://github.com/user-attachments/assets/d01bc890-d2d2-4f92-91b4-9dfc4e3e5733" />
  </p>
  <p align="center"><em>Picks a rich variety of colours for your palette given a rich and vibrant image.</em></p>
  <p></p>
  <br><br>
</details>

## Install

Requires Python 3.11+.

```bash
pipx install colorice
```

Or with pip:

```bash
pip install colorice
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

This copies templates to `~/.config/colorice/templates/` for: kitty, alacritty, foot, ghostty, wezterm, hyprland, i3, sway, rofi, dunst, mako, waybar, polybar, swaylock, zellij, neovim, vim, cava, xresources, and shell variables.

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
git clone https://github.com/rattle99/colorice.git
cd colorice
pip install -e ".[dev]"
pytest
```

## License

GPL-3.0
