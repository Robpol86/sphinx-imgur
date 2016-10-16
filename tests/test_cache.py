"""Tests for module."""

import time

import httpretty
import pytest

from sphinxcontrib.imgur.cache import initialize, prune_cache, update_cache
from sphinxcontrib.imgur.imgur_api import API_URL


def test_initialize():
    """Test function."""
    album_cache, image_cache = initialize(dict(), dict(), ['album1'], ['image1'])
    assert sorted(album_cache) == ['album1']
    assert sorted(image_cache) == ['image1']
    assert album_cache['album1'].title == ''
    assert image_cache['image1'].title == ''

    album_cache['album1'].title = 'Set1'
    image_cache['image1'].title = 'Set2'
    album_cache, image_cache = initialize(album_cache, image_cache, ['album1', 'album2'], ['image1', 'image2'])
    assert album_cache['album1'].title == 'Set1'
    assert image_cache['image1'].title == 'Set2'
    assert album_cache['album2'].title == ''
    assert image_cache['image2'].title == ''


@pytest.mark.parametrize('cache_in', [None, False, int(), list(), set(), tuple(), str(), object()])
def test_initialize_not_dict(cache_in):
    """Test function with a non-dictionary cache value.

    :param cache_in: Input cache value.
    """
    album_cache, image_cache = initialize(cache_in, cache_in, ['album1'], ['image1'])
    assert sorted(album_cache) == ['album1']
    assert sorted(image_cache) == ['image1']
    assert album_cache['album1'].title == ''
    assert image_cache['image1'].title == ''


def test_prune_cache_prune_nothing(app):
    """Test with nothing to prune.

    :param app: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['album1'], ['image1', 'image2', 'image3'])
    album_cache['album1'].image_ids = ['image3']
    doctree_album_ids = ['album1']
    doctree_image_ids = ['image1', 'image2']
    prune_cache(album_cache, image_cache, app, doctree_album_ids, doctree_image_ids)
    assert sorted(album_cache) == ['album1']
    assert sorted(image_cache) == ['image1', 'image2', 'image3']


def test_prune_cache_prune_albums_images(app):
    """Test pruning albums and images.

    :param app: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['album1', 'album2'], ['image1', 'image2', 'image3'])
    album_cache['album1'].image_ids = ['image1']
    album_cache['album2'].image_ids = ['image2']
    doctree_album_ids = ['album1']
    doctree_image_ids = ['image3']
    prune_cache(album_cache, image_cache, app, doctree_album_ids, doctree_image_ids)
    assert sorted(album_cache) == ['album1']
    assert sorted(image_cache) == ['image1', 'image3']


@pytest.mark.parametrize('doctree_none', [False, True])
def test_prune_cache_bad_types(app, doctree_none):
    """Test pruning v1.0.0/invalid items from cache.

    :param app: conftest fixture.
    :param bool doctree_none: Test with None value for last argument.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['album1', 'willBeBad1'], ['image1', 'willBeBad2'])
    doctree_album_ids = None if doctree_none else list(album_cache)  # Same effect.
    doctree_image_ids = None if doctree_none else list(image_cache)  # Same effect.
    for key in ('album2', 0, False, None, ''):
        album_cache[key] = album_cache['album1']
        if not doctree_none:
            doctree_album_ids.append(key)
    for key in ('image2', 0, False, None, ''):
        image_cache[key] = image_cache['image1']
        if not doctree_none:
            doctree_image_ids.append(key)
    album_cache['willBeBad1'] = None
    image_cache['willBeBad2'] = str()

    prune_cache(album_cache, image_cache, app, doctree_album_ids, doctree_image_ids)
    assert sorted(album_cache) == ['album1']
    assert sorted(image_cache) == ['image1']


def test_update_cache_none_needed(app, freezer):
    """Test no updates needed.

    :param app: conftest fixture.
    :param freezer: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['album1'], ['image1', 'image2', 'image3'])
    album_cache['album1'].image_ids = ['image3']

    album_cache['album1'].mod_time = int(time.time())
    image_cache['image1'].mod_time = int(time.time())
    image_cache['image2'].mod_time = int(time.time())
    image_cache['image3'].mod_time = int(time.time())
    before = {k: v.__dict__.copy() for k, v in album_cache.items()}
    before.update({k: v.__dict__.copy() for k, v in image_cache.items()})

    freezer.tick()
    update_cache(album_cache, image_cache, app, 'client_id', 30, list(), list())
    after = {k: v.__dict__.copy() for k, v in album_cache.items()}
    after.update({k: v.__dict__.copy() for k, v in image_cache.items()})

    assert not app.messages
    assert after == before


