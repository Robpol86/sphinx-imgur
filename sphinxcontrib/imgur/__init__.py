"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

from sphinxcontrib.imgur import directives, nodes

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
    app.add_directive('imgur-embed', directives.ImgurEmbedDirective)
    app.add_node(nodes.ImgurEmbedNode, html=(nodes.ImgurEmbedNode.visit, nodes.ImgurEmbedNode.depart))
    app.add_node(nodes.ImgurJavaScriptNode, html=(nodes.ImgurJavaScriptNode.visit, nodes.ImgurJavaScriptNode.depart))
    return dict(version=__version__)
