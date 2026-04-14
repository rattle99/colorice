# Colorice

Generate terminal color schemes from wallpaper images.

Colorice extracts dominant colors from an image, uses color theory to build a complete palette, and enforces WCAG contrast ratios for readability. It generates multiple mood variants (vibrant, muted, warm, cool) and lets you pick the one you like.

## Install

```bash
pip install -e .
```

## Usage

```bash
colorice wallpaper.jpg
```

This will:
1. Extract dominant colors from the image
2. Generate 4 palette variants (vibrant, muted, warm, cool)
3. Preview them in your terminal
4. Write the selected scheme to `~/.config/colorice/colors.json`

### Options

```
colorice <image> [options]

  -o, --output PATH         Output JSON path (default: ~/.config/colorice/colors.json)
  -n, --num-palettes N      Number of palette variants (default: 4)
  -m, --moods MOOD[,...]    Mood names (default: vibrant,muted,warm,cool)
  -c, --colors N            Dominant colors to extract (5-12, default: 8)
  --min-contrast RATIO      Min fg/bg contrast ratio (default: 7.0)
  --format FORMAT           Output: colorice|pywal (default: colorice)
  --no-preview              Skip preview, output first palette
  --light                   Light theme
  -q, --quiet               Suppress preview
```

### Examples

```bash
# Generate and select a scheme
colorice ~/wallpapers/sunset.jpg

# Quiet mode, output pywal-compatible JSON
colorice ~/wallpapers/ocean.png --format pywal -q

# Light theme with 2 palettes
colorice wallpaper.jpg --light -n 2

# Custom moods
colorice wallpaper.jpg -m vibrant,cool
```

## Output

The JSON output can be consumed by template systems like pywal or wallust to apply the scheme to your terminal, editor, window manager, etc.

## How It Works

1. **Extract** — loads the image, resizes for performance, runs KMeans clustering in Oklab color space (perceptually uniform)
2. **Fill gaps** — if the image lacks certain hue sectors (e.g., no green), synthesizes colors using color theory
3. **Mood transform** — adjusts chroma/hue for the selected mood variant
4. **Assign roles** — maps colors to the 16 ANSI slots by hue zone (red for errors, green for success, etc.)
5. **Enforce contrast** — adjusts lightness to meet WCAG contrast ratios against the background
6. **Output** — writes JSON with ANSI colors, extended colors, and semantic roles

## Development

```bash
pip install -e ".[dev]"
pytest
```
