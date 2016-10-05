"""Docutils roles for Imgur inline text."""

from sphinxcontrib.imgur.directives import ImgurError, RE_IMGUR_ID
from sphinxcontrib.imgur.nodes import ImgurTextNode


def imgur_role(name, rawtext, text, *_):
    """Imgur ":imgur-title:`a/abc1234`" or ":imgur-description:`abc1234`" rst inline roles.

    "Schedules" an API query.

    :raises ImgurError: if text has invalid Imgur ID.

    :param str name: Role name (e.g. 'imgur-title').
    :param str rawtext: Entire role and value markup (e.g. ':imgur-title:`hWyW0`').
    :param str text: The parameter used in the role markup (e.g. 'hWyW0').

    :return: 2-item tuple of lists. First list are the rst nodes replacing the role. Second is a list of errors.
    :rtype: tuple
    """
    if not RE_IMGUR_ID.match(text):
        message = 'Invalid Imgur ID specified. Must be 5-10 letters and numbers. Got "{}" from "{}".'
        raise ImgurError(message.format(text, rawtext))
    node = ImgurTextNode(name, text)
    return [node], []
