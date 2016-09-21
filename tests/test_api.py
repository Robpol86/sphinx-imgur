"""Test imgur.api functions."""

import json
import re
import time

import httpretty
import pytest
from sphinx.errors import ExtensionError

from sphinxcontrib.imgur import api
from sphinxcontrib.imgur.imgur_api import API_URL


def test_queue_new_imgur_ids():
    """Test."""
    env = type('FakeEnv', (), {})()
    env.imgur_api_cache = dict()
    imgur_ids = {'image'}
    api.queue_new_imgur_ids(env, imgur_ids)
    assert env.imgur_api_cache['image']


def test_query_imgur_api_imgur_api_test_response(monkeypatch, app):
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
    env.imgur_api_cache['image'] = dict(_mod_time=now - 50)
    api.query_imgur_api(app, env, '', 100, response)
    assert env.imgur_api_cache == dict(image=dict(_mod_time=now - 50))

    # Test predefined response.
    response = {
        'image': dict(description='This is a test image.', title='Test Image'),
        'a/album': dict(description='This is a test album.', title='Test Album', images=[
            dict(id='image2', description='This image is in an album.', title='Sub Image'),
            dict(id='image3', description='This image is also in an album.', title='Another Sub Image'),
        ]),
    }
    env.imgur_api_cache = dict()
    api.queue_new_imgur_ids(env, {'image', 'a/album'})
    assert sorted(env.imgur_api_cache.keys()) == ['a/album', 'image']
    assert not env.imgur_api_cache['image']['_mod_time']
    assert not env.imgur_api_cache['a/album']['_mod_time']
    api.query_imgur_api(app, env, '', 100, response)
    assert sorted(env.imgur_api_cache.keys()) == ['a/album', 'image', 'image2', 'image3']
    assert env.imgur_api_cache['image']['_mod_time'] == now
    assert env.imgur_api_cache['a/album']['_mod_time'] == now
    assert env.imgur_api_cache['image2']['_mod_time'] == now
    assert env.imgur_api_cache['image3']['_mod_time'] == now
    assert env.imgur_api_cache['image']['description'] == 'This is a test image.'
    assert env.imgur_api_cache['a/album']['description'] == 'This is a test album.'
    assert env.imgur_api_cache['image2']['description'] == 'This image is in an album.'
    assert env.imgur_api_cache['image3']['description'] == 'This image is also in an album.'
    assert env.imgur_api_cache['image']['title'] == 'Test Image'
    assert env.imgur_api_cache['a/album']['title'] == 'Test Album'
    assert env.imgur_api_cache['image2']['title'] == 'Sub Image'
    assert env.imgur_api_cache['image3']['title'] == 'Another Sub Image'
    assert not env.imgur_api_cache['image']['images']
    assert not env.imgur_api_cache['image2']['images']
    assert not env.imgur_api_cache['image3']['images']
    assert env.imgur_api_cache['a/album']['images'] == {'image2', 'image3'}

    # Test optimization.
    now += 50
    monkeypatch.setattr('time.time', lambda: now)
    response.pop('image')
    response['a/album']['title'] = 'The Test Album'
    env.imgur_api_cache['image2']['_mod_time'] = 0
    api.query_imgur_api(app, env, '', 100, response)
    assert env.imgur_api_cache['image']['_mod_time'] == now - 50
    assert env.imgur_api_cache['a/album']['_mod_time'] == now
    assert env.imgur_api_cache['image2']['_mod_time'] == now
    assert env.imgur_api_cache['image3']['_mod_time'] == now
    assert env.imgur_api_cache['a/album']['title'] == 'The Test Album'


def test_query_imgur_api_bad_client_id(monkeypatch, app):
    """Test with bad client_id value.

    :param monkeypatch: pytest fixture.
    :param app: conftest fixture.
    """
    monkeypatch.setattr(api, 'get_targeted_ids', lambda *_: {'image', 'a/album'})
    env = type('FakeEnv', (), {'imgur_api_cache': dict()})()
    response = dict()
    api.queue_new_imgur_ids(env, {'image', 'a/album'})

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
    api.queue_new_imgur_ids(env, {'image', 'a/album'})

    # Test just HTTPError.
    httpretty.register_uri(httpretty.GET, API_URL.format(type='album', id='album'), body='{}', status=500)
    httpretty.register_uri(httpretty.GET, API_URL.format(type='image', id='image'), body='{}', status=500)
    api.query_imgur_api(app, env, 'abc123abc123', 100, response)
    assert not env.imgur_api_cache['image']['_mod_time']
    assert not env.imgur_api_cache['a/album']['_mod_time']


@pytest.mark.httpretty
def test_query_imgur_api(monkeypatch, app):
    """Test with mocked urllib responses.

    :param monkeypatch: pytest fixture.
    :param app: conftest fixture.
    """
    monkeypatch.setattr(api, 'get_targeted_ids', lambda *_: {'image', 'a/album'})
    env = type('FakeEnv', (), {'imgur_api_cache': dict()})()
    response = dict()
    api.queue_new_imgur_ids(env, {'image', 'a/album'})

    # Test JSON response.
    def body(_, url, headers):
        rsp_all = {
            'image': dict(description='This is a test image.', title='Test Image'),
            'album': dict(description='This is a test album.', title='Test Album', images=[
                dict(id='image2', description='This image is in an album.', title='Sub Image'),
                dict(id='image3', description='This image is also in an album.', title='Another Sub Image'),
            ]),
        }
        rsp = [v for k, v in rsp_all.items() if url.endswith(k)][0]
        rsp_encoded = json.dumps(dict(data=rsp, success=True)).encode('utf-8')
        return 200, headers, rsp_encoded
    httpretty.register_uri(httpretty.GET, re.compile(API_URL.format(type='[^/]+', id=r'\w+')), body=body)
    api.query_imgur_api(app, env, 'abc123abc123', 100, response)
    assert sorted(env.imgur_api_cache.keys()) == ['a/album', 'image', 'image2', 'image3']
    assert env.imgur_api_cache['image']['_mod_time'] > 1438916421
    assert env.imgur_api_cache['a/album']['_mod_time'] > 1438916421
    assert env.imgur_api_cache['image2']['_mod_time'] > 1438916421
    assert env.imgur_api_cache['image3']['_mod_time'] > 1438916421
    assert env.imgur_api_cache['image']['description'] == 'This is a test image.'
    assert env.imgur_api_cache['a/album']['description'] == 'This is a test album.'
    assert env.imgur_api_cache['image2']['description'] == 'This image is in an album.'
    assert env.imgur_api_cache['image3']['description'] == 'This image is also in an album.'
    assert env.imgur_api_cache['image']['title'] == 'Test Image'
    assert env.imgur_api_cache['a/album']['title'] == 'Test Album'
    assert env.imgur_api_cache['image2']['title'] == 'Sub Image'
    assert env.imgur_api_cache['image3']['title'] == 'Another Sub Image'
    assert not env.imgur_api_cache['image']['images']
    assert not env.imgur_api_cache['image2']['images']
    assert not env.imgur_api_cache['image3']['images']
    assert env.imgur_api_cache['a/album']['images'] == {'image2', 'image3'}
