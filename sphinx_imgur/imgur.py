"""Sphinx extension that embeds Imgur images and albums in documents.

https://sphinx-imgur.readthedocs.io
https://github.com/Robpol86/sphinx-imgur
https://pypi.org/project/sphinx-imgur
"""
from typing import Dict, List

from docutils.nodes import Element
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import images
from sphinx.application import Sphinx

from sphinx_imgur import __version__
from sphinx_imgur.nodes import ImgurEmbedNode, ImgurImageNode, ImgurJavaScriptNode
from sphinx_imgur.utils import is_true


class ImgurImage(Directive):
    """Imgur image directive."""

    option_spec = images.Image.option_spec.copy()
    option_spec["target_page"] = is_true
    required_arguments = 1

    def run(self) -> List[Element]:
        """Main method."""
        # Get Imgur ID.
        imgur_id = self.arguments[0]

        # Read from conf.py. Unset page targets if :target: is set.
        if self.options.get("target", None):
            self.options.pop("target_page", None)
        elif not any(self.options.get("target_" + i, None) for i in ("page",)):
            config = self.state.document.settings.env.config
            self.options.setdefault("target_page", config.imgur_target_default_page)

        # Determine target. Code in directives.py handles defaults and unsets target_* if :target: is set.
        if self.options.get("target_page", ""):
            self.options["target"] = "//imgur.com/{}".format(imgur_id)
        elif not self.options.get("target", "") and (
            self.options.get("width", "") or self.options.get("height", "") or self.options.get("scale", "")
        ):
            self.options["target"] = "//i.imgur.com/{}.jpg".format(imgur_id)

        return [ImgurImageNode(imgur_id, self.options)]


class ImgurEmbed(Directive):
    """Imgur embed directive."""

    option_spec = {
        "hide_post_details": is_true,
    }
    required_arguments = 1

    def run(self) -> List[Element]:
        """Main method."""
        # Get Imgur ID.
        imgur_id = self.arguments[0]

        # Read from conf.py.
        config = self.state.document.settings.env.config
        hide_post_details = self.options.get("hide_post_details", config.imgur_hide_post_details)

        return [ImgurEmbedNode(imgur_id, hide_post_details), ImgurJavaScriptNode()]


def event_doctree_resolved(__, doctree, _):  # pylint: disable=invalid-name
    """Called by Sphinx after phase 3 (resolving).

    * Call finalizer for ImgurImageNode nodes.

    :param docutils.nodes.document doctree: Tree of docutils nodes.
    :param _: Not used.
    """
    for node in doctree.traverse(ImgurImageNode):
        node.finalize()


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    """
    app.add_config_value("imgur_hide_post_details", False, True)
    app.add_config_value("imgur_target_default_page", False, True)

    app.add_directive("imgur-embed", ImgurEmbed)
    app.add_directive("imgur-image", ImgurImage)
    app.add_node(ImgurImageNode, html=(ImgurImageNode.html_visit, ImgurImageNode.html_depart))
    app.add_node(ImgurEmbedNode, html=(ImgurEmbedNode.html_visit, ImgurEmbedNode.html_depart))
    app.add_node(ImgurJavaScriptNode, html=(ImgurJavaScriptNode.html_visit, ImgurJavaScriptNode.html_depart))

    app.connect("doctree-resolved", event_doctree_resolved)

    return dict(version=__version__)
