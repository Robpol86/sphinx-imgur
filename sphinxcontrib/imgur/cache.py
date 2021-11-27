"""Manage Imgur cache."""

from sphinxcontrib.imgur.imgur_api import Album, APIError, Image


def initialize(album_cache, image_cache, albums, images):
    """Instantiate Album or Image instances not already in cache.

    :param dict album_cache: Cache of Imgur albums to update. Keys are Imgur IDs, values are Album instances.
    :param dict image_cache: Cache of Imgur images to update. Keys are Imgur IDs, values are Image instances.
    :param iter albums: List of album Imgur IDs.
    :param iter images: List of image Imgur IDs.

    :return: Same album and image cache dictionaries from parameters.
    :rtype: tuple
    """
    if not hasattr(album_cache, "setdefault"):
        album_cache = dict()
    if not hasattr(image_cache, "setdefault"):
        image_cache = dict()
    for imgur_id in albums:
        album_cache.setdefault(imgur_id, Album(imgur_id))
    for imgur_id in images:
        image_cache.setdefault(imgur_id, Image(imgur_id))
    return album_cache, image_cache


def prune_cache(image_cache, app, doctree_image_ids=None):
    """Remove Images from the cache if they are no longer used.

    :param dict image_cache: Cache of Imgur images to update. Keys are Imgur IDs, values are Image instances.
    :param sphinx.application.Sphinx app: Sphinx application object.
    :param iter doctree_image_ids: Imgur image IDs used in all Sphinx docs.
    """
    # Prune invalid types.
    for kind, cache in (("Image", image_cache),):
        for key in [k for k, v in cache.items() if not hasattr(v, "KIND") or not hasattr(v, "imgur_id")]:
            app.debug("removing %s from Imgur cache since value isn't %s instance.", key, kind)
            cache.pop(key)

    # Prune key mismatches.
    for cache in (image_cache,):
        for key in [k for k, v in cache.items() if v.imgur_id != k]:
            app.debug("removing %s from Imgur cache since imgur_id doesn't match.", key)
            cache.pop(key)

    if doctree_image_ids is None:
        return

    # Finally prune images not in doctree.
    used_ids = list(doctree_image_ids)
    for image_id in [i for i in image_cache if i not in used_ids]:
        app.debug("removing %s from Imgur image cache since it's not in the doctree.", image_id)
        image_cache.pop(image_id)


def update_cache(image_cache, app, client_id, ttl, image_whitelist):
    """Update cache items with expired TTLs.

    :param dict image_cache: Cache of Imgur images to update. Keys are Imgur IDs, values are Image instances.
    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
    :param int ttl: Number of seconds before this is considered out of date.
    :param iter image_whitelist: Only update these Imgur image IDs.
    """
    if not image_whitelist:
        image_whitelist = list(image_cache)
    needs_update_image = {k: v for k, v in image_cache.items() if k in image_whitelist and not v.seconds_remaining(ttl)}
    if not needs_update_image:
        return

    # Possible new Image instances, redefining needs_update. Only caring about images now.
    needs_update_image = {k: v for k, v in image_cache.items() if k in image_whitelist and not v.seconds_remaining(ttl)}

    # Update all images.
    for image in needs_update_image.values():
        try:
            image.refresh(app, client_id, ttl)
        except APIError:
            continue
