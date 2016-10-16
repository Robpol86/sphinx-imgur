"""Interface with Sphinx.

Note about the two env variables: app.builder.env and just env are the same. I use them interchangeably for linting
purposes.
"""

import re

import docutils.nodes
from sphinx.errors import ExtensionError

from sphinxcontrib.imgur.cache import initialize, prune_cache, update_cache
from sphinxcontrib.imgur.directives import ImgurEmbedDirective, ImgurImageDirective
from sphinxcontrib.imgur.nodes import ImgurEmbedNode, ImgurImageNode, ImgurJavaScriptNode, ImgurTextNode
from sphinxcontrib.imgur.roles import imgur_role

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

    imgur_album_cache = getattr(env, 'imgur_album_cache', None)
    imgur_image_cache = getattr(env, 'imgur_image_cache', None)
    env.imgur_album_cache, env.imgur_image_cache = initialize(imgur_album_cache, imgur_image_cache, (), ())
    prune_cache(env.imgur_album_cache, env.imgur_image_cache, app)


def event_doctree_read(app, doctree):
    """Called by Sphinx during phase 1 (reading).

    * Add new Imgur IDs to the cache.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    """
    albums, images = set(), set()
    for node in (n for c in (ImgurTextNode, ImgurImageNode) for n in doctree.traverse(c)):
        if node.album:
            albums.add(node.imgur_id)
        else:
            images.add(node.imgur_id)
    initialize(app.builder.env.imgur_album_cache, app.builder.env.imgur_image_cache, albums, images)


def event_env_merge_info(app, env, _, other):
    """Called by Sphinx during phase 3 (resolving).

    * Combine child process' modified env with this one. Only changes should be new Imgur IDs since cache update is done
      in event_env_updated() after everything is merged and we're back to one process.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param sphinx.environment.BuildEnvironment env: Sphinx build environment.
    :param _: Not used.
    :param sphinx.environment.BuildEnvironment other: Sphinx build environment from child process.
    """
    other_album_cache = getattr(other, 'imgur_album_cache', None)
    other_image_cache = getattr(other, 'imgur_image_cache', None)
    if not other_album_cache and not other_image_cache:
        return
    album_cache = app.builder.env.imgur_album_cache
    image_cache = app.builder.env.imgur_image_cache
    assert env  # Linting.

    # Merge items.
    album_cache.update(other_album_cache)
    image_cache.update(other_image_cache)


def event_env_updated(app, env):
    """Called by Sphinx during phase 3 (resolving).

    * Find Imgur IDs that need to be queried.
    * Query the Imgur API for new/outdated albums/images.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param sphinx.environment.BuildEnvironment env: Sphinx build environment.
    """
    client_id = app.config['imgur_client_id']
    ttl = app.config['imgur_api_cache_ttl']
    album_cache = app.builder.env.imgur_album_cache
    image_cache = app.builder.env.imgur_image_cache
    album_whitelist = {v.imgur_id for v in album_cache.values() if v.mod_time == 0}
    image_whitelist = {v.imgur_id for v in image_cache.values() if v.mod_time == 0}

    # Build whitelist of Imgur IDs in just new/updated docs.
    for doctree in (env.get_doctree(n) for n in app.builder.get_outdated_docs()):
        for node in (n for c in (ImgurTextNode, ImgurImageNode) for n in doctree.traverse(c)):
            if node.album:
                album_whitelist.add(node.imgur_id)
            else:
                image_whitelist.add(node.imgur_id)

    # Update the cache only if an added/changed doc has an Imgur album/image.
    if album_whitelist or image_whitelist:
        update_cache(album_cache, image_cache, app, client_id, ttl, album_whitelist, image_whitelist)
        prune_cache(album_cache, image_cache, app)


def event_doctree_resolved(app, doctree, _):
    """Called by Sphinx after phase 3 (resolving).

    * Replace Imgur text nodes with data from the Sphinx cache.
    * Call finalizer for ImgurImageNode nodes.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    :param _: Not used.
    """
    album_cache = app.builder.env.imgur_album_cache
    image_cache = app.builder.env.imgur_image_cache

    for node in doctree.traverse(ImgurTextNode):
        cache = album_cache if node.album else image_cache
        if node.name == 'imgur-description':
            text = cache[node.imgur_id].description
        else:
            text = cache[node.imgur_id].title
        node.replace_self([docutils.nodes.Text(text)])

    for node in doctree.traverse(ImgurImageNode):
        if node.album and not album_cache[node.imgur_id].cover_id:
            app.warn('Album cover Imgur ID for {} not available in local cache.'.format(node.imgur_id))
            node.replace_self([docutils.nodes.Text('')])
        else:
            node.finalize(album_cache, image_cache, lambda m: app.builder.env.warn_node(m, node))


def setup(app, version):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str version: Version of sphinxcontrib-imgur.

    :returns: Extension metadata.
    :rtype: dict
    """
    app.add_config_value('imgur_api_cache_ttl', 172800, False)
    app.add_config_value('imgur_client_id', None, False)
    app.add_config_value('imgur_hide_post_details', False, True)
    app.add_config_value('imgur_target_default_gallery', False, True)
    app.add_config_value('imgur_target_default_largest', False, True)
    app.add_config_value('imgur_target_default_page', False, True)

    app.add_directive('imgur-embed', ImgurEmbedDirective)
    app.add_directive('imgur-image', ImgurImageDirective)
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.visit, ImgurEmbedNode.depart))
    app.add_node(ImgurImageNode, html=(ImgurImageNode.visit, ImgurImageNode.depart))
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.visit, ImgurJavaScriptNode.depart))
    app.add_role('imgur-description', imgur_role)
    app.add_role('imgur-title', imgur_role)

    app.connect('env-before-read-docs', event_before_read_docs)
    app.connect('doctree-read', event_doctree_read)
    app.connect('env-merge-info', event_env_merge_info)
    app.connect('env-updated', event_env_updated)
    app.connect('doctree-resolved', event_doctree_resolved)

    return dict(parallel_read_safe=True, version=version)
