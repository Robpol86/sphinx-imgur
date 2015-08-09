"""Interfaces with the Imgur REST API and the Sphinx cache."""

import inspect
import json
import re
import time

try:
    import urllib.request as urllib_request
except ImportError:
    import urllib2 as urllib_request

from sphinx.errors import ExtensionError

from sphinxcontrib.imgur import nodes


def get_imgur_ids_from_doctree(doctree):
    """Return a set of Imgur IDs mentioned in API-enabled nodes in a specific document.

    :param doctree: Tree of docutils nodes.

    :return: Set of Imgur IDs.
    :rtype: set
    """
    imgur_ids = set()
    for node_class in (c for c in vars(nodes).values() if hasattr(c, 'IMGUR_API') and c.IMGUR_API):
        for node in doctree.traverse(node_class):
            imgur_ids.add(node.imgur_id)
    return imgur_ids


def get_targeted_ids(app, env):
    """Find Imgur IDs in API-enabled nodes in changed/added documents.

    :param app: Sphinx application object.
    :param env: Sphinx persistent build environment object.

    :return: Set of Imgur IDs.
    :rtype: set
    """
    targeted_ids = set()
    for docname in app.builder.get_outdated_docs():
        doctree = env.get_doctree(docname)
        imgur_ids = get_imgur_ids_from_doctree(doctree)
        targeted_ids |= imgur_ids
    return targeted_ids


def queue_new_imgur_ids(env, imgur_ids):
    """Add new image/album IDs to the cache.

    New entries have a _mod_time of 0, which makes them expired. query_imgur_api() will handle them.

    :param env: Sphinx persistent build environment object.
    :param set imgur_ids: Imgur image/album IDs to refresh.
    """
    for imgur_id in imgur_ids:
        if imgur_id not in env.imgur_api_cache:
            env.imgur_api_cache[imgur_id] = dict(
                _mod_time=0,  # Epoch.
                description='',
                images=set(),  # Set of image IDs (populated in albums only).
                title='',
            )


def query_imgur_api(app, env, client_id, ttl, response):
    """Refresh cache by querying the Imgur API.

    Album API queries returns metadata of all images. If one of those images is also used in the Sphinx documentation
    then there is no need to issue a second API query when we already have the data.

    :raises ExtensionError: if client_id is empty or invalid.

    :param app: Sphinx application object.
    :param env: Sphinx persistent build environment object.
    :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
    :param int ttl: Number of seconds cache entries can age before being considered expired.
    :param dict response: Use this dict instead of actually querying the API (for testing).
    """
    now = int(time.time())
    targeted_ids = get_targeted_ids(app, env)
    imgur_ids_expired = {k for k, v in env.imgur_api_cache.items() if k in targeted_ids and now - v['_mod_time'] > ttl}
    if not imgur_ids_expired:
        return

    # Optimize: if an image is in some album, request album instead of image.
    album_lookup = {i: k for k, v in env.imgur_api_cache.items() for i in v['images'] if i in imgur_ids_expired}
    for image, album in album_lookup.items():
        imgur_ids_expired.remove(image)
        imgur_ids_expired.add(album)
    imgur_ids = sorted(imgur_ids_expired, key=lambda i: (0, i) if i[:2] == 'a/' else (1, i))

    # Handle response argument if set.
    if response:
        for imgur_id in imgur_ids:
            app.debug('loading Imgur ID %s from imgur_api_test_response config dict.', imgur_id)
            env.imgur_api_cache[imgur_id]['description'] = response[imgur_id]['description']
            env.imgur_api_cache[imgur_id]['title'] = response[imgur_id]['title']
            if imgur_id.startswith('a/'):
                env.imgur_api_cache[imgur_id]['images'].clear()
            for response_image in response[imgur_id].get('images', ()) if imgur_id.startswith('a/') else ():
                if response_image['id'] not in env.imgur_api_cache:
                    queue_new_imgur_ids(env, {response_image['id']})
                env.imgur_api_cache[imgur_id]['images'].add(response_image['id'])
                env.imgur_api_cache[response_image['id']]['description'] = response_image['description']
                env.imgur_api_cache[response_image['id']]['title'] = response_image['title']
                env.imgur_api_cache[response_image['id']]['_mod_time'] = now
            env.imgur_api_cache[imgur_id]['_mod_time'] = now
        return

    if not client_id:
        raise ExtensionError('imgur_client_id config value must be set for Imgur API calls.')
    if not re.match(r'^[a-f0-9]{5,30}$', client_id):
        raise ExtensionError('imgur_client_id config value must be 5-30 lower case letters and numbers only.')

    # Actually hit the API.
    url_base = 'https://api.imgur.com/3/{aoi}/{id}'
    for imgur_id in imgur_ids:
        if imgur_id.startswith('a/'):
            url = url_base.format(aoi='album', id=imgur_id[2:])
        else:
            url = url_base.format(aoi='image', id=imgur_id)
        app.debug('querying %s', url)
        request = urllib_request.Request(url)
        request.add_header('Authorization', 'Client-ID {}'.format(client_id))
        try:
            handle = urllib_request.urlopen(request)
        except urllib_request.HTTPError as exc:
            exc_lineno = inspect.currentframe().f_back.f_lineno - 2
            app.warn('{}: {}'.format(exc.url, str(exc)), location='{}:{}'.format(__file__, exc_lineno))
            continue
        raw_json = handle.read(409600)
        raw_json_decoded = raw_json.decode('utf-8')
        app.debug2('Imgur API responded with: %s', raw_json_decoded)
        response = json.loads(raw_json_decoded)['data']

        env.imgur_api_cache[imgur_id]['description'] = response['description']
        env.imgur_api_cache[imgur_id]['title'] = response['title']
        if imgur_id.startswith('a/'):
            env.imgur_api_cache[imgur_id]['images'].clear()
        for response_image in response.get('images', ()) if imgur_id.startswith('a/') else ():
            if response_image['id'] not in env.imgur_api_cache:
                queue_new_imgur_ids(env, {response_image['id']})
            env.imgur_api_cache[imgur_id]['images'].add(response_image['id'])
            env.imgur_api_cache[response_image['id']]['description'] = response_image['description']
            env.imgur_api_cache[response_image['id']]['title'] = response_image['title']
            env.imgur_api_cache[response_image['id']]['_mod_time'] = now
        env.imgur_api_cache[imgur_id]['_mod_time'] = now
