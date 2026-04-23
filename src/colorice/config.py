"""TOML configuration for template mappings."""

import os
import tomllib
from dataclasses import dataclass, field

from .paths import default_config_path, default_template_dir


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

    template_dir: str = ""
    templates: list[TemplateMapping] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.template_dir:
            self.template_dir = default_template_dir()


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

    template_dir = data.get("general", {}).get("template_dir", "")

    templates = []
    for i, t in enumerate(data.get("templates", [])):
        name = t.get("name", f"template-{i}")
        if "input" not in t:
            raise ValueError(
                f"Template '{name}' in {config_path} is missing required 'input' field."
            )
        if "output" not in t:
            raise ValueError(
                f"Template '{name}' in {config_path} is missing required 'output' field."
            )
        templates.append(
            TemplateMapping(
                name=name,
                input=os.path.expanduser(t["input"]),
                output=os.path.expanduser(t["output"]),
                hook=t.get("hook"),
            )
        )

    return ColoriceConfig(
        template_dir=os.path.expanduser(template_dir) if template_dir else "",
        templates=templates,
    )
