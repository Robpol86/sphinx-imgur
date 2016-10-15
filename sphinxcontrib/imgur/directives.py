"""Docutils directives for Imgur embeds."""

import re

from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.images import Image
from sphinx.application import SphinxError

from sphinxcontrib.imgur.nodes import ImgurEmbedNode, ImgurImageNode, ImgurJavaScriptNode

RE_IMGUR_ID = re.compile(r'^(?:a/)?[a-zA-Z0-9]{5,10}$')


def is_true(argument):
    """Return True if argument is the word "true" case insensitive.

    :param str argument: Argument/value passed to directive's option.

    :return: Is argument true/True/TRUE.
    :rtype: bool
    """
    return argument.lower() == 'true'


class ImgurError(SphinxError):
    """Non-configuration error. Raised when directive has bad options."""

    category = 'Imgur option error'


class ImgurEmbedDirective(Directive):
    """Imgur ".. imgur-embed::" rst directive for embedding albums/images with Imgur's JavaScript."""

    required_arguments = 1
    option_spec = dict(hide_post_details=is_true)

    def run(self):
        """Called by Sphinx.

        :returns: ImgurEmbedNode and ImgurJavaScriptNode instances with config values passed as arguments.
        :rtype: list
        """
        # Get Imgur ID.
        imgur_id = self.arguments[0]
        if not RE_IMGUR_ID.match(imgur_id):
            raise ImgurError('Invalid Imgur ID specified. Must be 5-10 letters and numbers. Albums prefixed with "a/".')

        # Read from conf.py.
        config = self.state.document.settings.env.config
        hide_post_details = self.options.get('hide_post_details', config.imgur_hide_post_details)

        return [ImgurEmbedNode(imgur_id, hide_post_details), ImgurJavaScriptNode()]


class ImgurImageDirective(Directive):
    """Imgur ".. imgur-image::" rst directive for inlining album covers and images from Imgur."""

    required_arguments = 1
    option_spec = dict(Image.option_spec, target_gallery=is_true, target_largest=is_true, target_page=is_true)

    def run(self):
        """Called by Sphinx.

        :returns: ImgurEmbedNode and ImgurJavaScriptNode instances with config values passed as arguments.
        :rtype: list
        """
        # Get Imgur ID.
        imgur_id = self.arguments[0]
        if not RE_IMGUR_ID.match(imgur_id):
            raise ImgurError('Invalid Imgur ID specified. Must be 5-10 letters and numbers. Albums prefixed with "a/".')

        # Validate directive options.
        if imgur_id.startswith('a/') and self.options.get('target_largest', None):
            raise ImgurError('Imgur albums (whose covers are displayed) do not support :target_largest: option.')

        # Modify options.
        if self.options.get('width', '').isdigit():
            self.options['width'] += 'px'
        if self.options.get('height', '').isdigit():
            self.options['height'] += 'px'

        # Read from conf.py. Unset gallery/largest/page targets if :target: is set.
        if self.options.get('target', None):
            self.options.pop('target_gallery', None)
            self.options.pop('target_largest', None)
            self.options.pop('target_page', None)
        elif not any(self.options.get('target_' + i, None) for i in ('gallery', 'largest', 'page')):
            config = self.state.document.settings.env.config
            self.options.setdefault('target_gallery', config.imgur_target_default_gallery)
            self.options.setdefault('target_largest', config.imgur_target_default_largest)
            self.options.setdefault('target_page', config.imgur_target_default_page)

        return [ImgurImageNode(imgur_id, self.options)]
