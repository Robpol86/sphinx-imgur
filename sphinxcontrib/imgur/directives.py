"""Docutils directives for Imgur embeds."""

import re

from docutils.parsers.rst import Directive
from sphinx.application import SphinxError

from sphinxcontrib.imgur.nodes import ImgurEmbedNode, ImgurJavaScriptNode

RE_IMGUR_ID = re.compile(r'^(?:a/)?[a-zA-Z0-9]{5,10}$')


class ImgurError(SphinxError):
    """Non-configuration error. Raised when directive has bad options."""

    category = 'Imgur option error'


class ImgurEmbedDirective(Directive):
    """Imgur ".. imgur-embed::" rst directive for embedding albums/images with Imgur's JavaScript."""

    required_arguments = 1
    option_spec = dict(hide_post_details=lambda i: i.lower() == 'true')

    def run(self):
        """Called by Sphinx.

        :returns: ImgurEmbedNode and ImgurJavaScriptNode instances with config values passed as arguments.
        :rtype: list
        """
        # Get Imgur ID.
        imgur_id = self.arguments[0]
        if not RE_IMGUR_ID.match(imgur_id):
            raise ImgurError('Invalid Imgur ID specified. Must be 5-10 letters and numbers. Albums prefixed with "a/".')

        # Hide post details?
        config = self.state.document.settings.env.config
        hide_post_details = self.options.get('hide_post_details', config.imgur_hide_post_details)

        return [ImgurEmbedNode(imgur_id, hide_post_details), ImgurJavaScriptNode()]
