"""Sphinx extension that embeds Imgur images and albums in documents.

https://sphinx-imgur.readthedocs.io
https://github.com/Robpol86/sphinx-imgur
https://pypi.org/project/sphinx-imgur
"""
from typing import Dict

from sphinx.application import Sphinx

from sphinx_imgur import __version__
from sphinx_imgur.directives import ImgurEmbedDirective, ImgurImageDirective
from sphinx_imgur.nodes import ImgurEmbedNode, ImgurImageNode, ImgurJavaScriptNode


def event_doctree_resolved(__, doctree, _):  # pylint: disable=invalid-name
    """Called by Sphinx after phase 3 (resolving).

    * Call finalizer for ImgurImageNode nodes.

    :param docutils.nodes.document doctree: Tree of docutils nodes.
    :param _: Not used.
    """
    for node in doctree.traverse(ImgurImageNode):
        node.finalize()


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    """
    app.add_config_value("imgur_api_cache_ttl", 172800, False)
    app.add_config_value("imgur_client_id", None, False)
    app.add_config_value("imgur_hide_post_details", False, True)
    app.add_config_value("imgur_target_default_gallery", False, True)
    app.add_config_value("imgur_target_default_largest", False, True)
    app.add_config_value("imgur_target_default_page", False, True)

    app.add_directive("imgur-embed", ImgurEmbedDirective)
    app.add_directive("imgur-image", ImgurImageDirective)
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.visit, ImgurEmbedNode.depart))
    app.add_node(ImgurImageNode, html=(ImgurImageNode.visit, ImgurImageNode.depart))
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.visit, ImgurJavaScriptNode.depart))

    app.connect("doctree-resolved", event_doctree_resolved)

    return dict(version=__version__)
