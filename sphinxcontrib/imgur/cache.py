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


def prune_cache(cache, app, doctree_imgur_ids=None):
    """Remove Images and Albums from the cache if they are no longer used.

    :param dict cache: Update this. Keys are Imgur IDs, values are Image or Album instances.
    :param sphinx.application.Sphinx app: Sphinx application object.
    :param iter doctree_imgur_ids: Imgur image or album IDs used in all Sphinx docs.
    """
    # Prune invalid types.
    for key in [k for k, v in cache.items() if not hasattr(v, 'TYPE') or not hasattr(v, 'imgur_id')]:
        app.debug("removing %s from Imgur cache since value isn't Album/Image instance.", key)
        cache.pop(key)

    # Prune key mismatches.
    for key in [k for k, v in cache.items() if v.imgur_id != k]:
        app.debug("removing %s from Imgur cache since imgur_id doesn't match.", key)
        cache.pop(key)

    if doctree_imgur_ids is None:
        return

    # Now prune albums.
    for album_id in [k for k, v in cache.items() if v.TYPE == 'album']:
        if album_id not in doctree_imgur_ids:
            app.debug("removing %s from Imgur cache since it's not in the doctree.", album_id)
            cache.pop(album_id)

    # Finally prune images not in doctree and not in any album.
    used_ids = list(doctree_imgur_ids) + [i for v in cache.values() if v.TYPE == 'album' for i in v.image_ids]
    for image_id in [k for k, v in cache.items() if v.TYPE == 'image']:
        if image_id not in used_ids:
            app.debug("removing %s from Imgur cache since it's not in the doctree nor any album.", image_id)
            cache.pop(image_id)


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
