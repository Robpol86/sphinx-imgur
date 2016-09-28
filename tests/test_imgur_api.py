"""Tests for the module."""

import re
import socket

import httpretty
import pytest

from sphinxcontrib.imgur.imgur_api import API_URL, APIError, query_api


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
    assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:50', app.messages[-1][2])


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
    assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:59$', app.messages[-1][2])


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
    assert re.search(r'sphinxcontrib[/\\]imgur[/\\]imgur_api\.pyc?:65$', app.messages[-1][2])


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
