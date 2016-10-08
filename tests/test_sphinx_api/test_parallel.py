"""Test Sphinx parallel support."""

import pickle
import re

import pytest


@pytest.mark.httpretty
def test_parallel(tmpdir, docs, httpretty_common_mock):
    """Run sphinx-build with -j option.

    :param py.path.local tmpdir: pytest fixture.
    :param py.path.local docs: conftest fixture.
    :param dict httpretty_common_mock: conftest fixture.
    """
    html = tmpdir.join('html')

    # Add pages to build in parallel.
    pytest.add_page(docs, 'one', 'Title: :imgur-title:`a/V76cJ`;\nDescription: :imgur-description:`a/VMlM6`;\n')
    pytest.add_page(docs, 'two', 'Title: :imgur-title:`611EovQ`;\nDescription: :imgur-description:`2QcXR3R`;\n')
    pytest.add_page(docs, 'three', 'Title: :imgur-title:`hiX02`;\n')
    pytest.add_page(docs, 'four', 'Title: :imgur-title:`Pwx1G5j`;\n')
    pytest.add_page(docs, 'five', 'Title: :imgur-title:`mGQBV`;\n')
    pytest.add_page(docs, 'six', 'Title: :imgur-title:`pc8hc`;\n')
    pytest.add_page(docs, 'seven', 'Title: :imgur-title:`ojGG7`;\n')
    pytest.add_page(docs, 'eight', 'Title: :imgur-title:`Hqw7KHM`;\n')

    # Add empty pages to test event_env_merge_info() if statement.
    for i in range(8):
        pytest.add_page(docs, 'ignore{}'.format(i), 'Hello World\n')

    # Run.
    result, stdout, stderr = pytest.build_isolated(docs, html, httpretty_common_mock, ('-j', '4'))

    # Verify return code and console output.
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

    # Verify HTML contents.
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

    # Verify pickled environment.
    handle = html.join('.doctrees', 'environment.pickle').open(mode='rb')
    env = pickle.load(handle)
    handle.close()
    actual = sorted(env.imgur_album_cache)
    assert actual == ['V76cJ', 'VMlM6']
    actual = sorted(env.imgur_image_cache)
    assert actual == ['2QcXR3R', '611EovQ', 'Hqw7KHM', 'Pwx1G5j', 'hiX02', 'mGQBV', 'ojGG7', 'pc8hc']
    assert env.imgur_image_cache['2QcXR3R'].title is None
    assert env.imgur_image_cache['611EovQ'].title == 'Work, June 1st, 2016: Uber'
    assert env.imgur_image_cache['Hqw7KHM'].title is None
    assert env.imgur_image_cache['Pwx1G5j'].title is None
    assert env.imgur_album_cache['V76cJ'].title == '2010 JSW, 2012 Projects'
    assert env.imgur_album_cache['VMlM6'].title == 'Screenshots'
    assert env.imgur_image_cache['hiX02'].title is None
    assert env.imgur_image_cache['mGQBV'].title == 'Wireless Charging 1: Testing'
    assert env.imgur_image_cache['ojGG7'].title == 'Wireless Charging 3: Works'
    assert env.imgur_image_cache['pc8hc'].title == 'Wireless Charging 2: Testing Closeup'
