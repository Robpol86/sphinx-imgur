"""Sphinx configuration file."""

import os
import sys
import time

import sphinx_rtd_theme

sys.path.append(os.path.abspath('..'))


# General configuration.
author = 'Robpol86'
copyright = '{}, {}'.format(time.strftime('%Y'), author)
exclude_patterns = ['_build']
extensions = ['sphinxcontrib.imgur']
master_doc = 'index'
nitpicky = True
project = 'sphinxcontrib-imgur'
release = '1.0'
templates_path = ['_templates']
version = release


# Options for HTML output.
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_title = project


# Options for extensions.
imgur_client_id = '13d3c73555f2190'


# Enable the `confval` directive.
def setup(app):
    """Called by Sphinx."""
    app.add_object_type('confval', 'confval', objname='configuration value', indextemplate='pair: %s; config value')
