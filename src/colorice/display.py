"""Terminal palette preview using ANSI 24-bit escape codes."""

from .oklab import hex_to_srgb
from .scheme import ColorScheme

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
    ext = scheme.extended
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

    # Extended syntax colors preview
    lines.append("")
    lines.append(f"  {_fg_escape(ext['comment'])}// Extended 24-bit syntax colors{RESET}")

    def _syntax_line(content: str) -> str:
        padded = content.ljust(TOTAL_WIDTH)
        return f"  {_bg_escape(bg)}{padded}{RESET}"

    line1 = (
        f"{_fg_escape(ext['keyword'])}func "
        f"{_fg_escape(ext['function'])}main"
        f"{_fg_escape(fg)}("
        f"{_fg_escape(ext['parameter'])}args"
        f"{_fg_escape(ext['operator'])}: "
        f"{_fg_escape(ext['type'])}List"
        f"{_fg_escape(fg)})"
    )
    lines.append(_syntax_line(line1))

    line2 = (
        f"  {_fg_escape(ext['keyword'])}val "
        f"{_fg_escape(fg)}x"
        f"{_fg_escape(ext['operator'])} = "
        f"{_fg_escape(ext['number'])}42"
        f"{_fg_escape(ext['operator'])} + "
        f"{_fg_escape(ext['string'])}\"hello\""
    )
    lines.append(_syntax_line(line2))

    line3 = (
        f"  {_fg_escape(ext['decorator'])}@cached "
        f"{_fg_escape(ext['comment'])}// "
        f"{_fg_escape(ext['tag'])}TODO: "
        f"{_fg_escape(ext['comment'])}refactor this"
    )
    lines.append(_syntax_line(line3))

    # Diff preview
    lines.append("")
    diff_w = TOTAL_WIDTH // 2
    add_text = "  + added line".ljust(diff_w)
    del_text = "  - deleted line".ljust(diff_w)
    lines.append(
        f"  {_bg_escape(ext['diff_add_bg'])}{_fg_escape(ext['diff_add'])}"
        f"{add_text}{RESET}"
        f"{_bg_escape(ext['diff_delete_bg'])}{_fg_escape(ext['diff_delete'])}"
        f"{del_text}{RESET}"
    )

    lines.append("")
    return "\n".join(lines)


def interactive_select(schemes: list[ColorScheme]) -> ColorScheme:
    """Display all palettes and prompt user to select one."""
    for i, scheme in enumerate(schemes, 1):
        print(preview_palette(scheme, i, len(schemes)))

    while True:
        try:
            choice = input(f"  Select palette (1-{len(schemes)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(schemes):
                return schemes[idx]
        except (ValueError, EOFError):
            pass
        print(f"  Please enter a number between 1 and {len(schemes)}")
