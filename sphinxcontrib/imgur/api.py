"""Interfaces with the Imgur REST API and the Sphinx cache."""

DATA_MODEL = dict(
    _mod_time=0,  # Epoch.
    description='',
    images=(),  # Tuple of image IDs (populated in albums only).
    title='',
)


def discover_imgur_ids_used(doctree, node_classes):
    """Find Imgur image and album IDs used in all Sphinx documents.

    :param doctree: Tree of docutils nodes.
    :param node_classes: List of Imgur-related node classes to traverse.

    :return: Imgur IDs.
    :rtype: set
    """
    imgur_ids = set()
    for node in (n for c in node_classes for n in doctree.traverse(c)):
        if hasattr(node, 'imgur_id'):
            imgur_ids.add(node.imgur_id)
    return imgur_ids


def purge_orphaned_entries(env, used_ids):
    """Remove orphaned Imgur cached entries from the Sphinx build environment. They are no longer used anywhere.

    :param env: Sphinx persistent build environment object.
    :param set used_ids: Imgur image/album IDs still used in all documents.
    """
    if not hasattr(env, 'imgur_api_cache'):
        return

    # Handle albums first.
    for imgur_id, metadata in [(k, v) for k, v in env.imgur_api_cache.items() if k.startswith('a/')]:
        if imgur_id not in used_ids:
            env.imgur_api_cache.pop(imgur_id)

    # Handle images.
    used_in_albums = {i for a in env.imgur_api_cache.values() for i in a['images']}
    for imgur_id, metadata in [(k, v) for k, v in env.imgur_api_cache.items() if not k.startswith('a/')]:
        if imgur_id not in used_ids and imgur_id not in used_in_albums:
            env.imgur_api_cache.pop(imgur_id)


def queue_new_imgur_ids(env, used_ids):
    """Queue/schedule new album (starting with a/) or image IDs.

    New entries have a _mod_time of 0, which makes them expired. query_imgur_api() will handle them.

    :param env: Sphinx persistent build environment object.
    :param set used_ids: Imgur image/album IDs still used in all documents.
    """
    if not hasattr(env, 'imgur_api_cache'):
        env.imgur_api_cache = dict()
    for imgur_id in used_ids:
        if imgur_id not in env.imgur_api_cache:
            env.imgur_api_cache[imgur_id] = DATA_MODEL.copy()


def query_imgur_api(env, client_id, ttl):
    """Refresh cache by querying the Imgur API.

    Album API queries returns metadata of all images. If one of those images is also used in the Sphinx documentation
    then there is no need to issue a second API query when we already have the data.

    :param env: Sphinx persistent build environment object.
    :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
    :param int ttl: Number of seconds cache entries can age before being considered expired.
    """
    pass
