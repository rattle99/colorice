"""Pywal-compatible template engine (placeholder).

Reads pywal-style templates with {color0}..{color15}, {background}, etc.
and performs simple string substitution.
"""

from ..scheme import ColorScheme
from . import TemplateEngine


class PywalCompatEngine(TemplateEngine):
    """Apply pywal-style templates.

    Template placeholders:
        {color0} .. {color15}
        {background}, {foreground}, {cursor}
    """

    def apply(self, scheme: ColorScheme, template_path: str, output_path: str) -> None:
        with open(template_path) as f:
            content = f.read()

        # Replace color placeholders
        for i, color in enumerate(scheme.colors):
            content = content.replace(f"{{color{i}}}", color)

        # Replace special placeholders
        content = content.replace("{background}", scheme.background)
        content = content.replace("{foreground}", scheme.foreground)
        content = content.replace("{cursor}", scheme.cursor)

        with open(output_path, "w") as f:
            f.write(content)
