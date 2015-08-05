"""Interfaces with the Imgur REST API and the Sphinx cache."""

import json
import time
import urllib


def purge_orphaned_entries(env, docname):
    """Remove orphaned Imgur cached entries from the Sphinx build environment. They are no longer used anywhere.

    :param env: Sphinx build environment.
    :param str docname: Sphinx document name being removed.
    """
    if not hasattr(env, 'imgur_api_cache'):
        return

    # First remove the docname from all imgur_api_cache entries.
    for imgur_id in [k for k, v in env.imgur_api_cache.items() if docname in v['_docnames']]:
        env.imgur_api_cache[imgur_id]['_docnames'].remove(docname)

    # Next prune albums with no docnames.
    for imgur_id in [k for k, v in env.imgur_api_cache.items() if k.startswith('a/') and not v['_docnames']]:
        env.imgur_api_cache.pop(imgur_id)

    # Finally prune images with BOTH no docnames and no albums.
    used_in_albums = {i for a in env.imgur_api_cache.values() for i in a['images']}
    for imgur_id in [k for k, v in env.imgur_api_cache.items() if k not in used_in_albums and not v['_docnames']]:
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
            env.imgur_api_cache[imgur_id] = dict(
                _docnames={docname},  # Set of Sphinx doc names using this ID.
                _mod_time=0,  # Epoch.
                description='',
                images=set(),  # Set of image IDs (populated in albums only).
                title='',
            )
        elif docname not in env.imgur_api_cache[imgur_id]['_docnames']:
            env.imgur_api_cache[imgur_id]['_docnames'].add(docname)


def query_imgur_api(env, client_id, ttl, response):
    """Refresh cache by querying the Imgur API.

    Album API queries returns metadata of all images. If one of those images is also used in the Sphinx documentation
    then there is no need to issue a second API query when we already have the data.

    :param env: Sphinx persistent build environment object.
    :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
    :param int ttl: Number of seconds cache entries can age before being considered expired.
    :param dict response: Use this dict instead of actually querying the API (for testing).
    """
    return  # TODO
    url_base = 'https://api.imgur.com/3/{aoi}/{id}'
    for imgur_id, data in sorted(env.imgur_api_cache.items(), key=lambda i: (0, i) if i[0][:2] == 'a/' else (1, i)):
        if time.time() - data['_mod_time'] < ttl:
            continue
        if response:
            raise NotImplementedError
        if imgur_id.startswith('a/'):
            url = url_base.format(aoi='album', id=imgur_id[2:])
        else:
            url = url_base.format(aoi='image', id=imgur_id)
        request = urllib.request.Request(url)
        request.add_header('Authorization', 'Client-ID {}'.format(client_id))
        handle = urllib.request.urlopen(request)
        raw_json = handle.read(409600)
        response = json.loads(raw_json.decode('utf-8'))['data']
        data['description'] = response['description']
        data['title'] = response['title']
        for image in response.get('images', ()):
            image_data = env.imgur_api_cache[image['id']]
            image_data['description'] = image['description']
            image_data['title'] = image['title']
            image_data['_mod_time'] = int(time.time())
        data['_mod_time'] = int(time.time())
