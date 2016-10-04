"""Interface with Sphinx.

Note about the two env variables: app.builder.env and just env are the same. I use them interchangeably for linting
purposes.
"""

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
    for node in (n for c in (ImgurDescriptionNode, ImgurTitleNode) for n in doctree.traverse(c)):
        if node.imgur_id.startswith('a/'):
            albums.add(node.imgur_id[2:])
        else:
            images.add(node.imgur_id)
    initialize(app.builder.env.imgur_album_cache, app.builder.env.imgur_image_cache, albums, images)


def event_env_merge_info(app, env, _, other):
    """Called by Sphinx during phase 3 (resolving).

    * Combine child process' modified env with this one.

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

    # Merge updated items.
    for cache, other in ((album_cache, other_album_cache), (image_cache, other_image_cache)):
        for imgur_id, instance in ((k, v) for k, v in other.items() if k in cache):
            if instance.mod_time > cache[imgur_id].mod_time:
                cache[imgur_id] = instance

    # Add new items.
    album_cache.update({k: v for k, v in other_album_cache.items() if k not in album_cache})
    image_cache.update({k: v for k, v in other_image_cache.items() if k not in image_cache})


def event_env_updated(app, env):
    """Called by Sphinx during phase 3 (resolving).

    * Find Imgur IDs that need to be queried.
    * Query the Imgur API for new/outdated albums/images.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param sphinx.environment.BuildEnvironment env: Sphinx build environment.
    """
    client_id = app.config['imgur_client_id']
    ttl = app.config['imgur_api_cache_ttl']
    album_whitelist = set()
    image_whitelist = set()

    # Build whitelist of Imgur IDs in just new/updated docs.
    for doctree in (env.get_doctree(n) for n in app.builder.get_outdated_docs()):
        for node in (n for c in (ImgurDescriptionNode, ImgurTitleNode) for n in doctree.traverse(c)):
            if node.imgur_id.startswith('a/'):
                album_whitelist.add(node.imgur_id[2:])
            else:
                image_whitelist.add(node.imgur_id)

    # Update the cache only if an added/changed doc has an Imgur album/image.
    album_cache = app.builder.env.imgur_album_cache
    image_cache = app.builder.env.imgur_image_cache
    if album_whitelist or image_whitelist:
        update_cache(album_cache, image_cache, app, client_id, ttl, album_whitelist, image_whitelist)
        prune_cache(album_cache, image_cache, app)


def event_doctree_resolved(app, doctree, _):
    """Called by Sphinx after phase 3 (resolving).

    * Replace Imgur nodes with data from the Sphinx cache.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    :param _: Not used.
    """
    for node in (n for c in (ImgurDescriptionNode, ImgurTitleNode) for n in doctree.traverse(c)):
        if node.imgur_id.startswith('a/'):
            text = getattr(app.env.imgur_album_cache[node.imgur_id[2:]], node.key)
        else:
            text = getattr(app.env.imgur_image_cache[node.imgur_id], node.key)
        node.replace_self([docutils.nodes.Text(text)])


def setup(app, version):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str version: Version of sphinxcontrib-imgur.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('imgur_api_cache_ttl', 172800, False)
    app.add_config_value('imgur_client_id', None, False)
    app.add_config_value('imgur_hide_post_details', False, True)

    app.connect('env-before-read-docs', event_before_read_docs)
    app.connect('doctree-read', event_doctree_read)
    app.connect('env-merge-info', event_env_merge_info)
    app.connect('env-updated', event_env_updated)
    app.connect('doctree-resolved', event_doctree_resolved)

    return dict(parallel_read_safe=True, version=version)
