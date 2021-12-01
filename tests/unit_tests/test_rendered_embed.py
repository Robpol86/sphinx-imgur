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
