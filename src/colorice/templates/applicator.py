"""Template application orchestrator.

Applies a color scheme to all configured templates, writes rendered
output, and runs optional post-apply hooks.
"""

import os
import subprocess
import sys

from colorice.config import ColoriceConfig
from colorice.scheme import ColorScheme
from colorice.templates.pywal_compat import apply_template


def apply_all_templates(
    scheme: ColorScheme,
    config: ColoriceConfig,
    dry_run: bool = False,
    no_hooks: bool = False,
    quiet: bool = False,
) -> list[str]:
    """Apply scheme to all configured templates.

    Args:
        scheme: Color scheme to apply.
        config: Configuration with template mappings.
        dry_run: If True, render without writing files.
        no_hooks: If True, skip post-apply hooks.
        quiet: If True, suppress status output.

    Returns:
        List of output paths that were written (empty if dry_run).
    """
    written: list[str] = []

    for mapping in config.templates:
        template_path = os.path.join(config.template_dir, mapping.input)

        if not os.path.isfile(template_path):
            print(
                f"  Warning: template not found: {template_path} ({mapping.name})",
                file=sys.stderr,
            )
            continue

        try:
            rendered = apply_template(
                scheme, template_path, mapping.output, dry_run=dry_run
            )
        except Exception as e:
            print(
                f"  Warning: failed to render {mapping.name}: {e}",
                file=sys.stderr,
            )
            continue

        if dry_run:
            if not quiet:
                print(f"  [dry-run] {mapping.name} → {mapping.output}")
                print(rendered)
        else:
            written.append(mapping.output)
            if not quiet:
                print(f"  Applied {mapping.name} → {mapping.output}")

        # Run hook
        if mapping.hook and not no_hooks and not dry_run:
            try:
                result = subprocess.run(
                    mapping.hook,
                    shell=True,
                    timeout=10,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0 and not quiet:
                    print(
                        f"  Warning: hook for {mapping.name} failed: "
                        f"{result.stderr.strip()}",
                        file=sys.stderr,
                    )
            except subprocess.TimeoutExpired:
                print(
                    f"  Warning: hook for {mapping.name} timed out",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"  Warning: hook for {mapping.name} error: {e}",
                    file=sys.stderr,
                )

    return written
