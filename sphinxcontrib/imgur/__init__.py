"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

from sphinxcontrib.imgur import sphinx_api
from sphinxcontrib.imgur.directives import ImgurEmbedDirective
from sphinxcontrib.imgur.nodes import ImgurEmbedNode, ImgurJavaScriptNode
from sphinxcontrib.imgur.roles import imgur_role

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '1.0.0'


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_directive('imgur-embed', ImgurEmbedDirective)
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.visit, ImgurEmbedNode.depart))
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.visit, ImgurJavaScriptNode.depart))
    app.add_role('imgur-description', imgur_role)
    app.add_role('imgur-title', imgur_role)

    return sphinx_api.setup(app, __version__)
