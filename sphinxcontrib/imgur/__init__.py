"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

from sphinxcontrib.imgur.directives import ImgurEmbedDirective
from sphinxcontrib.imgur.nodes import ImgurEmbedNode, ImgurJavaScriptNode

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '0.1.0'


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('imgur_hide_post_details', False, True)
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.visit, ImgurJavaScriptNode.depart))
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.visit, ImgurEmbedNode.depart))
    app.add_directive('imgur-embed', ImgurEmbedDirective)
    return dict(version=__version__)
