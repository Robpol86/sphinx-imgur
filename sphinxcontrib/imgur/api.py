"""Interfaces with the Imgur REST API and the Sphinx cache."""

DATA_MODEL = dict(
    _docnames=(),  # Tuple of Sphinx doc names using this ID.
    _mod_time=0,  # Epoch.
    description='',
    images=(),  # Tuple of image IDs (populated in albums only).
    title='',
)


def purge_orphaned_entries(env, docname):
    """Remove orphaned Imgur cached entries from the Sphinx build environment. They are no longer used anywhere.

    :param env: Sphinx build environment.
    :param str docname: Sphinx document name being removed.
    """
    if not hasattr(env, 'imgur_api_cache'):
        return

    imgur_ids_used_by_doc = {k for k, v in env.imgur_api_cache.items() if docname in v['_docnames']}

    # First remove the docname from all imgur_api_cache entries.
    for imgur_id in imgur_ids_used_by_doc:
        docnames = env.imgur_api_cache[imgur_id]['_docnames']
        env.imgur_api_cache[imgur_id]['_docnames'] = tuple(d for d in docnames if d != docname)

    # Next prune albums with no docnames.
    for imgur_id in (i for i in imgur_ids_used_by_doc if i.startswith('a/')):
        if not env.imgur_api_cache[imgur_id]['_docnames']:
            env.imgur_api_cache.pop(imgur_id)

    # Finally prune images with BOTH no docnames and no albums.
    used_in_albums = {i for a in env.imgur_api_cache.values() for i in a['images']}
    for imgur_id in (i for i in imgur_ids_used_by_doc if not i.startswith('a/')):
        if not env.imgur_api_cache[imgur_id]['_docnames'] and imgur_id not in used_in_albums:
            env.imgur_api_cache.pop(imgur_id)


def queue_new_imgur_ids_or_add_docname(env, imgur_ids, docname):
    """Add new image/album IDs to the cache or add the docname to existing cache entries.

    New entries have a _mod_time of 0, which makes them expired. query_imgur_api() will handle them.

    :param env: Sphinx persistent build environment object.
    :param set imgur_ids: Imgur image/album IDs to refresh.
    :param str docname: Sphinx document name being removed.
    """
    for imgur_id in imgur_ids:
        if imgur_id not in env.imgur_api_cache:
            env.imgur_api_cache[imgur_id] = DATA_MODEL.copy()
        elif docname not in env.imgur_api_cache[imgur_id]['_docnames']:
            docnames = set(env.imgur_api_cache[imgur_id]['_docnames'])
            docnames.add(docname)
            env.imgur_api_cache[imgur_id]['_docnames'] = tuple(docnames)


def query_imgur_api(env, client_id, ttl):
    """Refresh cache by querying the Imgur API.

    Album API queries returns metadata of all images. If one of those images is also used in the Sphinx documentation
    then there is no need to issue a second API query when we already have the data.

    :param env: Sphinx persistent build environment object.
    :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
    :param int ttl: Number of seconds cache entries can age before being considered expired.
    """
    pass
