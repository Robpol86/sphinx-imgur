"""Tests."""
from typing import List

import pytest
from bs4 import element


@pytest.mark.sphinx("html", testroot="embed")
def test_embed(blockquote_tags: List[element.Tag], img_tags: List[element.Tag]):
    """Test."""
    blockquote = blockquote_tags[0]
    assert blockquote.get("class") == ["imgur-embed-pub"]
    assert blockquote.get("data-id") == "a/hWyW0"
    assert blockquote.get("data-context") is None
    child = list(blockquote.children)[0]
    assert child.name == "a"
    assert child.get("href") == "https://imgur.com/a/hWyW0"
    script = blockquote.next_sibling
    assert script.name == "script"
    assert script.get("src") == "//s.imgur.com/min/embed.js"

    blockquote = blockquote_tags[1]
    assert blockquote.get("class") == ["imgur-embed-pub"]
    assert blockquote.get("data-id") == "611EovQ"
    assert blockquote.get("data-context") is None
    child = list(blockquote.children)[0]
    assert child.name == "a"
    assert child.get("href") == "https://imgur.com/611EovQ"
    script = blockquote.next_sibling
    assert script.name == "script"
    assert script.get("src") == "//s.imgur.com/min/embed.js"

    assert not img_tags


@pytest.mark.sphinx("html", testroot="embed-hide-post-details")
def test_embed_hide_post_details(blockquote_tags: List[element.Tag]):
    """Test."""
    blockquote = blockquote_tags[0]
    assert blockquote.get("class") == ["imgur-embed-pub"]
    assert blockquote.get("data-id") == "a/hWyW0"
    assert blockquote.get("data-context") == "false"

    blockquote = blockquote_tags[1]
    assert blockquote.get("class") == ["imgur-embed-pub"]
    assert blockquote.get("data-id") == "611EovQ"
    assert blockquote.get("data-context") == "false"


@pytest.mark.sphinx("html", testroot="embed-hide-post-details-config")
def test_embed_hide_post_details_config(blockquote_tags: List[element.Tag]):
    """Test."""
    blockquote = blockquote_tags[0]
    assert blockquote.get("class") == ["imgur-embed-pub"]
    assert blockquote.get("data-id") == "611EovQ"
    assert blockquote.get("data-context") == "false"


@pytest.mark.sphinx("html", testroot="embed-opengraph")
def test_embed_opengraph(meta_tags: List[element.Tag], img_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQh.jpg"
    og_image_alt = [t for t in meta_tags if t.get("property", "") == "og:image:alt"][0]
    assert og_image_alt.get("content") == "<no title>"

    assert not img_tags


@pytest.mark.sphinx("html", testroot="embed-opengraph-album")
def test_embed_opengraph_album(meta_tags: List[element.Tag], img_tags: List[element.Tag]):
    """Test."""
    og_images = [t for t in meta_tags if t.get("property", "") == "og:image"]
    assert not og_images
    og_image_alts = [t for t in meta_tags if t.get("property", "") == "og:image:alt"]
    assert not og_image_alts

    assert not img_tags


@pytest.mark.sphinx("html", testroot="embed-opengraph-alt")
def test_embed_opengraph_alt(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQh.jpg"
    og_image_alt = [t for t in meta_tags if t.get("property", "") == "og:image:alt"][0]
    assert og_image_alt.get("content") == "Help Text"


@pytest.mark.sphinx("html", testroot="embed-opengraph-fullsize")
def test_embed_opengraph_fullsize(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQ.jpg"


@pytest.mark.sphinx("html", testroot="embed-opengraph-img-src-format")
def test_embed_opengraph_img_src_format(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://robpol86.com/611EovQh.jpg"


@pytest.mark.sphinx("html", testroot="embed-opengraph-og-imgur-id")
def test_embed_opengraph_og_imgur_id(meta_tags: List[element.Tag], blockquote_tags: List[element.Tag]):
    """Test."""
    blockquote = blockquote_tags[0]
    assert blockquote.get("class") == ["imgur-embed-pub"]
    assert blockquote.get("data-id") == "a/hWyW0"
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/6nOHJ5Zh.jpg"


@pytest.mark.sphinx("html", testroot="embed-opengraph-size")
def test_embed_opengraph_size(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQl.jpg"


@pytest.mark.sphinx("html", testroot="embed-opengraph-size-implicit")
def test_embed_opengraph_size_implicit(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQs.jpg"


@pytest.mark.sphinx("html", testroot="embed-opengraph-ext")
def test_embed_opengraph_ext(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQh.jpeg"


@pytest.mark.sphinx("html", testroot="embed-opengraph-ext-implicit")
def test_embed_opengraph_ext_implicit(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQ.gif"
