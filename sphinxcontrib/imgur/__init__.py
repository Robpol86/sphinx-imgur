"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

import docutils.nodes

from sphinxcontrib.imgur.api import get_imgur_ids_from_doctree, query_imgur_api, queue_new_imgur_ids
from sphinxcontrib.imgur.directives import ImgurEmbedDirective
from sphinxcontrib.imgur.nodes import ImgurDescriptionNode, ImgurEmbedNode, ImgurJavaScriptNode, ImgurTitleNode
from sphinxcontrib.imgur.roles import imgur_role

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '1.0.0'


def event_doctree_read(app, doctree):
    """Event handler that adds new Imgur IDs to the cache.

    Called once for each Sphinx document.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    """
    if not hasattr(app.builder.env, 'imgur_api_cache'):
        app.builder.env.imgur_api_cache = dict()

    imgur_ids = get_imgur_ids_from_doctree(doctree)
    if not imgur_ids:
        return
    queue_new_imgur_ids(app.builder.env.imgur_api_cache, imgur_ids)


def event_env_updated(app, env):
    """Event handler that queries the Imgur API and updates the Sphinx cache.

    Called once for the entire sphinx-build session.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param sphinx.environment.BuildEnvironment env: Sphinx build environment.
    """
    client_id = app.config['imgur_client_id']
    ttl = app.config['imgur_api_cache_ttl']
    response = app.config['imgur_api_test_response']
    query_imgur_api(app, env, client_id, ttl, response)


def event_doctree_resolved(app, doctree, _):
    """Event handler that replaces temporary Imgur rst nodes with data from the Sphinx cache.

    Called once for each Sphinx document.

    This final Imgur event is called after cache is pruned and updated with API queries. This function is called once
    for each Sphinx document.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    """
    # Handle description and title roles.
    for node_class, key in ((ImgurDescriptionNode, 'description'), (ImgurTitleNode, 'title')):
        for node in doctree.traverse(node_class):
            imgur_id = node.imgur_id
            text = app.env.imgur_api_cache[imgur_id][key]
            node.replace_self([docutils.nodes.Text(text)])


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('imgur_api_cache_ttl', 172800, False)
    app.add_config_value('imgur_api_test_response', None, False)
    app.add_config_value('imgur_client_id', None, False)
    app.add_config_value('imgur_hide_post_details', False, True)

    app.add_directive('imgur-embed', ImgurEmbedDirective)
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.visit, ImgurEmbedNode.depart))
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.visit, ImgurJavaScriptNode.depart))
    app.add_role('imgur-description', imgur_role)
    app.add_role('imgur-title', imgur_role)

    app.connect('doctree-read', event_doctree_read)
    app.connect('doctree-resolved', event_doctree_resolved)
    app.connect('env-updated', event_env_updated)
    return dict(parallel_read_safe=False, version=__version__)
