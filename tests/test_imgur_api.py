"""Tests for the module."""

import re
import socket

import httpretty
import pytest

from sphinxcontrib.imgur.imgur_api import Album, API_URL, APIError, Image, query_api


@pytest.mark.parametrize('timeout', [True, False])
def test_query_api_timeout_connection_error(monkeypatch, request, app, timeout):
    """Test if API is unresponsive.

    Asserting line number of: response = requests.get(url, headers=headers, timeout=timeout)

    :param monkeypatch: pytest fixture.
    :param request: pytest fixture.
    :param app: conftest fixture.
    :param bool timeout: Test timeout instead of connection error.
    """
    # Listen on a random port.
    server = socket.socket()
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    api_url = 'https://%s/{type}/{id}' % '{}:{}'.format(*server.getsockname())
    if timeout:
        request.addfinalizer(lambda: server.close())
    else:
        server.close()  # Opened just to get unused port number.
    monkeypatch.setattr('sphinxcontrib.imgur.imgur_api.API_URL', api_url)

    # Test.
    with pytest.raises(APIError):
        query_api(app, 'client_id', 'imgur_id', False)

    # Verify log.
    if timeout:
        assert app.messages[-1][1].startswith('timed out waiting for reply from http')
    else:
        assert app.messages[-1][1].startswith('unable to connect to http')
    assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:51', app.messages[-1][2])


@pytest.mark.httpretty
def test_query_api_non_json(app):
    """Test when API returns something other than JSON.

    Asserting line number of: parsed = response.json()

    :param app: conftest fixture.
    """
    url = API_URL.format(type='image', id='imgur_id')
    httpretty.register_uri(httpretty.GET, url, body='<html></html>')

    # Test.
    with pytest.raises(APIError):
        query_api(app, 'client_id', 'imgur_id', False)

    # Verify log.
    assert app.messages[0] == ['info', 'querying {}'.format(url)]
    assert app.messages[1] == ['debug2', 'Imgur API responded with: <html></html>']
    assert app.messages[2][:2] == ['warn', 'failed to parse JSON from {}'.format(url)]
    assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:60$', app.messages[-1][2])


@pytest.mark.parametrize('bad_json', [False, True])
@pytest.mark.httpretty
def test_query_api_not_success(app, bad_json):
    """Test non-successful replies or unexpected JSON data.

    Asserting line number of: raise APIError('query unsuccessful from {}...

    :param app: conftest fixture.
    :param bool bad_json: Unexpected JSON.
    """
    if bad_json:
        body = '{}'
        status = 200
        error = 'N/A'
    else:
        body = '{"data":{"error":"Authentication required","method":"GET"},"success":false,"status":401}'
        status = 401
        error = 'Authentication required'
    url = API_URL.format(type='album', id='imgur_id')
    httpretty.register_uri(httpretty.GET, url, body=body, status=status)

    # Test.
    with pytest.raises(APIError):
        query_api(app, 'client_id', 'imgur_id', True)

    # Verify log.
    assert app.messages[0] == ['info', 'querying {}'.format(url)]
    assert app.messages[1] == ['debug2', 'Imgur API responded with: %s' % body]
    assert app.messages[2][:2] == ['warn', 'query unsuccessful from {}: {}'.format(url, error)]
    assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:66$', app.messages[-1][2])


@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_query_api_valid(app):
    """Test working response.

    :param app: conftest fixture.
    """
    actual = query_api(app, 'client_id', 'V76cJ', True)

    assert actual['status'] == 200
    assert actual['success'] is True
    assert actual['data']['id'] == 'V76cJ'
    assert actual['data']['title'] == '2010 JSW, 2012 Projects'


@pytest.mark.parametrize('error', ['not json', 'no data', 'no title'])
@pytest.mark.parametrize('is_album', [False, True])
@pytest.mark.httpretty
def test_image_album_refresh_error(app, error, is_album):
    """Test Image.refresh() and Album.refresh() with bad JSON.

    Asserting line number of: parsed = response.json()
    Asserting line number of: return self._parse(response['data'])

    :param app: conftest fixture.
    :param str error: Error to test for.
    :param bool is_album: Test Album instead of Image.
    """
    url = API_URL.format(type='album' if is_album else 'image', id='imgur_id')
    if error == 'not json':
        body = '<html></html>'
    elif error == 'no data':
        body = '{"success":true}'
    else:
        body = '{"success":true, "data":{"id":"imgur_id"}}'
    httpretty.register_uri(httpretty.GET, url, body=body)

    # Test.
    instance = Album('imgur_id') if is_album else Image('imgur_id')
    with pytest.raises(APIError):
        instance.refresh(app, 'client_id', 30)

    # Verify log.
    if error == 'not json':
        assert app.messages[-1][:2] == ['warn', 'failed to parse JSON from {}'.format(url)]
        assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:60$', app.messages[-1][2])
    elif error == 'no data':
        assert app.messages[-1][:2] == ['warn', "unexpected JSON for imgur_id: KeyError('data',)"]
        assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:138$', app.messages[-1][2])
    else:
        assert app.messages[-1][:2] == ['warn', "unexpected JSON for imgur_id: KeyError('title',)"]
        assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:138$', app.messages[-1][2])


