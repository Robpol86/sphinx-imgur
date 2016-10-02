"""Tests for module."""

import time

import httpretty
import pytest

from sphinxcontrib.imgur.cache import initialize, prune_cache, update_cache
from sphinxcontrib.imgur.imgur_api import API_URL


def test_initialize():
    """Test function."""
    cache = initialize(dict(), ['album1'], ['image1'])
    assert sorted(cache) == ['album1', 'image1']
    assert cache['album1'].title == ''
    assert cache['image1'].title == ''

    cache['album1'].title = 'Set1'
    cache['image1'].title = 'Set2'
    cache = initialize(cache, ['album1', 'album2'], ['image1', 'image2'])
    assert cache['album1'].title == 'Set1'
    assert cache['image1'].title == 'Set2'
    assert cache['album2'].title == ''
    assert cache['image2'].title == ''


@pytest.mark.parametrize('cache_in', [None, False, int(), list(), set(), tuple(), str(), object()])
def test_initialize_not_dict(cache_in):
    """Test function with a non-dictionary cache value.

    :param cache_in: Input cache value.
    """
    cache = initialize(cache_in, ['album1'], ['image1'])
    assert sorted(cache) == ['album1', 'image1']
    assert cache['album1'].title == ''
    assert cache['image1'].title == ''


def test_prune_cache_prune_nothing(app):
    """Test with nothing to prune.

    :param app: conftest fixture.
    """
    cache = initialize(dict(), ['album1'], ['image1', 'image2', 'image3'])
    cache['album1'].image_ids = ['image3']
    doctree_imgur_ids = ['album1', 'image1', 'image2']
    prune_cache(cache, app, doctree_imgur_ids)
    assert sorted(cache) == ['album1', 'image1', 'image2', 'image3']


def test_prune_cache_prune_albums_images(app):
    """Test pruning albums and images.

    :param app: conftest fixture.
    """
    cache = initialize(dict(), ['album1', 'album2'], ['image1', 'image2', 'image3'])
    cache['album1'].image_ids = ['image1']
    cache['album2'].image_ids = ['image2']
    doctree_imgur_ids = ['album1', 'image3']
    prune_cache(cache, app, doctree_imgur_ids)
    assert sorted(cache) == ['album1', 'image1', 'image3']


@pytest.mark.parametrize('doctree_none', [False, True])
def test_prune_cache_bad_types(app, doctree_none):
    """Test pruning v1.0.0/invalid items from cache.

    :param app: conftest fixture.
    :param bool doctree_none: Test with None value for last argument.
    """
    cache = initialize(dict(), ['album1'], ['image1', 'willBeBad1', 'willBeBad1'])
    doctree_imgur_ids = None if doctree_none else list(cache)  # Same effect.
    for key in ('album2', 0, False, None, ''):
        cache[key] = cache['album1']
        if not doctree_none:
            doctree_imgur_ids.append(key)
    cache['willBeBad1'] = None
    cache['willBeBad1'] = str()

    prune_cache(cache, app, doctree_imgur_ids)
    assert sorted(cache) == ['album1', 'image1']


@pytest.mark.httpretty
def test_update_cache_none_needed(app, freezer):
    """Test no updates needed.

    :param app: conftest fixture.
    :param freezer: conftest fixture.
    """
    cache = initialize(dict(), ['album1'], ['image1', 'image2', 'image3'])
    cache['album1'].image_ids = ['image3']

    cache['album1'].mod_time = int(time.time())
    cache['image1'].mod_time = int(time.time())
    cache['image2'].mod_time = int(time.time())
    cache['image3'].mod_time = int(time.time())
    before = {k: v.__dict__.copy() for k, v in cache.items()}

    freezer.tick()
    update_cache(cache, app, 'client_id', 30, list())
    after = {k: v.__dict__.copy() for k, v in cache.items()}

    assert not app.messages
    assert after == before


