"""Test imgur-image directive."""

import re

import py
import pytest


@pytest.fixture
def copy_images(docs):
    """Copy test images into docs root.

    :param docs: conftest fixture.
    """
    for path in py.path.local(__file__).dirpath().visit('image_*.???'):
        path.copy(docs.join(path.basename[6:]))


@pytest.mark.parametrize('album', [False, True])
def test_bad_imgur_id(tmpdir, docs, album):
    """Test invalid imgur_id value.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param bool album: Invalid album vs image ID.
    """
    iid = 'a/inv@lid' if album else 'inv@lid'
    pytest.add_page(docs, 'one', '\n.. imgur-image:: {}\n'.format(iid))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result != 0
    assert 'WARNING' not in stderr
    assert not html.listdir('*.html')
    expected = 'Invalid Imgur ID specified. Must be 5-10 letters and numbers. Albums prefixed with "a/".'
    assert expected in stderr


@pytest.mark.usefixtures('copy_images')
def test_basic(tmpdir, docs, httpretty_common_mock):
    """Verify imgur-image directive generates the same HTML as the built-in image directive when using no options.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    """
    pytest.add_page(docs, 'album', 'SEP\n\n.. image:: 2QcXR3R.png\n\nSEP\n\n.. imgur-image:: a/VMlM6\n\nSEP\n')
    pytest.add_page(docs, 'image', 'SEP\n\n.. image:: 611EovQ.jpg\n\nSEP\n\n.. imgur-image:: 611EovQ\n\nSEP\n')
    html = tmpdir.join('html')
    result, stdout, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)

    # Verify return code and console output.
    assert result == 0
    assert not stderr
    actual = sorted(re.compile(r'^querying http.+$', re.MULTILINE).findall(stdout))
    expected = [
        'querying https://api.imgur.com/3/album/VMlM6',
        'querying https://api.imgur.com/3/image/611EovQ',
    ]
    assert actual == expected

    # Verify HTML contents.
    contents = [c.strip() for c in html.join('album.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="_images/2QcXR3R.png" src="_images/2QcXR3R.png" />'
    assert contents[1] == '<img alt="i.imgur.com/2QcXR3R.png" src="//i.imgur.com/2QcXR3R.png">'
    contents = [c.strip() for c in html.join('image.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="_images/611EovQ.jpg" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="i.imgur.com/611EovQ.jpg" src="//i.imgur.com/611EovQ.jpg">'


@pytest.mark.usefixtures('copy_images')
def test_alt_align(tmpdir, docs, httpretty_common_mock):
    """Verify image alignment and alt text.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    """
    pytest.add_page(docs, 'alt', (
        'SEP\n'
        '\n'
        '.. image:: 611EovQ.jpg\n'
        '    :alt: Alternative Text\n'
        '    :align: right\n'
        '\n'
        'SEP\n'
        '\n'
        '.. imgur-image:: 611EovQ\n'
        '    :alt: Alternative Text\n'
        '    :align: right\n'
        '\n'
        'SEP\n'
    ))
    pytest.add_page(docs, 'aligns', (
        'SEP\n\n'
        '.. image:: 611EovQ.jpg\n    :align: left\n\nSEP\n\n.. imgur-image:: 611EovQ\n    :align: left\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :align: center\n\nSEP\n\n.. imgur-image:: 611EovQ\n    :align: center\n\nSEP\n\n'
    ))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)[::2]

    assert result == 0
    assert not stderr

    contents = [c.strip() for c in html.join('alt.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="Alternative Text" class="align-right" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="Alternative Text" class="align-right" src="//i.imgur.com/611EovQ.jpg">'

    contents = [c.strip() for c in html.join('aligns.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="_images/611EovQ.jpg" class="align-left" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="i.imgur.com/611EovQ.jpg" class="align-left" src="//i.imgur.com/611EovQ.jpg">'
    assert contents[2] == '<img alt="_images/611EovQ.jpg" class="align-center" src="_images/611EovQ.jpg" />'
    assert contents[3] == '<img alt="i.imgur.com/611EovQ.jpg" class="align-center" src="//i.imgur.com/611EovQ.jpg">'
