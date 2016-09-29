"""Test imgur.api functions."""

import time

import httpretty
import pytest
from sphinx.errors import ExtensionError

from sphinxcontrib.imgur import api
from sphinxcontrib.imgur.imgur_api import API_URL, Image


def test_queue_new_imgur_ids():
    """Test."""
    env = type('FakeEnv', (), {})()
    env.imgur_api_cache = dict()
    imgur_ids = {'image'}
    api.queue_new_imgur_ids(env.imgur_api_cache, imgur_ids)
    assert env.imgur_api_cache['image']


def test_query_imgur_api_imgur_api_test_response_albums(monkeypatch, app):
    """Test with predefined test data.

    :param monkeypatch: pytest fixture.
    :param app: conftest fixture.
    """
    now = int(time.time())
    monkeypatch.setattr('time.time', lambda: now)
    monkeypatch.setattr(api, 'get_targeted_ids', lambda *_: {'image', 'image2', 'a/album'})

    # Do nothing on empty or none expired.
    env = type('FakeEnv', (), {'imgur_api_cache': dict()})()
    response = dict()
    api.query_imgur_api(app, env, '', 100, response)
    assert not env.imgur_api_cache
    env.imgur_api_cache['image'] = Image('image')
    env.imgur_api_cache['image'].mod_time = now - 50
    api.query_imgur_api(app, env, '', 100, response)
    assert env.imgur_api_cache['image'].mod_time == now - 50

    # Test predefined response.
    response = {
        'image': dict(description='This is a test image.', title='Test Image'),
        'a/album': dict(description='This is a test album.', title='Test Album', images=[
            dict(id='image2', description='This image is in an album.', title='Sub Image'),
            dict(id='image3', description='This image is also in an album.', title='Another Sub Image'),
        ]),
    }
    env.imgur_api_cache = dict()
    api.queue_new_imgur_ids(env.imgur_api_cache, {'image', 'a/album'})
    assert sorted(env.imgur_api_cache.keys()) == ['a/album', 'image']
    assert not env.imgur_api_cache['image'].mod_time
    assert not env.imgur_api_cache['a/album'].mod_time
    api.query_imgur_api(app, env, '', 100, response)
    assert sorted(env.imgur_api_cache.keys()) == ['a/album', 'image', 'image2', 'image3']
    assert env.imgur_api_cache['image'].mod_time == now
    assert env.imgur_api_cache['a/album'].mod_time == now
    assert env.imgur_api_cache['image2'].mod_time == now
    assert env.imgur_api_cache['image3'].mod_time == now
    assert env.imgur_api_cache['image'].description == 'This is a test image.'
    assert env.imgur_api_cache['a/album'].description == 'This is a test album.'
    assert env.imgur_api_cache['image2'].description == 'This image is in an album.'
    assert env.imgur_api_cache['image3'].description == 'This image is also in an album.'
    assert env.imgur_api_cache['image'].title == 'Test Image'
    assert env.imgur_api_cache['a/album'].title == 'Test Album'
    assert env.imgur_api_cache['image2'].title == 'Sub Image'
    assert env.imgur_api_cache['image3'].title == 'Another Sub Image'
    assert not hasattr(env.imgur_api_cache['image'], 'image_ids')
    assert not hasattr(env.imgur_api_cache['image2'], 'image_ids')
    assert not hasattr(env.imgur_api_cache['image3'], 'image_ids')
    assert env.imgur_api_cache['a/album'].image_ids == ['image2', 'image3']

    # Test optimization.
    now += 50
    monkeypatch.setattr('time.time', lambda: now)
    response.pop('image')
    response['a/album']['title'] = 'The Test Album'
    env.imgur_api_cache['image2'].mod_time = 0
    api.query_imgur_api(app, env, '', 100, response)
    assert env.imgur_api_cache['image'].mod_time == now - 50
    assert env.imgur_api_cache['a/album'].mod_time == now
    assert env.imgur_api_cache['image2'].mod_time == now
    assert env.imgur_api_cache['image3'].mod_time == now
    assert env.imgur_api_cache['a/album'].title == 'The Test Album'