@pytest.mark.usefixtures('freezer', 'httpretty_common_mock')
def test_update_cache_everything(app):
    """Test with everything outdated.

    :param app: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['V76cJ'], ['hiX02'])
    before = {k: v.__dict__.copy() for k, v in album_cache.items()}
    before.update({k: v.__dict__.copy() for k, v in image_cache.items()})

    update_cache(album_cache, image_cache, app, 'client_id', 30, list(), list())
    after = {k: v.__dict__.copy() for k, v in album_cache.items()}
    after.update({k: v.__dict__.copy() for k, v in image_cache.items()})
    assert after != before

    assert sorted(album_cache) == ['V76cJ']
    assert sorted(image_cache) == ['hiX02', 'mGQBV', 'ojGG7', 'pc8hc']
    assert album_cache['V76cJ'].mod_time == int(time.time())
    assert image_cache['hiX02'].mod_time == int(time.time())
    assert image_cache['mGQBV'].mod_time == int(time.time())
    assert image_cache['ojGG7'].mod_time == int(time.time())
    assert image_cache['pc8hc'].mod_time == int(time.time())
    assert album_cache['V76cJ'].imgur_id == 'V76cJ'
    assert image_cache['hiX02'].imgur_id == 'hiX02'
    assert image_cache['mGQBV'].imgur_id == 'mGQBV'
    assert image_cache['ojGG7'].imgur_id == 'ojGG7'
    assert image_cache['pc8hc'].imgur_id == 'pc8hc'
    assert album_cache['V76cJ'].description.startswith('Installing a Qi wireless induction charger inside my door to c')
    assert image_cache['hiX02'].description is None
    assert image_cache['mGQBV'].description.startswith('Removed door panel from my car and tested whether my idea woul')
    assert image_cache['ojGG7'].description.startswith("Setting my phone in my door pocket charges it! The door panel'")
    assert image_cache['pc8hc'].description == 'Closeup of Nokia DT-900 charger wedged in my door panel.'
    assert album_cache['V76cJ'].title == '2010 JSW, 2012 Projects'
    assert image_cache['hiX02'].title is None
    assert image_cache['mGQBV'].title == 'Wireless Charging 1: Testing'
    assert image_cache['ojGG7'].title == 'Wireless Charging 3: Works'
    assert image_cache['pc8hc'].title == 'Wireless Charging 2: Testing Closeup'
    assert album_cache['V76cJ'].image_ids == ['mGQBV', 'pc8hc', 'ojGG7']


@pytest.mark.parametrize('album', [True, False])
@pytest.mark.usefixtures('httpretty_common_mock')
def test_update_cache_error_handling(app, album):
    """Test error handling.

    :param app: conftest fixture.
    :param bool album: Error on album instead of image.
    """
    if album:
        httpretty.register_uri(httpretty.GET, API_URL.format(type='album', id='album'), body='{}', status=500)
        album_cache, image_cache = initialize(dict(), dict(), ['album'], ['611EovQ'])
    else:
        httpretty.register_uri(httpretty.GET, API_URL.format(type='image', id='image'), body='{}', status=500)
        album_cache, image_cache = initialize(dict(), dict(), ['V76cJ'], ['image'])
    before = {k: v.__dict__.copy() for k, v in album_cache.items()}
    before.update({k: v.__dict__.copy() for k, v in image_cache.items()})

    update_cache(album_cache, image_cache, app, 'client_id', 30, list(), list())
    after = {k: v.__dict__.copy() for k, v in album_cache.items()}
    after.update({k: v.__dict__.copy() for k, v in image_cache.items()})
    assert after != before

    if album:
        assert sorted(album_cache) == ['album']
        assert sorted(image_cache) == ['611EovQ']
        assert image_cache['611EovQ'].mod_time > 0
        assert image_cache['611EovQ'].description.startswith('Right before I moved desks for the 6th time in 1.5 years')
        assert image_cache['611EovQ'].title == 'Work, June 1st, 2016: Uber'
        assert album_cache['album'].mod_time == 0
        assert album_cache['album'].description == ''
        assert album_cache['album'].title == ''
        assert album_cache['album'].image_ids == list()
    else:
        assert sorted(album_cache) == ['V76cJ']
        assert sorted(image_cache) == ['image', 'mGQBV', 'ojGG7', 'pc8hc']
        assert album_cache['V76cJ'].mod_time > 0
        assert album_cache['V76cJ'].description.startswith('Installing a Qi wireless induction charger inside my door ')
        assert album_cache['V76cJ'].title == '2010 JSW, 2012 Projects'
        assert album_cache['V76cJ'].image_ids == ['mGQBV', 'pc8hc', 'ojGG7']
        assert image_cache['image'].mod_time == 0
        assert image_cache['image'].description == ''
        assert image_cache['image'].title == ''
        assert image_cache['mGQBV'].mod_time > 0
        assert image_cache['mGQBV'].description.startswith('Removed door panel from my car and tested whether my idea ')
        assert image_cache['mGQBV'].title == 'Wireless Charging 1: Testing'
        assert image_cache['ojGG7'].mod_time > 0
        assert image_cache['ojGG7'].description.startswith('Setting my phone in my door pocket charges it! The door pa')
        assert image_cache['ojGG7'].title == 'Wireless Charging 3: Works'
        assert image_cache['pc8hc'].mod_time > 0
        assert image_cache['pc8hc'].description == 'Closeup of Nokia DT-900 charger wedged in my door panel.'
        assert image_cache['pc8hc'].title == 'Wireless Charging 2: Testing Closeup'

    # Verify log.
    merged = '\n'.join('\t'.join(m) for m in app.messages)
    if album:
        assert 'query unsuccessful from https://api.imgur.com/3/album/album: no "data" key in JSON' in merged
        assert '"id": "611EovQ"' in merged
    else:
        assert '"id": "V76cJ"' in merged
        assert '"id": "mGQBV"' in merged
        assert '"id": "ojGG7"' in merged
        assert '"id": "pc8hc"' in merged
        assert 'query unsuccessful from https://api.imgur.com/3/image/image: no "data" key in JSON' in merged


def test_update_cache_error_keep_previous(app):
    """Make sure error handling preserves previous data in cache.

    :param app: conftest fixture.
    """
    httpretty.register_uri(httpretty.GET, API_URL.format(type='album', id='album'), body='{"data": {}}', status=500)
    album_cache, image_cache = initialize(dict(), dict(), ['album'], [])
    album_cache['album'].description = 'Old'
    album_cache['album'].title = 'Old'

    update_cache(album_cache, image_cache, app, 'client_id', 30, list(), list())

    assert album_cache['album'].description == 'Old'
    assert album_cache['album'].title == 'Old'
    assert album_cache['album'].mod_time == 0

    merged = '\n'.join('\t'.join(m) for m in app.messages)
    assert 'query unsuccessful from https://api.imgur.com/3/album/album: no "error" key in JSON' in merged


@pytest.mark.usefixtures('httpretty_common_mock')
def test_update_cache_half(app):
    """Test with half the albums and half the standalone images being outdated.

    :param app: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j'])
    album_cache['V76cJ'].mod_time = int(time.time())
    album_cache['V76cJ'].title = 'No Change'
    album_cache['VMlM6'].image_ids = ['image1', 'image2', 'image2']
    image_cache['hiX02'].mod_time = int(time.time())
    image_cache['hiX02'].title = 'No Change'

    update_cache(album_cache, image_cache, app, 'client_id', 30, list(), list())

    assert album_cache['V76cJ'].title == 'No Change'
    assert album_cache['V76cJ'].image_ids == list()
    assert album_cache['VMlM6'].title == 'Screenshots'
    assert album_cache['VMlM6'].image_ids == ['2QcXR3R', 'Hqw7KHM']
    assert image_cache['hiX02'].title == 'No Change'
    assert image_cache['Pwx1G5j'].title is None


