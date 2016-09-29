"""Manage Imgur cache."""

from sphinxcontrib.imgur.imgur_api import Album, APIError, Image


def initialize(cache, albums, images):
    """Instantiate Album or Image instances not already in cache.

    :param dict cache: Update this. Keys are Imgur IDs, values are Image or Album instances.
    :param iter albums: List of album Imgur IDs.
    :param iter images: List of image Imgur IDs.

    :return: Same cache dictionary from parameters.
    :rtype: dict
    """
    if not hasattr(cache, 'setdefault'):
        cache = dict()
    for imgur_id in albums:
        cache.setdefault(imgur_id, Album(imgur_id))
    for imgur_id in images:
        cache.setdefault(imgur_id, Image(imgur_id))
    return cache


def update_cache(cache, app, client_id, ttl, whitelist):
    """Update cache items with expired TTLs.

    :param dict cache: Update this. Keys are Imgur IDs, values are Image or Album instances.
    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
    :param int ttl: Number of seconds before this is considered out of date.
    :param iter whitelist: Only update these Imgur IDs.
    """
    if not whitelist:
        whitelist = list(cache)
    needs_update = {k: v for k, v in cache.items() if k in whitelist and not v.seconds_remaining(ttl)}
    if not needs_update:
        return

    # If an image in an album needs to be updated, update entire album (includes all images in that album).
    albums_up_to_date = [v for k, v in cache.items() if v.TYPE == 'album' and k not in needs_update]
    for image_id in [k for k, v in needs_update.items() if v.TYPE == 'image']:
        for album in albums_up_to_date:
            if image_id in album:
                needs_update[album.imgur_id] = album

    # Update all albums.
    for album in (a for a in needs_update.values() if a.TYPE == 'album'):
        try:
            images = album.refresh(app, client_id, 0)
        except APIError:
            continue
        cache.update((i.imgur_id, i) for i in images)  # New Image instances.

    # Possible new Image instances, redefining needs_update. Only caring about images now.
    needs_update = {k: v for k, v in cache.items()
                    if v.TYPE == 'image' and k in whitelist and not v.seconds_remaining(ttl)}

    # Update all images.
    for image in needs_update.values():
        try:
            image.refresh(app, client_id, ttl)
        except APIError:
            continue