@pytest.mark.httpretty
def test_album_minor_error(app):
    """Test Album.refresh() with bad images JSON.

    Asserting line number of: return self._parse(response['data'])

    :param app: conftest fixture.
    """
    url = API_URL.format(type='album', id='imgur_id')
    body = '{"success":true, "data":{"id":"imgur_id", "title": null, "description": null, "images": [{}]}}'
    httpretty.register_uri(httpretty.GET, url, body=body)

    # Test.
    instance = Album('imgur_id')
    with pytest.raises(APIError):
        instance.refresh(app, 'client_id', 30)

    # Verify log.
    assert app.messages[-1][:2] == ['warn', "unexpected JSON for imgur_id: KeyError('id',)"]
    assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:138$', app.messages[-1][2])


@pytest.mark.parametrize('is_album', [False, True])
@pytest.mark.usefixtures('httpretty_common_mock')
@pytest.mark.httpretty
def test_image_album_refresh_ttl(app, is_album):
    """Test Image.refresh() and Album.refresh() successfully with ttl.

    :param app: conftest fixture.
    :param bool is_album: Test Album instead of Image.
    """
    if is_album:
        imgur_id = 'VMlM6'
        title = 'Screenshots'
        description = 'Screenshots of my various devices.'
        line = ['debug2', 'Imgur ID VMlM6 still has 30 seconds before needing refresh. Skipping.']
    else:
        imgur_id = '2QcXR3R'
        title = None
        description = None
        line = ['debug2', 'Imgur ID 2QcXR3R still has 30 seconds before needing refresh. Skipping.']

    # Test.
    instance = Album(imgur_id) if is_album else Image(imgur_id)
    instance.refresh(app, 'client_id', 30)

    # Verify instance.
    assert instance.imgur_id == imgur_id
    assert instance.title == title
    assert instance.description == description
    if is_album:
        assert instance.image_ids == ['2QcXR3R', 'Hqw7KHM']
        assert '2QcXR3R' in instance
        assert 'Hqw7KHM' in instance
        assert 'abc123' not in instance

    # Verify log.
    assert line not in app.messages

    # Test again.
    instance.refresh(app, 'client_id', 30)

    # Verify instance.
    assert instance.imgur_id == imgur_id
    assert instance.title == title
    assert instance.description == description
    if is_album:
        assert instance.image_ids == ['2QcXR3R', 'Hqw7KHM']
        assert '2QcXR3R' in instance
        assert Image('Hqw7KHM') in instance
        assert 'abc123' not in instance

    # Verify log.
    assert line in app.messages


@pytest.mark.parametrize('is_album', [False, True])
@pytest.mark.parametrize('error', [None, KeyError, APIError])
@pytest.mark.httpretty
def test_image_album_refresh_mock(app, error, is_album):
    """Test Image.refresh() and Album.refresh() with mocked data from Sphinx config.

    :param app: conftest fixture.
    :param exception error: Test this kind of error.
    :param bool is_album: Test Album instead of Image.
    """
    mock_data = app.config['imgur_api_test_response_albums' if is_album else 'imgur_api_test_response_images']
    if not error:
        mock_data['imgur_id'] = dict(success=True, status=200, data=dict(title='One', description='Two'))
        if is_album:
            mock_data['imgur_id']['data']['images'] = []
    elif error == KeyError:
        mock_data['other'] = dict()  # imgur_id not defined.
    else:
        mock_data['imgur_id'] = dict()

    # Test.
    instance = Album('imgur_id') if is_album else Image('imgur_id')
    if error:
        with pytest.raises(error):
            instance.refresh(app, 'client_id', 30)
    else:
        instance.refresh(app, 'client_id', 30)

    # Verify instance.
    if error:
        assert instance.title == ''
        assert instance.description == ''
    else:
        assert instance.title == 'One'
        assert instance.description == 'Two'
    assert instance.imgur_id == 'imgur_id'

    # Verify log.
    merged = '\n'.join('\t'.join(m) for m in app.messages)
    if is_album:
        assert 'loading mock response for imgur_id from imgur_api_test_response_albums' in merged
    else:
        assert 'loading mock response for imgur_id from imgur_api_test_response_images' in merged