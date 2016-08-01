"""Sphinx configuration file."""

import os
import time
from subprocess import check_output

SETUP = os.path.join(os.path.dirname(__file__), '..', 'setup.py')


# General configuration.
author = check_output([SETUP, '--author']).strip().decode('ascii')
copyright = '{}, {}'.format(time.strftime('%Y'), author)
master_doc = 'index'
project = check_output([SETUP, '--name']).strip().decode('ascii')
pygments_style = 'friendly'
release = version = check_output([SETUP, '--version']).strip().decode('ascii')
templates_path = ['_templates']
extensions = list()


# Options for HTML output.
html_context = dict(
    conf_py_path='/docs/',
    display_github=True,
    github_repo=os.environ.get('TRAVIS_REPO_SLUG', '/' + project).split('/', 1)[1],
    github_user=os.environ.get('TRAVIS_REPO_SLUG', 'robpol86/').split('/', 1)[0],
    github_version=os.environ.get('TRAVIS_BRANCH', 'master'),
    source_suffix='.rst',
)
html_copy_source = False
html_favicon = 'favicon.ico'
html_theme = 'sphinx_rtd_theme'
html_title = project


# imgur
extensions.append('sphinxcontrib.imgur')
imgur_client_id = '13d3c73555f2190'
