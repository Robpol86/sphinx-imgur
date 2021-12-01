"""Docutils nodes for Imgur embeds."""
from docutils import nodes
from sphinx.writers.html5 import HTML5Translator


class ImgurEmbedNode(nodes.Element):
    """Imgur <blockquote><a /></blockquote> node for Sphinx/docutils."""

    def __init__(self, imgur_id: str, hide_post_details: bool):
        """Store directive options during instantiation.

        :param imgur_id: Imgur ID of the album or image.
        :param hide_post_details: Hide title and image descriptions in embedded albums or images.
        """
        super().__init__()
        self.imgur_id = imgur_id
        self.hide_post_details = hide_post_details

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "ImgurEmbedNode"):
        """Append opening tags to document body list."""
        html_attrs_bq = {"CLASS": "imgur-embed-pub", "lang": writer.settings.language_code, "data-id": node.imgur_id}
        if node.hide_post_details:
            html_attrs_bq["data-context"] = "false"
        writer.body.append(writer.starttag(node, "blockquote", "", **html_attrs_bq))
        html_attrs_ah = dict(href="https://imgur.com/{}".format(node.imgur_id), CLASS="reference external")
        writer.body.append(writer.starttag(node, "a", "Loading...", **html_attrs_ah))

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.extend(["</a>", "</blockquote>"])


class ImgurJavaScriptNode(nodes.Element):
    """JavaScript node required after each embedded album/image because Imgur sucks at JavaScript."""

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "ImgurJavaScriptNode"):
        """Append opening tags to document body list."""
        html_attrs_bq = {"async": "", "src": "//s.imgur.com/min/embed.js", "charset": "utf-8"}
        writer.body.append(writer.starttag(node, "script", "", **html_attrs_bq))

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.append("</script>")


class ImgurImageNode(nodes.Element):
    """Imgur image node for inline images."""

    def __init__(self, text, options):
        """Constructor.

        :param str text: The parameter used in the directive markup (e.g. 'hWyW0').
        :param dict options: Options from directive.
        """
        super().__init__()
        if text.startswith("a/"):
            raise NotImplementedError
        self.imgur_id = text
        self.options = dict(
            align=options.get("align", ""),
            alt=options.get("alt", ""),
            height=options.get("height", ""),
            scale=options.get("scale", ""),
            target=options.get("target", ""),
            target_page=options.get("target_page", ""),
            width=options.get("width", ""),
        )
        self.src = str()
        self.style = str()

    def finalize(self):
        """Update attributes after Sphinx cache is updated."""
        # Set src and style.
        self.src = "//i.imgur.com/{}h.jpg".format(self.imgur_id)
        style = [p for p in ((k, self.options[k]) for k in ("width", "height")) if p[1]]
        if style:
            self.style = "; ".join("{}: {}".format(k, v) for k, v in style)

        # Determine alt text.
        if not self.options["alt"]:
            self.options["alt"] = self.src[2:]

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "ImgurImageNode"):
        """Append opening tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator writer: Object to modify.
        :param sphinx_imgur.nodes.ImgurImageNode node: This class' instance.
        """
        if node.options["target"]:
            html_attrs_ah = dict(CLASS="reference external image-reference", href=node.options["target"])
            writer.body.append(writer.starttag(node, "a", "", **html_attrs_ah))

        html_attrs_img = dict(src=node.src, alt=node.options["alt"])
        if node.options["align"]:
            html_attrs_img["CLASS"] = "align-{}".format(node.options["align"])
        if node.style:
            html_attrs_img["style"] = node.style
        writer.body.append(writer.starttag(node, "img", "" if node.options["target"] else "\n", **html_attrs_img))

    @staticmethod
    def html_depart(writer: HTML5Translator, node: "ImgurImageNode"):
        """Append closing tags to document body list.

        :param sphinx.writers.html.SmartyPantsHTMLTranslator writer: Object to modify.
        :param sphinx_imgur.nodes.ImgurImageNode node: This class' instance.
        """
        if node.options["target"]:
            writer.body.append("</a>\n")
