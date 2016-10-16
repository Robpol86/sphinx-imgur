"""Docutils nodes for Imgur embeds."""

import re

from docutils.nodes import Element, General

RE_WIDTH_HEIGHT = re.compile(r'([0-9.]+)(\S*)$')  # From: docutils/writers/html4css1/__init__.py


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
            align=options.get('align', ''),
            alt=options.get('alt', ''),
            height=options.get('height', ''),
            scale=options.get('scale', ''),
            target=options.get('target', ''),
            target_gallery=options.get('target_gallery', ''),
            target_largest=options.get('target_largest', ''),
            target_page=options.get('target_page', ''),
            width=options.get('width', ''),
        )
        self.src = str()
        self.style = str()

    def finalize(self, album_cache, image_cache, warn_node):
        """Update attributes after Sphinx cache is updated.

        :param dict album_cache: Cache of Imgur albums to read. Keys are Imgur IDs, values are Album instances.
        :param dict image_cache: Cache of Imgur images to read. Keys are Imgur IDs, values are Image instances.
        :param function warn_node: sphinx.environment.BuildEnvironment.warn_node without needing node argument.
        """
        album = album_cache[self.imgur_id] if self.album else None
        image = image_cache[album.cover_id] if self.album else image_cache[self.imgur_id]
        options = self.options

        # Determine target. Code in directives.py handles defaults and unsets target_* if :target: is set.
        if options['target_gallery'] and (album.in_gallery if album else image.in_gallery):
            options['target'] = '//imgur.com/gallery/{}'.format(album.imgur_id if album else image.imgur_id)
        elif options['target_page']:
            options['target'] = '//imgur.com/{}'.format(album.imgur_id if album else image.imgur_id)
        elif options['target_largest'] and not album:
            options['target'] = '//i.imgur.com/' + image.filename(full_size=True)
        elif not options['target'] and (options['width'] or options['height'] or options['scale']):
            options['target'] = '//i.imgur.com/' + image.filename(full_size=True)

        # Handle scale with no API data.
        if options['scale']:
            if not image.width and not options['width'] and not image.height and not options['height']:
                options['scale'] = ''
                warn_node('Could not obtain image size. :scale: option is ignored.')
            elif not image.width and not options['width']:
                warn_node('Could not obtain image width. :scale: option is partially ignored.')
            elif not image.width or not image.height:
                warn_node('Could not obtain image height. :scale: option is partially ignored.')

        # Handle scale, width, and height.
        if options['scale'] and (options['width'] or image.width):
            match = RE_WIDTH_HEIGHT.match(options['width'] or '%dpx' % image.width)
            options['width'] = '{}{}'.format(int(float(match.group(1)) * (options['scale'] / 100.0)), match.group(2))
        if options['scale'] and (options['height'] or image.height):
            match = RE_WIDTH_HEIGHT.match(options['height'] or '%dpx' % image.height)
            options['height'] = '{}{}'.format(int(float(match.group(1)) * (options['scale'] / 100.0)), match.group(2))

        # Set src and style.
        self.src = '//i.imgur.com/' + image.filename(options['width'], options['height'])
        style = [p for p in ((k, options[k]) for k in ('width', 'height')) if p[1]]
        if style:
            self.style = '; '.join('{}: {}'.format(k, v) for k, v in style)

        # Determine alt text.
        if not options['alt']:
            options['alt'] = image.title or self.src[2:]

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
        if node.style:
            html_attrs_img['style'] = node.style
        spht.body.append(spht.starttag(node, 'img', '', **html_attrs_img))

    @staticmethod
    def depart(spht, node):
        """Append closing tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator spht: Object to modify.
        :param sphinxcontrib.imgur.nodes.ImgurImageNode node: This class' instance.
        """
        if node.options['target']:
            spht.body.append('</a>')
