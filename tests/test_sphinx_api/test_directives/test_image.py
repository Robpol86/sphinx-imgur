"""Test imgur-image directive."""

import re

import httpretty
import py
import pytest

from sphinxcontrib.imgur.imgur_api import API_URL


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


def test_bad_album_largest(tmpdir, docs):
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
    assert contents[1] == '<img alt="i.imgur.com/2QcXR3Rh.png" src="//i.imgur.com/2QcXR3Rh.png">'
    contents = [c.strip() for c in html.join('image.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="_images/611EovQ.jpg" src="_images/611EovQ.jpg" />'
    assert contents[1] == '<img alt="Work, June 1st, 2016: Uber" src="//i.imgur.com/611EovQh.jpg">'


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
    assert contents[1] == '<img alt="Alternative Text" class="align-right" src="//i.imgur.com/611EovQh.jpg">'
    assert contents[2] == '<img alt="Work, June 1st, 2016: Uber" src="//i.imgur.com/611EovQh.jpg">'

    contents = [c.strip() for c in html.join('aligns.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == '<img alt="_images/2QcXR3R.png" class="align-left" src="_images/2QcXR3R.png" />'
    assert contents[1] == '<img alt="i.imgur.com/2QcXR3Rh.png" class="align-left" src="//i.imgur.com/2QcXR3Rh.png">'
    assert contents[2] == '<img alt="_images/2QcXR3R.png" class="align-center" src="_images/2QcXR3R.png" />'
    assert contents[3] == '<img alt="i.imgur.com/2QcXR3Rh.png" class="align-center" src="//i.imgur.com/2QcXR3Rh.png">'


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
    img = '<img alt="Work, June 1st, 2016: Uber" src="//i.imgur.com/611EovQh.jpg">'
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

    img = '<img alt="Rack Cabinet" src="//i.imgur.com/RIK1sDwh.jpg">'
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


@pytest.mark.usefixtures('copy_images')
@pytest.mark.parametrize('set_conf', [None, 'gallery', 'largest', 'page'])
def test_width(tmpdir, docs, httpretty_common_mock, set_conf):
    """Test width option.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    :param str set_conf: Set conf.py config setting.
    """
    if set_conf:
        docs.join('conf.py').write('imgur_target_default_{} = True\n'.format(set_conf), mode='a')

    pytest.add_page(docs, 'unsupported_units', (
        'SEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 300em\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 300em\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :height: 300em\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :height: 300em\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 300em\n    :height: 300em\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 300em\n    :height: 300em\n\nSEP\n\n'
    ))
    pytest.add_page(docs, 'no_mix', (
        'SEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 300px\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 300px\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 15%\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 15%\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 160\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 160\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :height: 200px\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :height: 200px\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :height: 110\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :height: 110\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :scale: 50%\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :scale: 50%\n\nSEP\n\n'
    ))
    pytest.add_page(docs, 'no_target_mix', (
        'SEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 300px\n    :height: 300px\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 300px\n    :height: 300px\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 300px\n    :scale: 50%\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 300px\n    :scale: 50%\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 50%\n    :scale: 50%\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 50%\n    :scale: 50%\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :height: 300px\n    :scale: 50%\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :height: 300px\n    :scale: 50%\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 300px\n    :height: 300px\n    :scale: 50%\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 300px\n    :height: 300px\n    :scale: 50%\n\nSEP\n\n'
    ))
    pytest.add_page(docs, 'target_mix', (
        'SEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 50%\n    :target: https://goo.gl\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :width: 50%\n    :target: https://goo.gl\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :width: 50%\n    :target_gallery: true\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :width: 50%\n    :target_largest: true\n\nSEP\n\n'
        '.. imgur-image:: zXVtETZ\n    :width: 50%\n    :target_page: true\n\nSEP\n\n'
    ))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)[::2]

    assert result == 0
    assert not stderr

    href_i = ('<a class="reference internal image-reference" href="_images/611EovQ.jpg">'
              '<img alt="_images/611EovQ.jpg" %s /></a>')
    if set_conf and set_conf != 'gallery':
        url = '//imgur.com/611EovQ' if set_conf == 'page' else '//i.imgur.com/611EovQ.jpg'
        href = ('<a class="reference external image-reference" href="{}">'
                '<img alt="Work, June 1st, 2016: Uber" %s></a>').format(url)
    else:
        href = ('<a class="reference external image-reference" href="//i.imgur.com/611EovQ.jpg">'
                '<img alt="Work, June 1st, 2016: Uber" %s></a>')

    contents = [c.strip() for c in html.join('unsupported_units.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == href_i % 'src="_images/611EovQ.jpg" style="width: 300em;"'
    assert contents[1] == href % 'src="//i.imgur.com/611EovQh.jpg" style="width: 300em"'
    assert contents[2] == href_i % 'src="_images/611EovQ.jpg" style="height: 300em;"'
    assert contents[3] == href % 'src="//i.imgur.com/611EovQh.jpg" style="height: 300em"'
    assert contents[4] == href_i % 'src="_images/611EovQ.jpg" style="width: 300em; height: 300em;"'
    assert contents[5] == href % 'src="//i.imgur.com/611EovQh.jpg" style="width: 300em; height: 300em"'

    contents = [c.strip() for c in html.join('no_mix.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == href_i % 'src="_images/611EovQ.jpg" style="width: 300px;"'
    assert contents[1] == href % 'src="//i.imgur.com/611EovQm.jpg" style="width: 300px"'
    assert contents[2] == href_i % 'src="_images/611EovQ.jpg" style="width: 15%;"'
    assert contents[3] == href % 'src="//i.imgur.com/611EovQl.jpg" style="width: 15%"'
    assert contents[4] == href_i % 'src="_images/611EovQ.jpg" style="width: 160px;"'
    assert contents[5] == href % 'src="//i.imgur.com/611EovQt.jpg" style="width: 160px"'
    assert contents[6] == href_i % 'src="_images/611EovQ.jpg" style="height: 200px;"'
    assert contents[7] == href % 'src="//i.imgur.com/611EovQm.jpg" style="height: 200px"'
    assert contents[8] == href_i % 'src="_images/611EovQ.jpg" style="height: 110px;"'
    assert contents[9] == href % 'src="//i.imgur.com/611EovQt.jpg" style="height: 110px"'
    assert contents[10] == href_i % 'src="_images/611EovQ.jpg" style="width: 2000.0px; height: 1496.0px;"'
    assert contents[11] == href % 'src="//i.imgur.com/611EovQh.jpg" style="width: 2000px; height: 1496px"'

    contents = [c.strip() for c in html.join('no_target_mix.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == href_i % 'src="_images/611EovQ.jpg" style="width: 300px; height: 300px;"'
    assert contents[1] == href % 'src="//i.imgur.com/611EovQm.jpg" style="width: 300px; height: 300px"'
    assert contents[2] == href_i % 'src="_images/611EovQ.jpg" style="width: 150.0px; height: 1496.0px;"'
    assert contents[3] == href % 'src="//i.imgur.com/611EovQt.jpg" style="width: 150px; height: 1496px"'
    assert contents[4] == href_i % 'src="_images/611EovQ.jpg" style="width: 25.0%; height: 1496.0px;"'
    assert contents[5] == href % 'src="//i.imgur.com/611EovQh.jpg" style="width: 25%; height: 1496px"'
    assert contents[6] == href_i % 'src="_images/611EovQ.jpg" style="width: 2000.0px; height: 150.0px;"'
    assert contents[7] == href % 'src="//i.imgur.com/611EovQh.jpg" style="width: 2000px; height: 150px"'
    assert contents[8] == href_i % 'src="_images/611EovQ.jpg" style="width: 150.0px; height: 150.0px;"'
    assert contents[9] == href % 'src="//i.imgur.com/611EovQt.jpg" style="width: 150px; height: 150px"'

    href_i = ('<a class="reference external image-reference" href="%s">'
              '<img alt="_images/611EovQ.jpg" src="_images/611EovQ.jpg" style="width: 50%%;" /></a>')
    href = ('<a class="reference external image-reference" href="%s">'
            '<img alt="Blow me a kiss!" src="//i.imgur.com/zXVtETZ.gif" style="width: 50%%"></a>')
    contents = [c.strip() for c in html.join('target_mix.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == href_i % 'https://goo.gl'
    assert contents[1] == href % 'https://goo.gl'
    assert contents[2] == href % '//imgur.com/gallery/zXVtETZ'
    assert contents[3] == href % '//i.imgur.com/zXVtETZ.gif'
    assert contents[4] == href % '//imgur.com/zXVtETZ'


def test_width_invalid(tmpdir, docs, httpretty_common_mock):
    """Test invalid values for width option.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    """
    pytest.add_page(docs, 'one', (
        'SEP\n\n'
        '.. image:: 611EovQ.jpg\n    :width: 300db\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :width: 300db\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :height: 300db\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :height: 300db\n\nSEP\n\n'
        '.. image:: 611EovQ.jpg\n    :scale: 300db\n\nSEP\n\n'
        '.. imgur-image:: 611EovQ\n    :scale: 300db\n\nSEP\n\n'
    ))
    html = tmpdir.join('html')
    results = pytest.build_isolated(docs, html, httpretty_common_mock)

    assert results[0] == 0

    contents = [c.strip() for c in html.join('one.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents == ['', '', '', '', '', '']  # Sphinx just omits the bad directive from the final HTML.


def test_missing_api_data(tmpdir, docs):
    """Test handling of missing data in the cache. Will behave like the built-in image directive with external URLs.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    """
    httpretty_mock = {API_URL.format(type='image', id='imgur0id'): '{}'}
    for url, body in httpretty_mock.items():
        httpretty.register_uri(httpretty.GET, url, body=body)

    pytest.add_page(docs, 'no_scale', (
        'SEP\n\n'
        '.. image:: https://i.imgur.com/imgur0idh.jpg\n    :width: 300px\n\nSEP\n\n'
        '.. imgur-image:: imgur0id\n    :width: 300px\n\nSEP\n\n'
        '.. image:: https://i.imgur.com/imgur0idh.jpg\n    :width: 30%\n\nSEP\n\n'
        '.. imgur-image:: imgur0id\n    :width: 30%\n\nSEP\n\n'
        '.. image:: https://i.imgur.com/imgur0idh.jpg\n    :height: 300px\n\nSEP\n\n'
        '.. imgur-image:: imgur0id\n    :height: 300px\n\nSEP\n\n'
    ))
    pytest.add_page(docs, 'scale', (
        'SEP\n\n'
        '.. image:: https://i.imgur.com/imgur0idh.jpg\n    :scale: 25%\n\nSEP\n\n'
        '.. imgur-image:: imgur0id\n    :scale: 25%\n\nSEP\n\n'
    ))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, httpretty_mock)[::2]

    assert result == 0
    lines = [l.split('WARNING: ')[-1].strip() for l in stderr.splitlines()]
    expected = [
        'query unsuccessful from https://api.imgur.com/3/image/imgur0id: no "data" key in JSON',
        'nonlocal image URI found: https://i.imgur.com/imgur0idh.jpg',
        'nonlocal image URI found: https://i.imgur.com/imgur0idh.jpg',
        'nonlocal image URI found: https://i.imgur.com/imgur0idh.jpg',
        'nonlocal image URI found: https://i.imgur.com/imgur0idh.jpg',
        'Could not obtain image size. :scale: option is ignored.',
        'Could not obtain image size. :scale: option is ignored.',
    ]
    assert lines == expected

    href_i = ('<a class="reference internal image-reference" href="https://i.imgur.com/imgur0idh.jpg">'
              '<img alt="https://i.imgur.com/imgur0idh.jpg" %s /></a>')
    href = ('<a class="reference external image-reference" href="//i.imgur.com/imgur0id.jpg">'
            '<img alt="i.imgur.com/imgur0idh.jpg" %s></a>')
    contents = [c.strip() for c in html.join('no_scale.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == href_i % 'src="https://i.imgur.com/imgur0idh.jpg" style="width: 300px;"'
    assert contents[1] == href % 'src="//i.imgur.com/imgur0idh.jpg" style="width: 300px"'
    assert contents[2] == href_i % 'src="https://i.imgur.com/imgur0idh.jpg" style="width: 30%;"'
    assert contents[3] == href % 'src="//i.imgur.com/imgur0idh.jpg" style="width: 30%"'
    assert contents[4] == href_i % 'src="https://i.imgur.com/imgur0idh.jpg" style="height: 300px;"'
    assert contents[5] == href % 'src="//i.imgur.com/imgur0idh.jpg" style="height: 300px"'

    contents = [c.strip() for c in html.join('scale.html').read().split('<p>SEP</p>')[1:-1]]
    assert contents[0] == href_i % 'src="https://i.imgur.com/imgur0idh.jpg"'
    assert contents[1] == href % 'src="//i.imgur.com/imgur0idh.jpg"'
