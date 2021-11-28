"""Tests."""
import subprocess


def test_version():
    """Verify multi-sourced versions are synchronized."""
    # Get version from Poetry.
    output = subprocess.check_output(["poetry", "version", "--no-interaction"]).strip()
    version_poetry = output.split()[1].decode("utf8")

    # Get version from project.
    output = subprocess.check_output(
        ["poetry", "run", "python", "-c", "from sphinx_imgur import __version__; print(__version__)"]
    ).strip()
    version_project = output.decode("utf8")

    assert version_poetry == version_project
