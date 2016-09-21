"""Query the Imgur API."""

import inspect
import sys

import requests
import requests.exceptions

API_URL = 'https://api.imgur.com/3/{type}/{id}'


class APIError(Exception):
    """Imgur API error."""

    def __init__(self, message, app):
        """Constructor.

        :param str message: Message to log.
        :param sphinx.application.Sphinx app: Sphinx application object.
        """
        try:
            line_number = sys.exc_info()[-1].tb_lineno
        except AttributeError:
            line_number = inspect.currentframe().f_back.f_lineno
        self.message = message
        super(APIError, self).__init__(message, app, line_number)
        app.warn(message, location='{}:{}'.format(__file__, line_number))


def query_api(app, client_id, imgur_id, is_album):
    """Query the Imgur API.

    :raise APIError: When Imgur responds with errors or unexpected data.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
    :param str imgur_id: The Imgur ID to query.
    :param bool is_album: If this ID is an album instead of an image.

    :return: Parsed JSON.
    :rtype: dict
    """
    url = API_URL.format(type='album' if is_album else 'image', id=imgur_id)
    headers = {'Authorization': 'Client-ID {}'.format(client_id)}
    timeout = 5

    # Query.
    app.info('querying {}'.format(url))
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.Timeout) as exc:
        raise APIError('timed out waiting for reply from {}: {}'.format(url, str(exc)), app)
    except requests.ConnectionError as exc:
        raise APIError('unable to connect to {}: {}'.format(url, str(exc)), app)
    app.debug2('Imgur API responded with: %s', response.text)

    # Parse JSON.
    try:
        parsed = response.json()
    except ValueError:
        raise APIError('failed to parse JSON from {}'.format(url), app)

    # Verify data.
    if not parsed.get('success'):
        raise APIError('query unsuccessful from {}: {}'.format(url, parsed.get('data', {}).get('error', 'N/A')), app)

    return parsed
