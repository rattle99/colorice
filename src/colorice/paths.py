"""XDG Base Directory compliant path resolution."""

import os


def _xdg_dir(env_var: str, default_suffix: str) -> str:
    """Resolve an XDG base directory, falling back to the default."""
    xdg = os.environ.get(env_var)
    if xdg:
        return xdg
    return os.path.join(os.path.expanduser("~"), default_suffix)


def config_dir() -> str:
    """$XDG_CONFIG_HOME/colorice — user-editable config and templates."""
    return os.path.join(_xdg_dir("XDG_CONFIG_HOME", ".config"), "colorice")


def data_dir() -> str:
    """$XDG_DATA_HOME/colorice — generated schemes and saved themes."""
    return os.path.join(_xdg_dir("XDG_DATA_HOME", ".local/share"), "colorice")


def cache_dir() -> str:
    """$XDG_CACHE_HOME/colorice — disposable cached data."""
    return os.path.join(_xdg_dir("XDG_CACHE_HOME", ".cache"), "colorice")


def default_config_path() -> str:
    """Default config.toml location."""
    return os.path.join(config_dir(), "config.toml")


def default_template_dir() -> str:
    """Default template directory."""
    return os.path.join(config_dir(), "templates")


def default_output_path() -> str:
    """Default colors.json output location."""
    return os.path.join(data_dir(), "colors.json")
