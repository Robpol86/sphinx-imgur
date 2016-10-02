"""Interface with Sphinx."""

import re

import docutils.nodes
from sphinx.errors import ExtensionError

from sphinxcontrib.imgur.cache import initialize, prune_cache, update_cache
from sphinxcontrib.imgur.nodes import ImgurDescriptionNode, ImgurTitleNode

RE_CLIENT_ID = re.compile(r'^[a-f0-9]{5,30}$')


def event_before_read_docs(app, env, _):
    """Called by Sphinx before phase 1 (reading).

    * Verify config.
    * Initialize the cache dict before reading any docs with an empty dictionary if not exists.
    * Prune old/invalid data from cache.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param sphinx.environment.BuildEnvironment env: Sphinx build environment.
    :param _: Not used.
    """
    client_id = app.config['imgur_client_id']
    if not client_id:
        raise ExtensionError('imgur_client_id config value must be set for Imgur API calls.')
    if not RE_CLIENT_ID.match(client_id):
        raise ExtensionError('imgur_client_id config value must be 5-30 lower case hexadecimal characters only.')
    env.imgur_album_cache = initialize(getattr(env, 'imgur_album_cache', None), (), ())
    prune_cache(env.imgur_album_cache, app)


def event_doctree_read(app, doctree):
    """Called by Sphinx during phase 1 (reading).

    * Add new Imgur IDs to the cache.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    """
    albums, images = set(), set()
    for node in (n for c in (ImgurDescriptionNode, ImgurTitleNode) for n in doctree.traverse(c)):
        if node.imgur_id.startswith('a/'):
            albums.add(node.imgur_id[2:])
        else:
            images.add(node.imgur_id)
    initialize(app.builder.env.imgur_album_cache, albums, images)


def event_env_updated(app, env):
    """Called by Sphinx during phase 3 (resolving).

    * Find Imgur IDs that need to be queried.
    * Query the Imgur API for new/outdated albums/images.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param sphinx.environment.BuildEnvironment env: Sphinx build environment.
    """
    client_id = app.config['imgur_client_id']
    ttl = app.config['imgur_api_cache_ttl']
    whitelist = set()

    # Build whitelist of Imgur IDs in just new/updated docs.
    for doctree in (env.get_doctree(n) for n in app.builder.get_outdated_docs()):
        for node in (n for c in (ImgurDescriptionNode, ImgurTitleNode) for n in doctree.traverse(c)):
            whitelist.add(node.imgur_id.split('/')[-1])

    # Update the cache only if an added/changed doc has an Imgur album/image.
    if whitelist:
        update_cache(app.builder.env.imgur_album_cache, app, client_id, ttl, whitelist)
        prune_cache(app.builder.env.imgur_album_cache, app)


def event_doctree_resolved(app, doctree, _):
    """Called by Sphinx after phase 3 (resolving).

    * Replace Imgur nodes with data from the Sphinx cache.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    :param _: Not used.
    """
    for node in (n for c in (ImgurDescriptionNode, ImgurTitleNode) for n in doctree.traverse(c)):
        imgur_id = node.imgur_id.split('/')[-1]
        text = getattr(app.env.imgur_album_cache[imgur_id], node.key)
        node.replace_self([docutils.nodes.Text(text)])


def setup(app, version):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str version: Version of sphinxcontrib-imgur.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('imgur_api_cache_ttl', 172800, False)
    app.add_config_value('imgur_api_test_response_albums', None, False)
    app.add_config_value('imgur_api_test_response_images', None, False)
    app.add_config_value('imgur_client_id', None, False)
    app.add_config_value('imgur_hide_post_details', False, True)

    app.connect('env-before-read-docs', event_before_read_docs)
    app.connect('doctree-read', event_doctree_read)
    app.connect('env-updated', event_env_updated)
    app.connect('doctree-resolved', event_doctree_resolved)

    return dict(parallel_read_safe=False, version=version)
