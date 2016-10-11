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


def test_album_largest(tmpdir, docs):
    """Test :target_largest: being used on albums.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    """
    pytest.add_page(docs, 'one', '\n.. imgur-image:: a/valid\n    :target_largest: true\n')
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result != 0
    assert 'WARNING' not in stderr
    assert not html.listdir('*.html')
    expected = 'Imgur albums (whose covers are displayed) do not support :target_largest: option.'
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
    assert contents[1] == '<img alt="Work, June 1st, 2016: Uber" src="//i.imgur.com/611EovQ.jpg">'


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
        'SEP\n\n'
        '.. imgur-image:: 611EovQ\n\nSEP\n\n'
    ))
    pytest.add_page(docs, 'aligns', (
        'SEP\n\n'
        '.. image:: 2QcXR3R.png\n    :align: left\n\nSEP\n\n.. imgur-image:: 2QcXR3R\n    :align: left\n\nSEP\n\n'
        '.. image:: 2QcXR3R.png\n    :align: center\n\nSEP\n\n.. imgur-image:: 2QcXR3R\n    :align: center\n\nSEP\n\n'
    ))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)[::2]

    assert result == 0
    assert not stderr

    contents = [c.strip() for c in html.join('alt.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="Alternative Text" class="align-right" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="Alternative Text" class="align-right" src="//i.imgur.com/611EovQ.jpg">'
    assert contents[2] == '<img alt="Work, June 1st, 2016: Uber" src="//i.imgur.com/611EovQ.jpg">'

    contents = [c.strip() for c in html.join('aligns.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="_images/2QcXR3R.png" class="align-left" src="_images/2QcXR3R.png" />'
    assert contents[1] == '<img alt="i.imgur.com/2QcXR3R.png" class="align-left" src="//i.imgur.com/2QcXR3R.png">'
    assert contents[2] == '<img alt="_images/2QcXR3R.png" class="align-center" src="_images/2QcXR3R.png" />'
    assert contents[3] == '<img alt="i.imgur.com/2QcXR3R.png" class="align-center" src="//i.imgur.com/2QcXR3R.png">'


@pytest.mark.usefixtures('copy_images')
@pytest.mark.parametrize('set_conf', [None, 'gallery', 'largest', 'page'])
def test_target(tmpdir, docs, httpretty_common_mock, set_conf):
    """Test combination of "target" conf.py and directive options.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    :param str set_conf: Set conf.py config setting.
    """
    if set_conf:
        docs.join('conf.py').write('imgur_target_default_{} = True\n'.format(set_conf), mode='a')

    pytest.add_page(docs, 'no_gallery', (
        'SEP\n\n'
        '.. image:: 611EovQ.jpg\n    :target: https://goo.gl\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :target: https://goo.gl\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :target_gallery: true\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :target_largest: true\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :target_page: true\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n\nSEP\n\n'
    ))
    pytest.add_page(docs, 'gallery_image', (
        'SEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :target: https://goo.gl\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :target_gallery: true\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :target_largest: true\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :target_page: true\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n\nSEP\n\n'
    ))
    pytest.add_page(docs, 'gallery_album', (
        'SEP\n\n'
        '.. imgur-image:: a/ePSyN\n    :target: https://goo.gl\n\nSEP\n\n'
        '.. imgur-image:: a/ePSyN\n    :target_gallery: true\n\nSEP\n\n'
        '.. imgur-image:: a/ePSyN\n    :target_page: true\n\nSEP\n\n'
        '.. imgur-image:: a/ePSyN\n\nSEP\n\n'
    ))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)[::2]

    assert result == 0
    assert not stderr

    img_i = '<img alt="_images/611EovQ.jpg" src="_images/611EovQ.jpg" />'
    img = '<img alt="Work, June 1st, 2016: Uber" src="//i.imgur.com/611EovQ.jpg">'
    dat = [c.strip() for c in html.join('no_gallery.html').read().split('<p>SEP</p>')[1:-1]]
    assert dat[0] == '<a class="reference external image-reference" href="https://goo.gl">%s</a>' % img_i
    assert dat[1] == '<a class="reference external image-reference" href="https://goo.gl">%s</a>' % img
    assert dat[2] == img  # No link since this isn't in gallery.
    assert dat[3] == '<a class="reference external image-reference" href="//i.imgur.com/611EovQ.jpg">%s</a>' % img
    assert dat[4] == '<a class="reference external image-reference" href="//imgur.com/611EovQ">%s</a>' % img
    if set_conf == 'largest':
        assert dat[5] == '<a class="reference external image-reference" href="//i.imgur.com/611EovQ.jpg">%s</a>' % img
    elif set_conf == 'page':
        assert dat[5] == '<a class="reference external image-reference" href="//imgur.com/611EovQ">%s</a>' % img
    else:
        assert dat[5] == img  # No link.

    img = '<img alt="Blow me a kiss!" src="//i.imgur.com/zXVtETZ.gif">'
    dat = [c.strip() for c in html.join('gallery_image.html').read().split('<p>SEP</p>')[1:-1]]
    assert dat[0] == '<a class="reference external image-reference" href="https://goo.gl">%s</a>' % img
    assert dat[1] == '<a class="reference external image-reference" href="//imgur.com/gallery/zXVtETZ">%s</a>' % img
    assert dat[2] == '<a class="reference external image-reference" href="//i.imgur.com/zXVtETZ.gif">%s</a>' % img
    assert dat[3] == '<a class="reference external image-reference" href="//imgur.com/zXVtETZ">%s</a>' % img
    if set_conf == 'largest':
        assert dat[4] == '<a class="reference external image-reference" href="//i.imgur.com/zXVtETZ.gif">%s</a>' % img
    elif set_conf == 'page':
        assert dat[4] == '<a class="reference external image-reference" href="//imgur.com/zXVtETZ">%s</a>' % img
    elif set_conf == 'gallery':
        assert dat[4] == '<a class="reference external image-reference" href="//imgur.com/gallery/zXVtETZ">%s</a>' % img
    else:
        assert dat[4] == img

    img = '<img alt="Rack Cabinet" src="//i.imgur.com/RIK1sDw.jpg">'
    dat = [c.strip() for c in html.join('gallery_album.html').read().split('<p>SEP</p>')[1:-1]]
    assert dat[0] == '<a class="reference external image-reference" href="https://goo.gl">%s</a>' % img
    assert dat[1] == '<a class="reference external image-reference" href="//imgur.com/gallery/ePSyN">%s</a>' % img
    assert dat[2] == '<a class="reference external image-reference" href="//imgur.com/ePSyN">%s</a>' % img
    if set_conf == 'page':
        assert dat[3] == '<a class="reference external image-reference" href="//imgur.com/ePSyN">%s</a>' % img
    elif set_conf == 'gallery':
        assert dat[3] == '<a class="reference external image-reference" href="//imgur.com/gallery/ePSyN">%s</a>' % img
    else:
        assert dat[3] == img