@pytest.mark.usefixtures('httpretty_common_mock')
def test_update_cache_one_image_in_album(app, freezer):
    """Test one image in an album outdated (but not other images in said album).

    :param app: conftest fixture.
    :param freezer: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j'])
    update_cache(album_cache, image_cache, app, 'client_id', 30, list(), list())

    # Advance time by one second and outdate one image from V76cJ album.
    freezer.tick()
    image_cache['mGQBV'].mod_time = 0
    update_cache(album_cache, image_cache, app, 'client_id', 30, list(), list())

    # V76cJ should be updated since one of its images were.
    assert album_cache['V76cJ'].mod_time == int(time.time())  # Recently updated.
    assert album_cache['VMlM6'].mod_time != int(time.time())  # Not updated.
    assert image_cache['hiX02'].mod_time != int(time.time())
    assert image_cache['Pwx1G5j'].mod_time != int(time.time())

    # All images in V76cJ should be updated.
    assert image_cache['mGQBV'].mod_time == int(time.time())
    assert image_cache['pc8hc'].mod_time == int(time.time())
    assert image_cache['ojGG7'].mod_time == int(time.time())
    assert image_cache['2QcXR3R'].mod_time != int(time.time())
    assert image_cache['Hqw7KHM'].mod_time != int(time.time())


@pytest.mark.usefixtures('httpretty_common_mock')
def test_update_cache_whitelist(app):
    """Test updating only whitelisted items.

    :param app: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j'])
    update_cache(album_cache, image_cache, app, 'client_id', 30, ['V76cJ'], ['hiX02'])
    updated = [m[1].split('/')[-1] for m in app.messages if m[0] == 'info' and m[1].startswith('querying https://api')]

    assert album_cache['V76cJ'].mod_time > 0
    assert album_cache['VMlM6'].mod_time == 0
    assert image_cache['hiX02'].mod_time > 0
    assert image_cache['Pwx1G5j'].mod_time == 0

    assert image_cache['mGQBV'].mod_time > 0
    assert image_cache['pc8hc'].mod_time > 0
    assert image_cache['ojGG7'].mod_time > 0

    assert updated == ['V76cJ', 'hiX02']


