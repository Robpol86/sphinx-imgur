"""Interface with Sphinx.

Note about the two env variables: app.builder.env and just env are the same. I use them interchangeably for linting
purposes.
"""
from sphinxcontrib.imgur.directives import ImgurEmbedDirective, ImgurImageDirective
from sphinxcontrib.imgur.nodes import ImgurEmbedNode, ImgurImageNode, ImgurJavaScriptNode


def event_doctree_resolved(__, doctree, _):  # pylint: disable=invalid-name
    """Called by Sphinx after phase 3 (resolving).

    * Call finalizer for ImgurImageNode nodes.

    :param docutils.nodes.document doctree: Tree of docutils nodes.
    :param _: Not used.
    """
    for node in doctree.traverse(ImgurImageNode):
        node.finalize()


def setup(app, version):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str version: Version of sphinxcontrib-imgur.

    :returns: Extension metadata.
    :rtype: dict
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

    return dict(parallel_read_safe=True, version=version)
