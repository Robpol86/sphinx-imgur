"""Docutils nodes for Imgur embeds."""

from docutils.nodes import Element, General


class ImgurJavaScriptNode(General, Element):
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


class ImgurEmbedNode(General, Element):
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