def test_query_imgur_api_bad_client_id(monkeypatch, app):
    """Test with bad client_id value.

    :param monkeypatch: pytest fixture.
    :param app: conftest fixture.
    """
    monkeypatch.setattr(api, 'get_targeted_ids', lambda *_: {'image', 'a/album'})
    env = type('FakeEnv', (), {'imgur_api_cache': dict()})()
    response = dict()
    api.queue_new_imgur_ids(env.imgur_api_cache, {'image', 'a/album'})

    client_id = ''
    with pytest.raises(ExtensionError) as exc:
        api.query_imgur_api(app, env, client_id, 100, response)
    assert exc.value.args[0] == 'imgur_client_id config value must be set for Imgur API calls.'
    client_id = 'inv@lid'
    with pytest.raises(ExtensionError) as exc:
        api.query_imgur_api(app, env, client_id, 100, response)
    assert exc.value.args[0] == 'imgur_client_id config value must be 5-30 lower case letters and numbers only.'


@pytest.mark.httpretty
def test_query_imgur_api_http_error(monkeypatch, app):
    """Test HTTPError handling.

    :param monkeypatch: pytest fixture.
    :param app: conftest fixture.
    """
    monkeypatch.setattr(api, 'get_targeted_ids', lambda *_: {'image', 'a/album'})
    env = type('FakeEnv', (), {'imgur_api_cache': dict()})()
    response = dict()
    api.queue_new_imgur_ids(env.imgur_api_cache, {'image', 'a/album'})

    # Test just HTTPError.
    httpretty.register_uri(httpretty.GET, API_URL.format(type='album', id='album'), body='{}', status=500)
    httpretty.register_uri(httpretty.GET, API_URL.format(type='image', id='image'), body='{}', status=500)
    api.query_imgur_api(app, env, 'abc123abc123', 100, response)
    assert not env.imgur_api_cache['image'].mod_time
    assert not env.imgur_api_cache['a/album'].mod_time


@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_query_imgur_api(monkeypatch, app):
    """Test with mocked urllib responses.

    :param monkeypatch: pytest fixture.
    :param app: conftest fixture.
    """
    monkeypatch.setattr(api, 'get_targeted_ids', lambda *_: {'611EovQ', 'a/V76cJ'})
    env = type('FakeEnv', (), {'imgur_api_cache': dict()})()
    response = dict()
    api.queue_new_imgur_ids(env.imgur_api_cache, {'611EovQ', 'a/V76cJ'})

    # Test JSON response.
    api.query_imgur_api(app, env, 'abc123abc123', 100, response)
    assert sorted(env.imgur_api_cache.keys()) == ['611EovQ', 'a/V76cJ', 'mGQBV', 'ojGG7', 'pc8hc']
    assert env.imgur_api_cache['611EovQ'].mod_time > 1438916421
    assert env.imgur_api_cache['a/V76cJ'].mod_time > 1438916421
    assert env.imgur_api_cache['mGQBV'].mod_time > 1438916421
    assert env.imgur_api_cache['pc8hc'].mod_time > 1438916421
    assert env.imgur_api_cache['ojGG7'].mod_time > 1438916421
    assert env.imgur_api_cache['611EovQ'].description == ('Right before I moved desks for the 6th time in 1.5 years.'
                                                          ' I lost my nice window desk, oh well.')
    assert env.imgur_api_cache['a/V76cJ'].description == ('Installing a Qi wireless induction charger inside my '
                                                          'door to charge my phone when I set it down in my door '
                                                          'pocket.')
    assert env.imgur_api_cache['mGQBV'].description == ('Removed door panel from my car and tested whether my idea '
                                                        'would work. It works!')
    assert env.imgur_api_cache['pc8hc'].description == 'Closeup of Nokia DT-900 charger wedged in my door panel.'
    assert env.imgur_api_cache['ojGG7'].description == ("Setting my phone in my door pocket charges it! The door "
                                                        "panel's plastic between the phone and charger is thin "
                                                        "enough.")
    assert env.imgur_api_cache['611EovQ'].title == 'Work, June 1st, 2016: Uber'
    assert env.imgur_api_cache['a/V76cJ'].title == '2010 JSW, 2012 Projects'
    assert env.imgur_api_cache['mGQBV'].title == 'Wireless Charging 1: Testing'
    assert env.imgur_api_cache['pc8hc'].title == 'Wireless Charging 2: Testing Closeup'
    assert env.imgur_api_cache['ojGG7'].title == 'Wireless Charging 3: Works'
    assert not hasattr(env.imgur_api_cache['611EovQ'], 'image_ids')
    assert not hasattr(env.imgur_api_cache['mGQBV'], 'image_ids')
    assert not hasattr(env.imgur_api_cache['pc8hc'], 'image_ids')
    assert not hasattr(env.imgur_api_cache['ojGG7'], 'image_ids')
    assert env.imgur_api_cache['a/V76cJ'].image_ids == ['mGQBV', 'pc8hc', 'ojGG7']
