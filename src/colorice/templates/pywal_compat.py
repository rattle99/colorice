"""Pywal-compatible template engine.

Reads templates with {color0}..{color15}, {background}, etc. placeholders
and performs substitution. Supports pywal format modifiers (.strip, .rgb, etc.)
and colorice color manipulation filters (.lighten_20, .darken_15, etc.).
"""

import os
import re

from colorice.scheme import ColorScheme
from colorice.templates.variables import build_variables

# Matches {placeholder} but not escaped {{ or }}
_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_.]*)\}")


def render(scheme: ColorScheme, template_content: str) -> str:
    """Render a template string by substituting color variables.

    Placeholders like {color0}, {background.strip}, {color4.lighten_20}
    are replaced with their resolved values. Unknown placeholders are
    left unchanged. Escaped braces {{ and }} become literal { and }.
    """
    variables = build_variables(scheme, template_content)

    # Temporarily replace escaped braces so they're not matched
    content = template_content.replace("{{", "\x00LBRACE\x00")
    content = content.replace("}}", "\x00RBRACE\x00")

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in variables:
            return variables[key]
        return match.group(0)  # leave unknown placeholders unchanged

    content = _PLACEHOLDER_RE.sub(_replace, content)

    # Restore escaped braces as literals
    content = content.replace("\x00LBRACE\x00", "{")
    content = content.replace("\x00RBRACE\x00", "}")

    return content


def apply_template(
    scheme: ColorScheme,
    template_path: str,
    output_path: str,
    dry_run: bool = False,
) -> str:
    """Read a template file, render it, and write the output.

    Args:
        scheme: Color scheme to apply.
        template_path: Path to the template file.
        output_path: Path to write the rendered output.
        dry_run: If True, return rendered content without writing.

    Returns:
        The rendered content.
    """
    with open(template_path) as f:
        template_content = f.read()

    rendered = render(scheme, template_content)

    if not dry_run:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered)

    return rendered