@pytest.mark.usefixtures('freezer', 'httpretty_common_mock')
@pytest.mark.httpretty
def test_update_cache_everything(app):
    """Test with everything outdated.

    :param app: conftest fixture.
    """
    cache = initialize(dict(), ['V76cJ'], ['hiX02'])
    before = {k: v.__dict__.copy() for k, v in cache.items()}

    update_cache(cache, app, 'client_id', 30, list())
    after = {k: v.__dict__.copy() for k, v in cache.items()}
    assert after != before

    assert sorted(cache) == ['V76cJ', 'hiX02', 'mGQBV', 'ojGG7', 'pc8hc']
    assert cache['V76cJ'].mod_time == int(time.time())
    assert cache['hiX02'].mod_time == int(time.time())
    assert cache['mGQBV'].mod_time == int(time.time())
    assert cache['ojGG7'].mod_time == int(time.time())
    assert cache['pc8hc'].mod_time == int(time.time())
    assert cache['V76cJ'].imgur_id == 'V76cJ'
    assert cache['hiX02'].imgur_id == 'hiX02'
    assert cache['mGQBV'].imgur_id == 'mGQBV'
    assert cache['ojGG7'].imgur_id == 'ojGG7'
    assert cache['pc8hc'].imgur_id == 'pc8hc'
    assert cache['V76cJ'].description.startswith('Installing a Qi wireless induction charger inside my door to charge ')
    assert cache['hiX02'].description is None
    assert cache['mGQBV'].description.startswith('Removed door panel from my car and tested whether my idea would work')
    assert cache['ojGG7'].description.startswith("Setting my phone in my door pocket charges it! The door panel's plas")
    assert cache['pc8hc'].description == 'Closeup of Nokia DT-900 charger wedged in my door panel.'
    assert cache['V76cJ'].title == '2010 JSW, 2012 Projects'
    assert cache['hiX02'].title is None
    assert cache['mGQBV'].title == 'Wireless Charging 1: Testing'
    assert cache['ojGG7'].title == 'Wireless Charging 3: Works'
    assert cache['pc8hc'].title == 'Wireless Charging 2: Testing Closeup'
    assert cache['V76cJ'].image_ids == ['mGQBV', 'pc8hc', 'ojGG7']


@pytest.mark.parametrize('album', [True, False])
@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_update_cache_error_handling(app, album):
    """Test error handling.

    :param app: conftest fixture.
    :param bool album: Error on album instead of image.
    """
    if album:
        httpretty.register_uri(httpretty.GET, API_URL.format(type='album', id='album'), body='{}', status=500)
        cache = initialize(dict(), ['album'], ['611EovQ'])
    else:
        httpretty.register_uri(httpretty.GET, API_URL.format(type='image', id='image'), body='{}', status=500)
        cache = initialize(dict(), ['V76cJ'], ['image'])
    before = {k: v.__dict__.copy() for k, v in cache.items()}

    update_cache(cache, app, 'client_id', 30, list())
    after = {k: v.__dict__.copy() for k, v in cache.items()}
    assert after != before

    if album:
        assert sorted(cache) == ['611EovQ', 'album']
        assert cache['611EovQ'].mod_time > 0
        assert cache['611EovQ'].description.startswith('Right before I moved desks for the 6th time in 1.5 years. I')
        assert cache['611EovQ'].title == 'Work, June 1st, 2016: Uber'
        assert cache['album'].mod_time == 0
        assert cache['album'].description == ''
        assert cache['album'].title == ''
        assert cache['album'].image_ids == list()
    else:
        assert sorted(cache) == ['V76cJ', 'image', 'mGQBV', 'ojGG7', 'pc8hc']
        assert cache['V76cJ'].mod_time > 0
        assert cache['V76cJ'].description.startswith('Installing a Qi wireless induction charger inside my door to')
        assert cache['V76cJ'].title == '2010 JSW, 2012 Projects'
        assert cache['V76cJ'].image_ids == ['mGQBV', 'pc8hc', 'ojGG7']
        assert cache['image'].mod_time == 0
        assert cache['image'].description == ''
        assert cache['image'].title == ''
        assert cache['mGQBV'].mod_time > 0
        assert cache['mGQBV'].description.startswith('Removed door panel from my car and tested whether my idea would')
        assert cache['mGQBV'].title == 'Wireless Charging 1: Testing'
        assert cache['ojGG7'].mod_time > 0
        assert cache['ojGG7'].description.startswith("Setting my phone in my door pocket charges it! The door panel's")
        assert cache['ojGG7'].title == 'Wireless Charging 3: Works'
        assert cache['pc8hc'].mod_time > 0
        assert cache['pc8hc'].description == 'Closeup of Nokia DT-900 charger wedged in my door panel.'
        assert cache['pc8hc'].title == 'Wireless Charging 2: Testing Closeup'

    # Verify log.
    merged = '\n'.join('\t'.join(m) for m in app.messages)
    if album:
        assert 'query unsuccessful from https://api.imgur.com/3/album/album: N/A' in merged
        assert '"id": "611EovQ"' in merged
    else:
        assert '"id": "V76cJ"' in merged
        assert '"id": "mGQBV"' in merged
        assert '"id": "ojGG7"' in merged
        assert '"id": "pc8hc"' in merged
        assert 'query unsuccessful from https://api.imgur.com/3/image/image: N/A' in merged


@pytest.mark.httpretty
def test_update_cache_error_keep_previous(app):
    """Make sure error handling preserves previous data in cache.

    :param app: conftest fixture.
    """
    httpretty.register_uri(httpretty.GET, API_URL.format(type='album', id='album'), body='{}', status=500)
    cache = initialize(dict(), ['album'], [])
    cache['album'].description = 'Old'
    cache['album'].title = 'Old'

    update_cache(cache, app, 'client_id', 30, list())

    assert cache['album'].description == 'Old'
    assert cache['album'].title == 'Old'
    assert cache['album'].mod_time == 0

    merged = '\n'.join('\t'.join(m) for m in app.messages)
    assert 'query unsuccessful from https://api.imgur.com/3/album/album: N/A' in merged


