"""Test imgur-image directive."""
import py
import pytest


@pytest.fixture
def copy_images(docs):
    """Copy test images into docs root.

    :param docs: conftest fixture.
    """
    for path in py.path.local(__file__).dirpath().visit("image_*.???"):
        path.copy(docs.join(path.basename[6:]))


def test_bad_imgur_id(tmpdir, docs):
    """Test invalid imgur_id value.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    """
    iid = "inv@lid"
    pytest.add_page(docs, "one", "\n.. imgur-image:: {}\n".format(iid))
    html = tmpdir.join("html")
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result != 0
    assert "WARNING" not in stderr
    assert not html.listdir("*.html")
    expected = 'Invalid Imgur ID specified. Must be 5-10 letters and numbers.'
    assert expected in stderr


@pytest.mark.usefixtures("copy_images")
def test_basic(tmpdir, docs):
    """Verify imgur-image directive generates the same HTML as the built-in image directive when using no options.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    """
    pytest.add_page(docs, "image", "SEP\n\n.. image:: 611EovQ.jpg\n\nSEP\n\n.. imgur-image:: 611EovQ\n\nSEP\n")
    html = tmpdir.join("html")
    result, stdout, stderr = pytest.build_isolated(docs, html, {})

    # Verify return code and console output.
    assert result == 0
    assert not stderr

    # Verify HTML contents.
    contents = [c.strip() for c in html.join("image.html").read().split("<p>SEP</p>")[1:-1]]
    assert contents[0] == '<img alt="_images/611EovQ.jpg" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="i.imgur.com/611EovQh.jpg" src="//i.imgur.com/611EovQh.jpg">'

    # Verify newlines.
    contents = html.join("image.html").read()
    assert '\n<img alt="i.imgur.com/611EovQh.jpg" src="//i.imgur.com/611EovQh.jpg">\n' in contents


@pytest.mark.usefixtures("copy_images")
def test_alt_align(tmpdir, docs):
    """Verify image alignment and alt text.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    """
    pytest.add_page(
        docs,
        "alt",
        (
            "SEP\n"
            "\n"
            ".. image:: 611EovQ.jpg\n"
            "    :alt: Alternative Text\n"
            "    :align: right\n"
            "\n"
            "SEP\n"
            "\n"
            ".. imgur-image:: 611EovQ\n"
            "    :alt: Alternative Text\n"
            "    :align: right\n"
            "\n"
            "SEP\n\n"
            ".. imgur-image:: 611EovQ\n\nSEP\n\n"
        ),
    )
    pytest.add_page(
        docs,
        "aligns",
        (
            "SEP\n\n"
            ".. image:: 611EovQ.jpg\n    :align: left\n\nSEP\n\n.. imgur-image:: 611EovQ\n    :align: left\n\nSEP\n\n"
            ".. image:: 611EovQ.jpg\n    :align: center\n\nSEP\n\n.. imgur-image:: 611EovQ\n    :align: center\n\nSEP\n\n"
        ),
    )
    html = tmpdir.join("html")
    result, stderr = pytest.build_isolated(docs, html, {})[::2]

    assert result == 0
    assert not stderr

    contents = [c.strip() for c in html.join("alt.html").read().split("<p>SEP</p>")[1:-1]]
    assert contents[0] == '<img alt="Alternative Text" class="align-right" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="Alternative Text" class="align-right" src="//i.imgur.com/611EovQh.jpg">'
    assert contents[2] == '<img alt="i.imgur.com/611EovQh.jpg" src="//i.imgur.com/611EovQh.jpg">'

    contents = [c.strip() for c in html.join("aligns.html").read().split("<p>SEP</p>")[1:-1]]
    assert contents[0] == '<img alt="_images/611EovQ.jpg" class="align-left" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="i.imgur.com/611EovQh.jpg" class="align-left" src="//i.imgur.com/611EovQh.jpg">'
    assert contents[2] == '<img alt="_images/611EovQ.jpg" class="align-center" src="_images/611EovQ.jpg" />'
    assert contents[3] == '<img alt="i.imgur.com/611EovQh.jpg" class="align-center" src="//i.imgur.com/611EovQh.jpg">'


@pytest.mark.usefixtures("copy_images")
@pytest.mark.parametrize("set_conf", [None, "largest", "page"])
def test_target(tmpdir, docs, set_conf):
    """Test combination of "target" conf.py and directive options.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param str set_conf: Set conf.py config setting.
    """
    if set_conf:
        docs.join("conf.py").write("imgur_target_default_{} = True\n".format(set_conf), mode="a")

    pytest.add_page(
        docs,
        "test",
        (
            "SEP\n\n"
            ".. image:: 611EovQ.jpg\n    :target: https://goo.gl\n\nSEP\n\n"
            ".. imgur-image:: 611EovQ\n    :target: https://goo.gl\n\nSEP\n\n"
            ".. imgur-image:: 611EovQ\n    :target_largest: true\n\nSEP\n\n"
            ".. imgur-image:: 611EovQ\n    :target_page: true\n\nSEP\n\n"
            ".. imgur-image:: 611EovQ\n\nSEP\n\n"
        ),
    )
    html = tmpdir.join("html")
    result, stderr = pytest.build_isolated(docs, html, {})[::2]

    assert result == 0
    assert not stderr

    img_i = '<img alt="_images/611EovQ.jpg" src="_images/611EovQ.jpg" />'
    img = '<img alt="i.imgur.com/611EovQh.jpg" src="//i.imgur.com/611EovQh.jpg">'
    dat = [c.strip() for c in html.join("test.html").read().split("<p>SEP</p>")[1:-1]]
    assert dat[0] == '<a class="reference external image-reference" href="https://goo.gl">%s</a>' % img_i
    assert dat[1] == '<a class="reference external image-reference" href="https://goo.gl">%s</a>' % img
    assert dat[2] == '<a class="reference external image-reference" href="//i.imgur.com/611EovQ.jpg">%s</a>' % img
    assert dat[3] == '<a class="reference external image-reference" href="//imgur.com/611EovQ">%s</a>' % img
    if set_conf == "largest":
        assert dat[4] == '<a class="reference external image-reference" href="//i.imgur.com/611EovQ.jpg">%s</a>' % img
    elif set_conf == "page":
        assert dat[4] == '<a class="reference external image-reference" href="//imgur.com/611EovQ">%s</a>' % img
    else:
        assert dat[4] == img  # No link.
