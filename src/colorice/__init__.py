"""Colorice — Generate terminal color schemes from wallpaper images."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("colorice")
except PackageNotFoundError:
    __version__ = "0.1.0"  # fallback for dev/editable installs
