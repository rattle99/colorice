"""Tests for TOML configuration loading."""

import os
import tempfile

from colorice.config import ColoriceConfig, load_config


def test_missing_config_returns_defaults():
    """Non-existent config file should return default config."""
    config = load_config("/tmp/nonexistent_colorice_config.toml")
    assert isinstance(config, ColoriceConfig)
    assert config.templates == []


def test_load_minimal_config():
    """Config with just one template should load correctly."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[[templates]]
name = "kitty"
input = "kitty.conf"
output = "~/.config/kitty/colors.conf"
""")
        f.flush()
        config = load_config(f.name)

    os.unlink(f.name)
    assert len(config.templates) == 1
    assert config.templates[0].name == "kitty"
    assert config.templates[0].input == "kitty.conf"
    assert config.templates[0].hook is None


def test_load_full_config():
    """Config with all fields should load correctly."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[general]
template_dir = "~/my-templates"

[[templates]]
name = "kitty"
input = "kitty.conf"
output = "~/.config/kitty/colors.conf"
hook = "killall -USR1 kitty"

[[templates]]
name = "rofi"
input = "rofi.rasi"
output = "~/.config/rofi/colors.rasi"
""")
        f.flush()
        config = load_config(f.name)

    os.unlink(f.name)
    assert len(config.templates) == 2
    assert config.templates[0].hook == "killall -USR1 kitty"
    assert config.templates[1].hook is None
    assert config.template_dir == os.path.expanduser("~/my-templates")


def test_path_expansion():
    """~ in paths should be expanded."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[[templates]]
name = "test"
input = "test.conf"
output = "~/output/test.conf"
""")
        f.flush()
        config = load_config(f.name)

    os.unlink(f.name)
    assert "~" not in config.templates[0].output


def test_invalid_toml_raises():
    """Malformed TOML should raise ValueError."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("this is not valid toml [[[")
        f.flush()
        try:
            load_config(f.name)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    os.unlink(f.name)