@pytest.mark.usefixtures('httpretty_common_mock')
def test_update_cache_whitelist_parent(app):
    """Make sure parent album is updated even if not in whitelist.

    :param app: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j', 'mGQBV'])
    album_cache['V76cJ'].image_ids = ['mGQBV']
    update_cache(album_cache, image_cache, app, 'client_id', 30, [], ['mGQBV'])
    updated = [m[1].split('/')[-1] for m in app.messages if m[0] == 'info' and m[1].startswith('querying https://api')]

    assert album_cache['V76cJ'].mod_time > 0
    assert album_cache['VMlM6'].mod_time == 0
    assert image_cache['hiX02'].mod_time == 0
    assert image_cache['Pwx1G5j'].mod_time == 0

    assert image_cache['mGQBV'].mod_time > 0
    assert image_cache['pc8hc'].mod_time > 0
    assert image_cache['ojGG7'].mod_time > 0

    assert updated == ['V76cJ']


@pytest.mark.usefixtures('httpretty_common_mock')
def test_update_cache_whitelist_parent_changed(app):
    """Make sure child image is still updated when parent album no longer has the image.

    :param app: conftest fixture.
    """
    album_cache, image_cache = initialize(dict(), dict(), ['V76cJ'], ['hiX02', 'Pwx1G5j', '2QcXR3R'])
    album_cache['V76cJ'].image_ids = ['2QcXR3R']
    update_cache(album_cache, image_cache, app, 'client_id', 30, [], ['2QcXR3R'])
    updated = [m[1].split('/')[-1] for m in app.messages if m[0] == 'info' and m[1].startswith('querying https://api')]

    assert album_cache['V76cJ'].mod_time > 0
    assert image_cache['hiX02'].mod_time == 0
    assert image_cache['Pwx1G5j'].mod_time == 0
    assert image_cache['2QcXR3R'].mod_time > 0

    assert image_cache['mGQBV'].mod_time > 0
    assert image_cache['pc8hc'].mod_time > 0
    assert image_cache['ojGG7'].mod_time > 0

    assert updated == ['V76cJ', '2QcXR3R']
