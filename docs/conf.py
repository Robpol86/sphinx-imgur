"""Sphinx configuration file."""
# pylint: disable=invalid-name
import time

from sphinx_imgur.imgur import DEFAULT_EXT, DEFAULT_SIZE, IMG_SRC_FORMAT, TARGET_FORMAT


# General configuration.
author = "Robpol86"
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
language = "en"
project = "sphinx-imgur"
pygments_style = "vs"
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


# https://sphinxext-opengraph.readthedocs.io/en/latest/#options
ogp_site_name = project
ogp_type = "website"
ogp_use_first_image = True
