"""Copy bundled default templates to the user's template directory.

Templates are never overwritten — user edits are always preserved.
"""

import importlib.resources
import os
import shutil


def install_default_templates(template_dir: str, quiet: bool = False) -> list[str]:
    """Copy bundled templates to template_dir, skipping existing files.

    Returns list of newly installed template names.
    """
    os.makedirs(template_dir, exist_ok=True)

    installed = []
    skipped = []
    data_pkg = importlib.resources.files("colorice.data.templates")

    for resource in data_pkg.iterdir():
        name = resource.name
        dest = os.path.join(template_dir, name)

        if os.path.isfile(dest):
            skipped.append(name)
            continue  # never overwrite user edits

        with importlib.resources.as_file(resource) as src_path:
            shutil.copy2(src_path, dest)
        installed.append(name)

    if not quiet:
        if installed:
            print(f"  Installed to {template_dir}:")
            for name in installed:
                print(f"    + {name}")
        if skipped:
            print(f"  Already exist (skipped):")
            for name in skipped:
                print(f"    ~ {name}")
        if not installed and not skipped:
            print(f"  No templates found in package.")

    return installed
