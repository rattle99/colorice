"""Terminal palette preview using ANSI 24-bit escape codes."""

from colorice.oklab import hex_to_srgb
from colorice.scheme import ColorScheme

# Each color block is 6 chars wide, 8 blocks = 48 chars
BLOCK_WIDTH = 6


def _fg_escape(hex_color: str) -> str:
    """ANSI 24-bit foreground escape for a hex color."""
    r, g, b = (int(x * 255) for x in hex_to_srgb(hex_color))
    return f"\033[38;2;{r};{g};{b}m"


def _bg_escape(hex_color: str) -> str:
    """ANSI 24-bit background escape for a hex color."""
    r, g, b = (int(x * 255) for x in hex_to_srgb(hex_color))
    return f"\033[48;2;{r};{g};{b}m"


RESET = "\033[0m"
TOTAL_WIDTH = BLOCK_WIDTH * 8


def preview_palette(scheme: ColorScheme, index: int, total: int) -> str:
    """Render a visual palette preview."""
    lines = []
    bg = scheme.background
    fg = scheme.foreground
    block = " " * BLOCK_WIDTH

    lines.append(f"\n  Palette {index}/{total}: {scheme.mood}")
    lines.append("  " + "─" * TOTAL_WIDTH)

    # ANSI color blocks: normal (0-7)
    row = "  "
    for i in range(8):
        row += f"{_bg_escape(scheme.colors[i])}{block}{RESET}"
    lines.append(row)

    # ANSI color blocks: bright (8-15)
    row = "  "
    for i in range(8, 16):
        row += f"{_bg_escape(scheme.colors[i])}{block}{RESET}"
    lines.append(row)

    # Labels — centered in each block
    labels = ["BLK", "RED", "GRN", "YEL", "BLU", "MAG", "CYN", "WHT"]
    row = "  "
    for label in labels:
        row += label.center(BLOCK_WIDTH)
    lines.append(row)

    # Sample text on bg — padded to full width
    lines.append("")
    sample_text = "  The quick brown fox jumps over the lazy dog  "
    padded = sample_text.ljust(TOTAL_WIDTH)
    lines.append(f"  {_bg_escape(bg)}{_fg_escape(fg)}{padded}{RESET}")

    # ANSI colors as text on bg
    names = [" red ", " grn ", " yel ", " blu ", " mag ", " cyn "]
    row = f"  {_bg_escape(bg)}"
    for i, name in enumerate(names, 1):
        row += f"{_fg_escape(scheme.colors[i])}{name.center(BLOCK_WIDTH)}"
    # Pad remaining space
    row += " " * (TOTAL_WIDTH - BLOCK_WIDTH * len(names))
    row += RESET
    lines.append(row)

    lines.append("")
    return "\n".join(lines)


def interactive_select(schemes: list[ColorScheme]) -> ColorScheme:
    """Display all palettes and prompt user to select one."""
    import sys

    if not sys.stdin.isatty():
        return schemes[0]

    for i, scheme in enumerate(schemes, 1):
        print(preview_palette(scheme, i, len(schemes)))

    while True:
        try:
            choice = input(f"  Select palette (1-{len(schemes)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(schemes):
                return schemes[idx]
        except EOFError:
            return schemes[0]
        except ValueError:
            pass
        print(f"  Please enter a number between 1 and {len(schemes)}")
