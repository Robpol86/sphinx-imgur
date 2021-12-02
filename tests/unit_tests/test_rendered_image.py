"""Tests."""
from typing import List

import pytest
from bs4 import element


@pytest.mark.sphinx("html", testroot="image")
def test_image(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "//i.imgur.com/611EovQh.jpg"
    assert image.get("alt") == "i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "//imgur.com/611EovQ"


@pytest.mark.sphinx("html", testroot="image-target")
def test_image_target(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "//i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://robpol86.com"
