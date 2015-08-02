"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

import docutils.nodes

from sphinxcontrib.imgur import api, directives, nodes, roles

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '0.1.0'


def cleanup_imgur_cache(app, doctree):
    """Sphinx event handler. Prunes orphaned Imgur entries from Sphinx cache and queues new entries.

    :param app: Sphinx application object.
    :param doctree: Tree of docutils nodes.
    """
    # Get all Imgur IDs used.
    api_enabled_nodes_classes = [
        nodes.ImgurDescriptionNode,
        nodes.ImgurTitleNode,
    ]
    imgur_ids = api.discover_imgur_ids_used(doctree, api_enabled_nodes_classes)
    # Clean up persistent cache and queue new entries.
    api.purge_orphaned_entries(app.env, imgur_ids)
    api.queue_new_imgur_ids(app.env, imgur_ids)


def update_imgur_nodes(app, doctree, _):
    """Sphinx event handler. Replace temporary Imgur rst nodes with data from the Sphinx cache.

    This final Imgur event is called after cache is pruned and updated with API queries. This function is called once
    for each Sphinx document.

    :param app: Sphinx application object.
    :param doctree: Tree of docutils nodes.
    """
    # Handle description and title roles.
    for node_class, key in ((nodes.ImgurDescriptionNode, 'description'), (nodes.ImgurTitleNode, 'title')):
        for node in doctree.traverse(node_class):
            imgur_id = node.imgur_id
            text = app.env.imgur_api_cache[imgur_id][key]
            node.replace_self([docutils.nodes.Text(text)])


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('imgur_allow_html', False, True)
    app.add_config_value('imgur_api_cache_ttl', 172800, False)
    app.add_config_value('imgur_client_id', None, False)
    app.add_config_value('imgur_hide_post_details', False, True)
    app.add_directive('imgur-embed', directives.ImgurEmbedDirective)
    app.add_node(nodes.ImgurEmbedNode, html=(nodes.ImgurEmbedNode.visit, nodes.ImgurEmbedNode.depart))
    app.add_node(nodes.ImgurJavaScriptNode, html=(nodes.ImgurJavaScriptNode.visit, nodes.ImgurJavaScriptNode.depart))
    app.add_role('imgur-description', roles.imgur_role)
    app.add_role('imgur-title', roles.imgur_role)
    app.connect('doctree-read', cleanup_imgur_cache)
    app.connect('doctree-resolved', update_imgur_nodes)
    return dict(version=__version__)
