"""Sphinx configuration file."""

# pylint: disable=invalid-name

import time
from pathlib import Path

import toml

from sphinx_imgur.imgur import DEFAULT_EXT, DEFAULT_SIZE, IMG_SRC_FORMAT, TARGET_FORMAT

PYPROJECT = toml.loads(Path(__file__).parent.parent.joinpath("pyproject.toml").read_text(encoding="utf8"))


# General configuration.
author = PYPROJECT["tool"]["poetry"]["authors"][0].split()[0]
copyright = f'{time.strftime("%Y")}, {author}'  # pylint: disable=redefined-builtin  # noqa
html_last_updated_fmt = f"%c {time.tzname[time.localtime().tm_isdst]}"
exclude_patterns = []
extensions = [
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io
    "sphinx_imgur.imgur",
    "sphinx_panels",  # https://sphinx-panels.readthedocs.io
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io
]
project = PYPROJECT["tool"]["poetry"]["name"]
pygments_style = "sphinx"
rst_epilog = f"""
.. |LABEL_DEFAULT_EXT| replace:: :guilabel:`{DEFAULT_EXT}`
.. |LABEL_DEFAULT_SIZE| replace:: :guilabel:`{DEFAULT_SIZE}`
.. |LABEL_IMG_SRC_FORMAT| replace:: :guilabel:`{IMG_SRC_FORMAT}`
.. |LABEL_TARGET_FORMAT| replace:: :guilabel:`{TARGET_FORMAT}`
.. |LABEL_HIDE_POST_DETAILS| replace:: :guilabel:`False`
"""


# Options for HTML output.
html_copy_source = False
html_theme = "sphinx_rtd_theme"
