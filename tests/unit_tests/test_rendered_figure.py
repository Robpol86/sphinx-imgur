"""Tests."""
from typing import List

import pytest
from bs4 import element


@pytest.mark.sphinx("html", testroot="figure")
def test_figure(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    assert image.get("alt") == "https://i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name != "a"

    image = img_tags[1]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    assert image.get("alt") == "https://i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"


@pytest.mark.sphinx("html", testroot="figure-opengraph")
def test_figure_opengraph(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQh.jpg"
    og_image_alt = [t for t in meta_tags if t.get("property", "") == "og:image:alt"][0]
    assert og_image_alt.get("content") == "<no title>"


@pytest.mark.sphinx("html", testroot="figure-opengraph-alt")
def test_opengraph_alt(meta_tags: List[element.Tag]):
    """Test."""
    og_image = [t for t in meta_tags if t.get("property", "") == "og:image"][0]
    assert og_image.get("content") == "https://i.imgur.com/611EovQh.jpg"
    og_image_alt = [t for t in meta_tags if t.get("property", "") == "og:image:alt"][0]
    assert og_image_alt.get("content") == "Alt Text"
