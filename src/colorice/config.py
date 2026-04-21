"""TOML configuration for template mappings."""

import os
import tomllib
from dataclasses import dataclass, field


@dataclass
class TemplateMapping:
    """A single template: input file, output path, optional hook."""

    name: str
    input: str
    output: str
    hook: str | None = None


@dataclass
class ColoriceConfig:
    """Top-level configuration."""

    template_dir: str = "~/.config/colorice/templates"
    templates: list[TemplateMapping] = field(default_factory=list)


def default_config_path() -> str:
    """Default config file location."""
    return os.path.expanduser("~/.config/colorice/config.toml")


def load_config(path: str | None = None) -> ColoriceConfig:
    """Load configuration from TOML file.

    Returns default config (empty template list) if file doesn't exist.
    Raises ValueError on malformed TOML.
    """
    config_path = path or default_config_path()
    config_path = os.path.expanduser(config_path)

    if not os.path.isfile(config_path):
        return ColoriceConfig()

    with open(config_path, "rb") as f:
        try:
            data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid config file {config_path}: {e}") from e

    template_dir = data.get("general", {}).get(
        "template_dir", "~/.config/colorice/templates"
    )

    templates = []
    for t in data.get("templates", []):
        templates.append(
            TemplateMapping(
                name=t.get("name", "unnamed"),
                input=t["input"],
                output=os.path.expanduser(t["output"]),
                hook=t.get("hook"),
            )
        )

    return ColoriceConfig(
        template_dir=os.path.expanduser(template_dir),
        templates=templates,
    )
