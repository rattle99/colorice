"""Tests for template application orchestrator."""

import os
import tempfile

from colorice.config import ColoriceConfig, TemplateMapping
from colorice.templates.applicator import apply_all_templates


def test_apply_single_template(sample_scheme):
    """Should render template and write output file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create template
        template_dir = os.path.join(tmpdir, "templates")
        os.makedirs(template_dir)
        template_path = os.path.join(template_dir, "test.conf")
        with open(template_path, "w") as f:
            f.write("bg={color0}\nfg={foreground}\n")

        output_path = os.path.join(tmpdir, "output.conf")
        config = ColoriceConfig(
            template_dir=template_dir,
            templates=[
                TemplateMapping(
                    name="test",
                    input="test.conf",
                    output=output_path,
                ),
            ],
        )

        written = apply_all_templates(sample_scheme, config, quiet=True)
        assert output_path in written
        assert os.path.isfile(output_path)

        with open(output_path) as f:
            content = f.read()
        assert "bg=#191724" in content
        assert "fg=#ecf0f1" in content


def test_missing_template_warns_no_crash(sample_scheme):
    """Missing template file should warn but not crash."""
    config = ColoriceConfig(
        template_dir="/tmp/nonexistent_dir",
        templates=[
            TemplateMapping(
                name="missing",
                input="nonexistent.conf",
                output="/tmp/out.conf",
            ),
        ],
    )

    written = apply_all_templates(sample_scheme, config, quiet=True)
    assert written == []


def test_dry_run_no_write(sample_scheme):
    """dry_run should not create the output file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = os.path.join(tmpdir, "templates")
        os.makedirs(template_dir)
        template_path = os.path.join(template_dir, "test.conf")
        with open(template_path, "w") as f:
            f.write("bg={color0}\n")

        output_path = os.path.join(tmpdir, "output.conf")
        config = ColoriceConfig(
            template_dir=template_dir,
            templates=[
                TemplateMapping(
                    name="test",
                    input="test.conf",
                    output=output_path,
                ),
            ],
        )

        written = apply_all_templates(sample_scheme, config, dry_run=True, quiet=True)
        assert written == []
        assert not os.path.isfile(output_path)


def test_hook_failure_no_crash(sample_scheme):
    """Hook that fails should warn but not abort."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = os.path.join(tmpdir, "templates")
        os.makedirs(template_dir)
        template_path = os.path.join(template_dir, "test.conf")
        with open(template_path, "w") as f:
            f.write("{color0}")

        output_path = os.path.join(tmpdir, "output.conf")
        config = ColoriceConfig(
            template_dir=template_dir,
            templates=[
                TemplateMapping(
                    name="test",
                    input="test.conf",
                    output=output_path,
                    hook="false",  # always fails
                ),
            ],
        )

        written = apply_all_templates(sample_scheme, config, quiet=True)
        assert output_path in written  # template still applied despite hook failure