@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_update_cache_half(app):
    """Test with half the albums and half the standalone images being outdated.

    :param app: conftest fixture.
    """
    cache = initialize(dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j'])
    cache['V76cJ'].mod_time = int(time.time())
    cache['V76cJ'].title = 'No Change'
    cache['VMlM6'].image_ids = ['image1', 'image2', 'image2']
    cache['hiX02'].mod_time = int(time.time())
    cache['hiX02'].title = 'No Change'

    update_cache(cache, app, 'client_id', 30, list())

    assert cache['V76cJ'].title == 'No Change'
    assert cache['V76cJ'].image_ids == list()
    assert cache['VMlM6'].title == 'Screenshots'
    assert cache['VMlM6'].image_ids == ['2QcXR3R', 'Hqw7KHM']
    assert cache['hiX02'].title == 'No Change'
    assert cache['Pwx1G5j'].title is None


@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_update_cache_one_image_in_album(app, freezer):
    """Test one image in an album outdated (but not other images in said album).

    :param app: conftest fixture.
    :param freezer: conftest fixture.
    """
    cache = initialize(dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j'])
    update_cache(cache, app, 'client_id', 30, list())

    # Advance time by one second and outdate one image from V76cJ album.
    freezer.tick()
    cache['mGQBV'].mod_time = 0
    update_cache(cache, app, 'client_id', 30, list())

    # V76cJ should be updated since one of its images were.
    assert cache['V76cJ'].mod_time == int(time.time())  # Recently updated.
    assert cache['VMlM6'].mod_time != int(time.time())  # Not updated.
    assert cache['hiX02'].mod_time != int(time.time())
    assert cache['Pwx1G5j'].mod_time != int(time.time())

    # All images in V76cJ should be updated.
    assert cache['mGQBV'].mod_time == int(time.time())
    assert cache['pc8hc'].mod_time == int(time.time())
    assert cache['ojGG7'].mod_time == int(time.time())
    assert cache['2QcXR3R'].mod_time != int(time.time())
    assert cache['Hqw7KHM'].mod_time != int(time.time())


@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_update_cache_whitelist(app):
    """Test updating only whitelisted items.

    :param app: conftest fixture.
    """
    cache = initialize(dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j'])
    update_cache(cache, app, 'client_id', 30, ['V76cJ', 'hiX02'])
    updated = [m[1].split('/')[-1] for m in app.messages if m[0] == 'info' and m[1].startswith('querying https://api')]

    assert cache['V76cJ'].mod_time > 0
    assert cache['VMlM6'].mod_time == 0
    assert cache['hiX02'].mod_time > 0
    assert cache['Pwx1G5j'].mod_time == 0

    assert cache['mGQBV'].mod_time > 0
    assert cache['pc8hc'].mod_time > 0
    assert cache['ojGG7'].mod_time > 0

    assert updated == ['V76cJ', 'hiX02']


@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_update_cache_whitelist_parent(app):
    """Make sure parent album is updated even if not in whitelist.

    :param app: conftest fixture.
    """
    cache = initialize(dict(), ['V76cJ', 'VMlM6'], ['hiX02', 'Pwx1G5j', 'mGQBV'])
    cache['V76cJ'].image_ids = ['mGQBV']
    update_cache(cache, app, 'client_id', 30, ['mGQBV'])
    updated = [m[1].split('/')[-1] for m in app.messages if m[0] == 'info' and m[1].startswith('querying https://api')]

    assert cache['V76cJ'].mod_time > 0
    assert cache['VMlM6'].mod_time == 0
    assert cache['hiX02'].mod_time == 0
    assert cache['Pwx1G5j'].mod_time == 0

    assert cache['mGQBV'].mod_time > 0
    assert cache['pc8hc'].mod_time > 0
    assert cache['ojGG7'].mod_time > 0

    assert updated == ['V76cJ']


@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_update_cache_whitelist_parent_changed(app):
    """Make sure child image is still updated when parent album no longer has the image.

    :param app: conftest fixture.
    """
    cache = initialize(dict(), ['V76cJ'], ['hiX02', 'Pwx1G5j', '2QcXR3R'])
    cache['V76cJ'].image_ids = ['2QcXR3R']
    update_cache(cache, app, 'client_id', 30, ['2QcXR3R'])
    updated = [m[1].split('/')[-1] for m in app.messages if m[0] == 'info' and m[1].startswith('querying https://api')]

    assert cache['V76cJ'].mod_time > 0
    assert cache['hiX02'].mod_time == 0
    assert cache['Pwx1G5j'].mod_time == 0
    assert cache['2QcXR3R'].mod_time > 0

    assert cache['mGQBV'].mod_time > 0
    assert cache['pc8hc'].mod_time > 0
    assert cache['ojGG7'].mod_time > 0

    assert updated == ['V76cJ', '2QcXR3R']
