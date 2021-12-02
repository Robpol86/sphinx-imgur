"""Sphinx extension that embeds Imgur images and albums in documents.

https://sphinx-imgur.readthedocs.io
https://github.com/Robpol86/sphinx-imgur
https://pypi.org/project/sphinx-imgur
"""
from typing import Dict, List

from docutils.nodes import Element, SkipNode
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives import images
from sphinx.application import Sphinx

from sphinx_imgur import __version__
from sphinx_imgur.nodes import ImgurEmbedNode, ImgurJavaScriptNode, ImgurOmittedImageNode
from sphinx_imgur.utils import img_src_target_formats, imgur_id_size_ext

DEFAULT_EXT = "jpg"
DEFAULT_SIZE = "h"
IMG_SRC_FORMAT = "https://i.imgur.com/%(id)s%(size)s.%(ext)s"
TARGET_FORMAT = "https://imgur.com/%(id)s"


class ImgurImage(images.Image):
    """Imgur image directive."""

    option_spec = images.Image.option_spec.copy()
    option_spec["ext"] = directives.unchanged
    option_spec["fullsize"] = directives.flag
    option_spec["img_src_format"] = directives.unchanged
    option_spec["notarget"] = directives.flag
    option_spec["size"] = directives.single_char_or_unicode

    def run(self) -> List[Element]:
        """Main method."""
        config = self.state.document.settings.env.config
        imgur_id, size, ext = imgur_id_size_ext(self.arguments[0], self.options, config)
        img_src_format, target_format = img_src_target_formats(self.options, config)

        self.arguments[0] = img_src_format % {"id": imgur_id, "size": size, "ext": ext}
        if target_format:
            self.options["target"] = target_format % {"id": imgur_id, "size": size, "ext": ext}

        return super().run()


class ImgurFigure(images.Figure):
    """Imgur figure directive."""

    option_spec = images.Figure.option_spec.copy()
    option_spec["ext"] = directives.unchanged
    option_spec["fullsize"] = directives.flag
    option_spec["img_src_format"] = directives.unchanged
    option_spec["notarget"] = directives.flag
    option_spec["size"] = directives.single_char_or_unicode

    def run(self) -> List[Element]:
        """Main method."""
        config = self.state.document.settings.env.config
        imgur_id, size, ext = imgur_id_size_ext(self.arguments[0], self.options, config)
        img_src_format, target_format = img_src_target_formats(self.options, config)

        self.arguments[0] = img_src_format % {"id": imgur_id, "size": size, "ext": ext}
        if target_format:
            self.options["target"] = target_format % {"id": imgur_id, "size": size, "ext": ext}

        return super().run()


class ImgurEmbed(Directive):
    """Imgur embed directive."""

    required_arguments = 1
    option_spec = {
        "alt": directives.unchanged,
        "ext": directives.unchanged,
        "fullsize": directives.flag,
        "hide_post_details": directives.flag,
        "img_src_format": directives.unchanged,
        "og_imgur_id": directives.unchanged,
        "size": directives.single_char_or_unicode,
    }

    def run(self) -> List[Element]:
        """Main method."""
        config = self.state.document.settings.env.config
        imgur_id, size, ext = imgur_id_size_ext(self.arguments[0], self.options, config)
        hide_post_details = "hide_post_details" in self.options or config["imgur_hide_post_details"]

        node_embed = ImgurEmbedNode(imgur_id, hide_post_details)
        node_js = ImgurJavaScriptNode()
        nodes = [node_embed, node_js]

        # Hidden image node for opengraph.
        try:
            node_img = ImgurOmittedImageNode(self.block_text, self.options, config, imgur_id, size, ext)
        except SkipNode:
            pass
        else:
            nodes.append(node_img)

        return nodes


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    """
    app.add_config_value("imgur_default_ext", DEFAULT_EXT, "html")
    app.add_config_value("imgur_default_size", DEFAULT_SIZE, "html")
    app.add_config_value("imgur_hide_post_details", False, "html")
    app.add_config_value("imgur_img_src_format", IMG_SRC_FORMAT, "html")
    app.add_config_value("imgur_target_format", TARGET_FORMAT, "html")
    app.add_directive("imgur", ImgurImage)
    app.add_directive("imgur-embed", ImgurEmbed)
    app.add_directive("imgur-figure", ImgurFigure)
    app.add_directive("imgur-image", ImgurImage)
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.html_visit, ImgurEmbedNode.html_depart))
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.html_visit, ImgurJavaScriptNode.html_depart))
    app.add_node(ImgurOmittedImageNode, html=(ImgurOmittedImageNode.html_visit, ImgurOmittedImageNode.html_visit))
    return dict(version=__version__)
