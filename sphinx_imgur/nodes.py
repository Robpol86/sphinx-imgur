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
