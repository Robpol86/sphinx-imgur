"""Test Sphinx directives."""

import re

import pytest

RE_BLOCKQUOTES = re.compile(r'(<blockquote[^>]* class="imgur-embed-pub"[^>]*>)')
RE_SCRIPTS = re.compile(r'(<script[^>]* src="//s.imgur.com/min/embed.js"[^>]*>)')


@pytest.mark.parametrize('album', [False, True])
@pytest.mark.httpretty
def test_bad_imgur_id(tmpdir, docs, album):
    """Test invalid imgur_id value.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param bool album: Invalid album vs image ID.
    """
    iid = 'a/inv@lid' if album else 'inv@lid'
    docs.join('one.rst').write('\n.. imgur-embed:: {}\n'.format(iid), mode='a')
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result != 0
    assert 'WARNING' not in stderr
    assert not html.listdir('*.html')
    expected = 'Invalid Imgur ID specified. Must be 5-10 letters and numbers. Albums prefixed with "a/".'
    assert expected in stderr


@pytest.mark.parametrize('hpd_option', [None, False, True])
@pytest.mark.parametrize('hpd_conf', [None, False, True])
@pytest.mark.httpretty
def test_embed(tmpdir, docs, hpd_conf, hpd_option):
    """Test valid imgur_id value in imgur-embed directive.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param bool hpd_conf: Value of imgur_hide_post_details in conf.py or don't set if None.
    :param bool hpd_option: Value of hide_post_details in rst file or don't set if None.
    """
    if hpd_conf is not None:
        docs.join('conf.py').write('imgur_hide_post_details = {}\n'.format(hpd_conf), mode='a')
    pytest.add_page(docs, 'one')

    for iid in ('a/VMlM6', '611EovQ'):
        docs.join('one.rst').write('\n.. imgur-embed:: {}\n'.format(iid), mode='a')
        if hpd_option is not None:
            docs.join('one.rst').write('    :hide_post_details: {}\n'.format(hpd_option), mode='a')

    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result == 0
    assert not stderr
    contents = html.join('one.html').read()
    blockquotes = RE_BLOCKQUOTES.findall(contents)
    scripts = RE_SCRIPTS.findall(contents)
    assert len(blockquotes) == 2
    assert len(scripts) == 2
    assert 'data-id="a/VMlM6"' in blockquotes[0]
    assert 'data-id="611EovQ"' in blockquotes[1]

    actual = contents.count('data-context="false"')
    if hpd_option or (hpd_option is None and hpd_conf):
        assert actual == 2
    else:
        assert actual == 0
