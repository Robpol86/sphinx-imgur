"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

from sphinxcontrib.imgur import sphinx_api

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '2.0.1'


def setup(app):
    """Wrap sphinxcontrib.imgur.sphinx_api.setup.

    :param sphinx.application.Sphinx app: Sphinx application object.

    :returns: Extension metadata.
    :rtype: dict
    """
    return sphinx_api.setup(app, __version__)
