"""Query the Imgur API."""

import inspect
import sys
import time

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
        if 'data' not in parsed:
            message = 'no "data" key in JSON'
        elif 'error' not in parsed['data']:
            message = 'no "error" key in JSON'
        else:
            message = parsed['data']['error']
        raise APIError('query unsuccessful from {}: {}'.format(url, message), app)

    return parsed


class Base(object):
    """Base class for Image and Album classes. Defines common attributes."""

    KIND = None

    def __init__(self, imgur_id, data=None):
        """Constructor.

        :param str imgur_id: The Imgur ID to query.
        :param dict data: Parsed JSON response from API.
        """
        self.description = str()
        self.imgur_id = imgur_id
        self.in_gallery = False
        self.mod_time = 0
        self.title = str()
        if data:
            self._parse(data)

    def _parse(self, data):
        """Parse API response.

        :param dict data: Parsed JSON response from API 'data' key.
        """
        self.description = data['description']
        self.in_gallery = data['in_gallery']
        self.mod_time = int(time.time())
        self.title = data['title']

    def seconds_remaining(self, ttl):
        """Return number of seconds left before Imgur API needs to be queried for this instance.

        :param int ttl: Number of seconds before this is considered out of date.

        :return: Seconds left before this is expired. 0 indicated update needed (no negatives).
        :rtype: int
        """
        return max(0, ttl - (int(time.time()) - self.mod_time))

    def refresh(self, app, client_id, ttl):
        """Query the API to update this instance.

        :raise APIError: When Imgur responds with errors or unexpected data.

        :param sphinx.application.Sphinx app: Sphinx application object.
        :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
        :param int ttl: Number of seconds before this is considered out of date.
        """
        remaining = self.seconds_remaining(ttl)
        if remaining:
            app.debug2('Imgur ID %s still has %d seconds before needing refresh. Skipping.', self.imgur_id, remaining)
            return

        # Retrieve data.
        response = query_api(app, client_id, self.imgur_id, self.KIND == 'album')

        # Parse.
        try:
            return self._parse(response['data'])
        except KeyError as exc:
            raise APIError('unexpected JSON for {}: {}'.format(self.imgur_id, repr(exc)), app)


class Image(Base):
    """Imgur image metadata."""

    KIND = 'image'

    def __init__(self, imgur_id, data=None):
        """Constructor.

        :param str imgur_id: The Imgur ID to query.
        :param dict data: Parsed JSON response from API.
        """
        self.height = 0
        self.type = str()
        self.width = 0
        super(Image, self).__init__(imgur_id, data)

    def _parse(self, data):
        """Parse API response.

        :param dict data: Parsed JSON response from API 'data' key.
        """
        super(Image, self)._parse(data)
        self.height = data['height']
        self.type = data['type']
        self.width = data['width']

    def filename(self, display_width='', display_height='', full_size=False):
        """Determine which resized Imgur filename to use based on the display width/height. Includes the extension.

        :param str display_width: Display width from Sphinx directive options (e.g. '100px', '50%').
        :param str display_height: Display height from Sphinx directive options (e.g. '100px', '50%').
        :param bool full_size: Always return the original full size image filename.

        :return: The filename to use in <img src="...">.
        :rtype: str
        """
        extension = self.type[-3:] if self.type in ('image/png', 'image/gif') else 'jpg'
        if extension == 'gif' or full_size:
            return '{}.{}'.format(self.imgur_id, extension)  # Imgur doesn't animate resized versions.
        size = 'h'  # Default is 'huge' since all Sphinx themes limit document width to < 1024px.
        if (not display_width and not display_height) or not self.width or not self.height:
            return '{}{}.{}'.format(self.imgur_id, size, extension)

        # Parse display_width and display_height.
        if display_width.endswith('px'):
            width = int(display_width[:-2])
        elif display_width.endswith('%'):
            width = self.width * (int(display_width[:-1]) / 100.0)
        elif display_height.endswith('px'):
            width = (self.width * int(display_height[:-2])) / self.height
        else:
            width = self.width

        # Determine size.
        if width <= 160:
            size = 't'
        elif width <= 320:
            size = 'm'
        elif width <= 640:
            size = 'l'
        return '{}{}.{}'.format(self.imgur_id, size, extension)


class Album(Base):
    """Imgur album metadata."""

    KIND = 'album'

    def __init__(self, imgur_id, data=None):
        """Constructor.

        :param str imgur_id: The Imgur ID to query.
        :param dict data: Parsed JSON response from API.
        """
        self.cover_id = str()
        self.image_ids = list()
        super(Album, self).__init__(imgur_id, data)

    def __contains__(self, item):
        """Search for images in this album.

        :param item: Imgur ID string or Image instance to search for in self.images.

        :return: If image is in this album.
        :rtype: bool
        """
        if hasattr(item, 'imgur_id'):
            # item is an Image instance.
            return item.imgur_id in self.image_ids
        return item in self.image_ids

    def _parse(self, data):
        """Parse API response.

        :param dict data: Parsed JSON response from API 'data' key.

        :return: Image instances.
        :rtype: list.
        """
        super(Album, self)._parse(data)
        self.cover_id = data['cover']
        images = [Image(i['id'], i) for i in data['images']]
        self.image_ids[:] = [i.imgur_id for i in images]
        return images

    def refresh(self, app, client_id, ttl):
        """Query the API to update this instance.

        :raise APIError: When Imgur responds with errors or unexpected data.

        :param sphinx.application.Sphinx app: Sphinx application object.
        :param str client_id: Imgur API client ID to use. https://api.imgur.com/oauth2
        :param int ttl: Number of seconds before this is considered out of date.

        :return: self._parse() return value.
        :rtype: list
        """
        return super(Album, self).refresh(app, client_id, ttl) or list()
