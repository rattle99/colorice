"""Copy bundled default templates and config to the user's directories.

Files are never overwritten — user edits are always preserved.
"""

import importlib.resources
import os
import shutil

from colorice.paths import default_config_path


def install_default_config(quiet: bool = False, force: bool = False) -> bool:
    """Copy bundled config.toml if one doesn't exist (or force-overwrite).

    Returns True if installed, False if skipped.
    """
    dest = default_config_path()
    if os.path.isfile(dest) and not force:
        if not quiet:
            print(f"  Config already exists: {dest}")
        return False

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    data_pkg = importlib.resources.files("colorice.data")
    config_resource = data_pkg.joinpath("config.toml")
    with importlib.resources.as_file(config_resource) as src_path:
        shutil.copy2(src_path, dest)

    if not quiet:
        action = "Reset" if force else "Installed"
        print(f"  {action} default config: {dest}")
        if not force:
            print("  Uncomment the templates you want to use.")

    return True


def install_default_templates(
    template_dir: str, quiet: bool = False, force: bool = False
) -> list[str]:
    """Copy bundled templates to template_dir, skipping existing files unless force.

    Returns list of newly installed/overwritten template names.
    """
    os.makedirs(template_dir, exist_ok=True)

    installed = []
    skipped = []
    data_pkg = importlib.resources.files("colorice.data.templates")

    for resource in data_pkg.iterdir():
        name = resource.name
        dest = os.path.join(template_dir, name)

        if os.path.isfile(dest) and not force:
            skipped.append(name)
            continue

        with importlib.resources.as_file(resource) as src_path:
            shutil.copy2(src_path, dest)
        installed.append(name)

    if not quiet:
        if installed:
            action = "Reset" if force else "Installed"
            print(f"  {action} templates to {template_dir}:")
            for name in installed:
                print(f"    + {name}")
        if skipped:
            print("  Already exist (skipped):")
            for name in skipped:
                print(f"    ~ {name}")
        if not installed and not skipped:
            print("  No templates found in package.")

    return installed
