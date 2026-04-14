"""Placeholder template layer for applying schemes to tool configs."""

from abc import ABC, abstractmethod

from ..scheme import ColorScheme


class TemplateEngine(ABC):
    """Base class for template engines.

    Future: apply color schemes to app configs (kitty, i3, polybar, etc.)
    via template files with placeholders.
    """

    @abstractmethod
    def apply(self, scheme: ColorScheme, template_path: str, output_path: str) -> None:
        """Apply a color scheme to a template, writing the result to output_path."""
        ...
