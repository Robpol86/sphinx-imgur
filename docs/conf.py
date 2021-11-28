"""Sphinx configuration file."""

import os
import sys
import time


# General configuration.
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
author = "@Robpol86"
copyright = "{}, {}".format(time.strftime("%Y"), author)
master_doc = "index"
project = "sphinx-imgur"
pygments_style = "friendly"
release = version = "2.0.1"
templates_path = ["_templates"]
extensions = list()


# Options for HTML output.
html_context = dict(
    conf_py_path="/docs/",
    display_github=True,
    github_repo=os.environ.get("TRAVIS_REPO_SLUG", "/" + project).split("/", 1)[1],
    github_user=os.environ.get("TRAVIS_REPO_SLUG", "robpol86/").split("/", 1)[0],
    github_version=os.environ.get("TRAVIS_BRANCH", "master"),
    source_suffix=".rst",
)
html_copy_source = False
html_favicon = "favicon.ico"
html_theme = "sphinx_rtd_theme"
html_title = project


# imgur
extensions.append("sphinx_imgur.imgur")
