"""Docutils nodes for Imgur embeds."""
from typing import Any, Dict

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator

from sphinx_imgur.utils import img_src_target_formats, imgur_id_size_ext


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


class ImgurOmittedImageNode(nodes.image):
    """Hidden image node not included in output. Used for opengraph compatibility."""

    def __init__(self, block_text: str, options: Dict[str, Any], config: Dict[str, Any], imgur_id: str, size: str, ext: str):
        """Generate URL for hidden image.

        :param block_text: Raw rst text, probably not used by parent class.
        :param options: Embed directive options.
        :param config: Sphinx config.
        :param imgur_id: Imgur ID from embed directive.
        :param size: Opengraph image size from embed directive.
        :param ext: Opengraph image extension from embed directive.
        """
        img_src_format, _ = img_src_target_formats(options, config)
        if "og_imgur_id" in options:
            imgur_id, size, ext = imgur_id_size_ext(options["og_imgur_id"], options, config)
        if imgur_id.startswith("a/"):
            # No hidden image when all we have is an album.
            raise nodes.SkipNode
        uri = img_src_format % {"id": imgur_id, "size": size, "ext": ext}
        super().__init__(block_text, uri=uri, **options)

    @staticmethod
    def html_visit(writer: HTML5Translator, _):
        """Always tell Sphinx writers to skip this node."""
        raise nodes.SkipNode
