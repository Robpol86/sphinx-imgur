"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

from __future__ import print_function

from sphinx.application import SphinxError

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '1.0.0'


class ImgurError(SphinxError):
    """Non-configuration error. Raised when directive has bad options."""

    category = 'Imgur option error'
