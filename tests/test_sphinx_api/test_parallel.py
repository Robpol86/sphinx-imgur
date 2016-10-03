"""Test Sphinx parallel support."""

import pickle
import re

import pytest


def add_page(docs, name, role):
    """Add a page to the sample Sphinx docs.

    :param py.path docs: Path to docs root dir.
    :param str name: Page name.
    :param str role: Sphinx role to put in page..
    """
    docs.join('contents.rst').write('    {}\n'.format(name), mode='a')
    page = docs.join('{}.rst'.format(name))
    assert not page.check()
    page.write('.. _{}:\n\n{}\n{}\n\nTitle: {};\n'.format(name, name.capitalize(), '=' * len(name), role))


@pytest.mark.parametrize('parallel', range(1, 5))
@pytest.mark.httpretty
def test_parallel(tmpdir, build_isolated, docs, httpretty_common_mock, parallel):
    """Run sphinx-build with -j option.

    :param tmpdir: pytest fixture.
    :param build_isolated: conftest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    :param int parallel: Run these many parallel processes.
    """
    add_page(docs, 'three', ':imgur-title:`hiX02`')
    add_page(docs, 'four', ':imgur-title:`Pwx1G5j`')
    add_page(docs, 'five', ':imgur-title:`mGQBV`')
    add_page(docs, 'six', ':imgur-title:`pc8hc`')
    add_page(docs, 'seven', ':imgur-title:`ojGG7`')
    add_page(docs, 'eight', ':imgur-title:`Hqw7KHM`')
    html = tmpdir.join('html')
    result, stdout, stderr = build_isolated(docs, html, httpretty_common_mock, ('-j', str(parallel)))

    assert result == 0
    assert not stderr
    actual = sorted(re.compile(r'^querying http.+$', re.MULTILINE).findall(stdout))
    expected = [
        'querying https://api.imgur.com/3/album/V76cJ',
        'querying https://api.imgur.com/3/album/VMlM6',
        'querying https://api.imgur.com/3/image/611EovQ',
        'querying https://api.imgur.com/3/image/Pwx1G5j',
        'querying https://api.imgur.com/3/image/hiX02',
    ]
    assert actual == expected

    contents = html.join('one.html').read()
    assert 'Title: 2010 JSW, 2012 Projects;' in contents
    assert 'Description: Screenshots of my various devices.;' in contents
    contents = html.join('two.html').read()
    assert 'Title: Work, June 1st, 2016: Uber;' in contents
    assert 'Description: None;' in contents
    contents = html.join('three.html').read()
    assert 'Title: None;' in contents
    contents = html.join('four.html').read()
    assert 'Title: None;' in contents
    contents = html.join('five.html').read()
    assert 'Title: Wireless Charging 1: Testing;' in contents
    contents = html.join('six.html').read()
    assert 'Title: Wireless Charging 2: Testing Closeup;' in contents
    contents = html.join('seven.html').read()
    assert 'Title: Wireless Charging 3: Works;' in contents
    contents = html.join('eight.html').read()
    assert 'Title: None;' in contents

    handle = html.join('.doctrees', 'environment.pickle').open(mode='rb')
    env = pickle.load(handle)
    handle.close()
    actual = sorted(env.imgur_album_cache)
    assert actual == ['2QcXR3R', '611EovQ', 'Hqw7KHM', 'Pwx1G5j', 'V76cJ', 'VMlM6', 'hiX02', 'mGQBV', 'ojGG7', 'pc8hc']
    assert env.imgur_album_cache['2QcXR3R'].title is None
    assert env.imgur_album_cache['611EovQ'].title == 'Work, June 1st, 2016: Uber'
    assert env.imgur_album_cache['Hqw7KHM'].title is None
    assert env.imgur_album_cache['Pwx1G5j'].title is None
    assert env.imgur_album_cache['V76cJ'].title == '2010 JSW, 2012 Projects'
    assert env.imgur_album_cache['VMlM6'].title == 'Screenshots'
    assert env.imgur_album_cache['hiX02'].title is None
    assert env.imgur_album_cache['mGQBV'].title == 'Wireless Charging 1: Testing'
    assert env.imgur_album_cache['ojGG7'].title == 'Wireless Charging 3: Works'
    assert env.imgur_album_cache['pc8hc'].title == 'Wireless Charging 2: Testing Closeup'
