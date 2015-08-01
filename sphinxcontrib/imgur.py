"""Sphinx extension that embeds Imgur images, albums, and their metadata in documents.

https://sphinxcontrib-imgur.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-imgur
https://pypi.python.org/pypi/sphinxcontrib-imgur
"""

from __future__ import print_function

import re

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import SphinxError

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '1.0.0'
RE_IMGUR_ID = re.compile(r'^[a-zA-Z0-9]{5,10}$')


class ImgurError(SphinxError):
    """Non-configuration error. Raised when directive has bad options."""

    category = 'Imgur option error'


class ImgurJavaScriptNode(nodes.General, nodes.Element):
    """JavaScript node required after each embedded album/image because Imgur sucks at JavaScript."""

    @staticmethod
    def visit(spht, node):
        """Append opening tags to document body list."""
        html_attrs_bq = {'async': '', 'src': '//s.imgur.com/min/embed.js', 'charset': 'utf-8'}
        spht.body.append(spht.starttag(node, 'script', '', **html_attrs_bq))

    @staticmethod
    def depart(spht, _):
        """Append closing tags to document body list."""
        spht.body.append('</script>')


class ImgurEmbedNode(nodes.General, nodes.Element):
    """Imgur <blockquote><a /></blockquote> node for Sphinx/docutils."""

    def __init__(self, imgur_id, is_album, hide_post_details):
        """Store directive options during instantiation.

        :param str imgur_id: Imgur ID of the album or image.
        :param bool is_album: Whether this block quote embeds an image or an album.
        :param bool hide_post_details: Hide title and image descriptions in embedded albums or images.
        """
        super(ImgurEmbedNode, self).__init__()
        self.imgur_id = imgur_id
        self.is_album = is_album
        self.hide_post_details = hide_post_details

    @staticmethod
    def visit(spht, node):
        """Append opening tags to document body list."""
        imgur_id = ('a/{}' if node.is_album else '{}').format(node.imgur_id)
        html_attrs_bq = {'CLASS': 'imgur-embed-pub', 'lang': spht.settings.language_code, 'data-id': imgur_id}
        if node.hide_post_details:
            html_attrs_bq['data-context'] = 'false'
        spht.body.append(spht.starttag(node, 'blockquote', '', **html_attrs_bq))
        html_attrs_ah = dict(href='https://imgur.com/{}'.format(imgur_id), CLASS='reference external')
        spht.body.append(spht.starttag(node, 'a', 'Loading...', **html_attrs_ah))

    @staticmethod
    def depart(spht, _):
        """Append closing tags to document body list."""
        spht.body.extend(['</a>', '</blockquote>'])


class ImgurEmbedDirective(Directive):
    """Imgur ".. imgur-embed::" rst directive for embedding albums/images with Imgur's JavaScript."""

    required_arguments = 1
    optional_arguments = 2
    option_spec = dict(album=lambda i: i.lower() == 'true', hide_post_details=lambda i: i.lower() == 'true')

    def get_id(self):
        """Validate and return the Imgur ID argument value.

        :returns: Imgur ID.
        :rtype: str
        """
        imgur_id = self.arguments[0]
        if not RE_IMGUR_ID.match(imgur_id):
            raise ImgurError('Invalid Imgur ID specified. Must be 5-10 letters and numbers.')
        return imgur_id

    def get_hide_post_details(self):
        """Handle both the config setting `imgur_hide_post_details` and directive option `hide_post_details`.

        :returns: Hide post details value.
        :rtype: bool
        """
        if 'hide_post_details' in self.options:
            return self.options['hide_post_details']
        return self.state.document.settings.env.config.imgur_hide_post_details

    def run(self):
        """Called by Sphinx.

        :returns: ImgurEmbedNode and ImgurJavaScriptNode instances with config values passed as arguments.
        :rtype: list
        """
        imgur_id = self.get_id()
        hide_post_details = self.get_hide_post_details()
        is_album = self.options.get('album')
        return [ImgurEmbedNode(imgur_id, is_album, hide_post_details), ImgurJavaScriptNode()]


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('imgur_hide_post_details', False, True)
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.visit, ImgurJavaScriptNode.depart))
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.visit, ImgurEmbedNode.depart))
    app.add_directive('imgur-embed', ImgurEmbedDirective)
    return dict(version=__version__)
