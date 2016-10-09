"""Test imgur-embed directive."""

import re

import pytest

RE_BLOCKQUOTES = re.compile(r'(<blockquote[^>]* class="imgur-embed-pub"[^>]*>)')
RE_SCRIPTS = re.compile(r'(<script[^>]* src="//s.imgur.com/min/embed.js"[^>]*>)')


@pytest.mark.parametrize('album', [False, True])
def test_bad_imgur_id(tmpdir, docs, album):
    """Test invalid imgur_id value.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param bool album: Invalid album vs image ID.
    """
    iid = 'a/inv@lid' if album else 'inv@lid'
    pytest.add_page(docs, 'one', '\n.. imgur-embed:: {}\n'.format(iid))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result != 0
    assert 'WARNING' not in stderr
    assert not html.listdir('*.html')
    expected = 'Invalid Imgur ID specified. Must be 5-10 letters and numbers. Albums prefixed with "a/".'
    assert expected in stderr


@pytest.mark.parametrize('hpd_conf', [None, False, True])
def test_embed(tmpdir, docs, hpd_conf):
    """Test valid imgur_id value in imgur-embed directive.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param bool hpd_conf: Value of imgur_hide_post_details in conf.py or don't set if None.
    """
    if hpd_conf is not None:
        docs.join('conf.py').write('imgur_hide_post_details = {}\n'.format(hpd_conf), mode='a')

    for page, hpd_option in [('one', None), ('two', False), ('three', True)]:
        hpd = '\n    :hide_post_details: {}'.format(hpd_option) if hpd_option is not None else ''
        pytest.add_page(docs, page, '.. imgur-embed:: a/VMlM6{0}\n\n.. imgur-embed:: 611EovQ{0}\n'.format(hpd))

    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result == 0
    assert not stderr

    # Verify blockquotes/scripts.
    for page in ('one.html', 'two.html', 'three.html'):
        contents = html.join(page).read()
        blockquotes = RE_BLOCKQUOTES.findall(contents)
        scripts = RE_SCRIPTS.findall(contents)
        assert len(blockquotes) == 2
        assert len(scripts) == 2
        assert 'data-id="a/VMlM6"' in blockquotes[0]
        assert 'data-id="611EovQ"' in blockquotes[1]

    # Verify data-context.
    for page, expected in [('one.html', 2 if hpd_conf else 0), ('two.html', 0), ('three.html', 2)]:
        contents = html.join(page).read()
        actual = contents.count('data-context="false"')
        assert actual == expected
