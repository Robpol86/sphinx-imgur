"""Docutils nodes for Imgur embeds."""

from docutils.nodes import Element, General


class ImgurJavaScriptNode(General, Element):
    """JavaScript node required after each embedded album/image because Imgur sucks at JavaScript."""

    @staticmethod
    def visit(spht, node):
        """Append opening tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator spht: Object to modify.
        :param sphinxcontrib.imgur.nodes.ImgurJavaScriptNode node: This class' instance.
        """
        html_attrs_bq = {'async': '', 'src': '//s.imgur.com/min/embed.js', 'charset': 'utf-8'}
        spht.body.append(spht.starttag(node, 'script', '', **html_attrs_bq))

    @staticmethod
    def depart(spht, _):
        """Append closing tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator spht: Object to modify.
        :param _: Not used.
        """
        spht.body.append('</script>')


class ImgurEmbedNode(General, Element):
    """Imgur <blockquote><a /></blockquote> node for Sphinx/docutils."""

    def __init__(self, imgur_id, hide_post_details):
        """Store directive options during instantiation.

        :param str imgur_id: Imgur ID of the album or image.
        :param bool hide_post_details: Hide title and image descriptions in embedded albums or images.
        """
        super(ImgurEmbedNode, self).__init__()
        self.imgur_id = imgur_id
        self.hide_post_details = hide_post_details

    @staticmethod
    def visit(spht, node):
        """Append opening tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator spht: Object to modify.
        :param sphinxcontrib.imgur.nodes.ImgurEmbedNode node: This class' instance.
        """
        html_attrs_bq = {'CLASS': 'imgur-embed-pub', 'lang': spht.settings.language_code, 'data-id': node.imgur_id}
        if node.hide_post_details:
            html_attrs_bq['data-context'] = 'false'
        spht.body.append(spht.starttag(node, 'blockquote', '', **html_attrs_bq))
        html_attrs_ah = dict(href='https://imgur.com/{}'.format(node.imgur_id), CLASS='reference external')
        spht.body.append(spht.starttag(node, 'a', 'Loading...', **html_attrs_ah))

    @staticmethod
    def depart(spht, _):
        """Append closing tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator spht: Object to modify.
        :param _: Not used.
        """
        spht.body.extend(['</a>', '</blockquote>'])


class ImgurTextNode(General, Element):
    """Imgur text node for image/album descriptions. To be replaced with docutils.nodes.Text."""

    def __init__(self, name, text):
        """Constructor.

        :param str name: Role name (e.g. 'imgur-title').
        :param str text: The parameter used in the role markup (e.g. 'hWyW0').
        """
        super(ImgurTextNode, self).__init__()
        self.name = name
        self.album = text.startswith('a/')
        self.imgur_id = text[2:] if self.album else text


class ImgurImageNode(General, Element):
    """Imgur image node for inline images."""

    def __init__(self, text, options):
        """Constructor.

        :param str text: The parameter used in the directive markup (e.g. 'hWyW0').
        :param dict options: Options from directive.
        """
        super(ImgurImageNode, self).__init__()
        self.album = text.startswith('a/')
        self.imgur_id = text[2:] if self.album else text
        self.options = dict(
            align=options.get('align', None),
            alt=options.get('alt', None),
            target=options.get('target', None),
            target_gallery=options.get('target_gallery', None),
            target_largest=options.get('target_largest', None),
            target_page=options.get('target_page', None),
        )
        self.src = str()

    def finalize(self, album_cache, image_cache):
        """Update attributes after Sphinx cache is updated.

        :param dict album_cache: Cache of Imgur albums to read. Keys are Imgur IDs, values are Album instances.
        :param dict image_cache: Cache of Imgur images to read. Keys are Imgur IDs, values are Image instances.
        """
        album = album_cache[self.imgur_id] if self.album else None
        image = image_cache[album.cover_id] if self.album else image_cache[self.imgur_id]
        if image.type in ('image/png', 'image/gif'):
            extension = image.type[-3:]
        else:
            extension = 'jpg'
        self.src = '//i.imgur.com/{}.{}'.format(image.imgur_id, extension)

        # Determine alt text.
        if not self.options['alt']:
            self.options['alt'] = image.title or self.src[2:]

        # Determine target. Code in directives.py handles defaults and unsets target_* if :target: is set.
        if self.options['target_gallery'] and (album.in_gallery if album else image.in_gallery):
            self.options['target'] = '//imgur.com/gallery/{}'.format(album.imgur_id if album else image.imgur_id)
        elif self.options['target_page']:
            self.options['target'] = '//imgur.com/{}'.format(album.imgur_id if album else image.imgur_id)
        elif self.options['target_largest'] and not album:
            imgur_id = album.imgur_id if album else image.imgur_id
            self.options['target'] = '//i.imgur.com/{}.{}'.format(imgur_id, extension)

    @staticmethod
    def visit(spht, node):
        """Append opening tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator spht: Object to modify.
        :param sphinxcontrib.imgur.nodes.ImgurImageNode node: This class' instance.
        """
        if node.options['target']:
            html_attrs_ah = dict(CLASS='reference external image-reference', href=node.options['target'])
            spht.body.append(spht.starttag(node, 'a', '', **html_attrs_ah))

        html_attrs_img = dict(src=node.src, alt=node.options['alt'])
        if node.options['align']:
            html_attrs_img['CLASS'] = 'align-{}'.format(node.options['align'])
        spht.body.append(spht.starttag(node, 'img', '', **html_attrs_img))

    @staticmethod
    def depart(spht, node):
        """Append closing tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator spht: Object to modify.
        :param sphinxcontrib.imgur.nodes.ImgurImageNode node: This class' instance.
        """
        if node.options['target']:
            spht.body.append('</a>')
