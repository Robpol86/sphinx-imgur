"""Tests."""
from typing import Dict, List

import pytest
from bs4 import element
from TexSoup import TexNode


@pytest.mark.sphinx("html", testroot="image")
def test_image(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    assert image.get("alt") == "https://i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"

    image = img_tags[1]
    assert image.get("src") == "https://i.imgur.com/611EovQ.jpg"
    assert image.get("alt") == "https://i.imgur.com/611EovQ.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"

    image = img_tags[2]
    assert image.get("src") == "https://i.imgur.com/611EovQ.jpeg"
    assert image.get("alt") == "https://i.imgur.com/611EovQ.jpeg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"

    image = img_tags[3]
    assert image.get("src") == "https://i.imgur.com/611EovQm.jpg"
    assert image.get("alt") == "https://i.imgur.com/611EovQm.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"

    image = img_tags[4]
    assert image.get("src") == "https://i.imgur.com/611EovQm.jpg"
    assert image.get("alt") == "https://i.imgur.com/611EovQm.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"

    image = img_tags[5]
    assert image.get("src") == "https://i.imgur.com/611EovQm.jpeg"
    assert image.get("alt") == "https://i.imgur.com/611EovQm.jpeg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"


@pytest.mark.sphinx("html", testroot="image-directive-alias")
def test_image_directive_alias(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    assert image.get("alt") == "https://i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://imgur.com/611EovQ"


@pytest.mark.sphinx("html", testroot="image-ext")
def test_image_ext(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpeg"
    image = img_tags[1]
    assert image.get("src") == "https://i.imgur.com/611EovQ.jpeg"
    image = img_tags[2]
    assert image.get("src") == "https://i.imgur.com/611EovQ.jpg"
    image = img_tags[3]
    assert image.get("src") == "https://i.imgur.com/611EovQh.png"
    image = img_tags[4]
    assert image.get("src") == "https://i.imgur.com/611EovQ.png"
    image = img_tags[5]
    assert image.get("src") == "https://i.imgur.com/611EovQ.png"


@pytest.mark.sphinx("html", testroot="image-img-src-format")
def test_image_img_src_format(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://robpol86.com/611EovQh.jpg"


@pytest.mark.sphinx("html", testroot="image-implicit")
def test_image_implicit(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    image = img_tags[1]
    assert image.get("src") == "https://i.imgur.com/611EovQ.gif"
    image = img_tags[2]
    assert image.get("src") == "https://i.imgur.com/611EovQs.gif"
    image = img_tags[3]
    assert image.get("src") == "https://i.imgur.com/611EovQs.jpg"


@pytest.mark.sphinx("latex", testroot="image-latex")
def test_image_latex(latex_graphics: List[TexNode], ls_out_files: Dict[str, int]):
    """Test."""
    image = latex_graphics[0]
    assert image.text == ["611EovQh", ".jpg"]
    assert ls_out_files["611EovQh.jpg"] > 90000
    target = image.parent
    assert target.name != "sphinxhref"

    image = latex_graphics[1]
    assert image.text == ["611EovQm", ".jpeg"]
    assert ls_out_files["611EovQm.jpeg"] > 18000
    target = image.parent
    assert target.name == "sphinxhref"
    assert target.text == ["https://imgur.com/611EovQ", "611EovQm", ".jpeg"]


@pytest.mark.sphinx("html", testroot="image-size")
def test_image_size(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://i.imgur.com/001EovQl.jpg"
    image = img_tags[1]
    assert image.get("src") == "https://i.imgur.com/011EovQ.jpg"
    image = img_tags[2]
    assert image.get("src") == "https://i.imgur.com/021EovQ.jpeg"
    image = img_tags[3]
    assert image.get("src") == "https://i.imgur.com/031EovQm.jpg"
    image = img_tags[4]
    assert image.get("src") == "https://i.imgur.com/041EovQm.jpg"
    image = img_tags[5]
    assert image.get("src") == "https://i.imgur.com/051EovQm.jpeg"
    image = img_tags[6]
    assert image.get("src") == "https://i.imgur.com/061EovQs.jpg"
    image = img_tags[7]
    assert image.get("src") == "https://i.imgur.com/071EovQs.jpg"
    image = img_tags[8]
    assert image.get("src") == "https://i.imgur.com/081EovQs.jpeg"
    image = img_tags[9]
    assert image.get("src") == "https://i.imgur.com/091EovQs.jpg"
    image = img_tags[10]
    assert image.get("src") == "https://i.imgur.com/101EovQs.jpg"
    image = img_tags[11]
    assert image.get("src") == "https://i.imgur.com/111EovQs.jpeg"
    image = img_tags[12]
    assert image.get("src") == "https://i.imgur.com/121EovQ.jpg"
    image = img_tags[13]
    assert image.get("src") == "https://i.imgur.com/131EovQ.jpg"
    image = img_tags[14]
    assert image.get("src") == "https://i.imgur.com/141EovQ.jpg"
    image = img_tags[15]
    assert image.get("src") == "https://i.imgur.com/151EovQ.jpeg"


@pytest.mark.sphinx("html", testroot="image-target")
def test_image_target(img_tags: List[element.Tag]):
    """Test."""
    image = img_tags[0]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://robpol86.com"

    image = img_tags[1]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name == "a"
    assert target.get("href") == "https://i.imgur.com/611EovQh.jpg#%"

    image = img_tags[2]
    assert image.get("src") == "https://i.imgur.com/611EovQh.jpg"
    target = image.parent
    assert target.name != "a"
