"""Test Imgur API data caching."""

import re
import time

import pytest


@pytest.mark.httpretty
def test_first_run(docs, httpretty_common_mock, tmpdir_module):
    """Run sphinx-build once. Persist output files in module-scoped tmpdir.

    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    :param tmpdir_module: conftest fixture.
    """
    docs.copy(tmpdir_module.ensure_dir('docs'))
    docs = tmpdir_module.join('docs')
    pytest.add_page(docs, 'one', 'Title: :imgur-title:`a/V76cJ`;\nDescription: :imgur-description:`a/VMlM6`;\n')
    pytest.add_page(docs, 'two', 'Title: :imgur-title:`611EovQ`;\nDescription: :imgur-description:`2QcXR3R`;\n')
    html = tmpdir_module.join('html')
    result, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)[::2]

    assert result == 0
    assert not stderr
    assert html.join('contents.html').check()

    contents = html.join('one.html').read()
    assert 'Title: 2010 JSW, 2012 Projects;' in contents
    assert 'Description: Screenshots of my various devices.;' in contents
    contents = html.join('two.html').read()
    assert 'Title: Work, June 1st, 2016: Uber;' in contents
    assert 'Description: None;' in contents


@pytest.mark.parametrize('update', ['two.rst', 'ignore.rst'])
@pytest.mark.httpretty
def test_second_cached_run(tmpdir_module, update):
    """Run with nothing changed. Ensure no API queries happen.

    :param tmpdir_module: conftest fixture.
    :param str update: Which file to edit. two.rst edits a file with Imgur IDs, ignore.rst edits file without.
    """
    time.sleep(1.1)

    docs = tmpdir_module.join('docs')
    docs.join(update).write('Edited\n', mode='a')
    html = tmpdir_module.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result == 0
    assert not stderr

    contents = html.join('one.html').read()
    assert 'Title: 2010 JSW, 2012 Projects;' in contents
    assert 'Description: Screenshots of my various devices.;' in contents
    contents = html.join('two.html').read()
    assert 'Title: Work, June 1st, 2016: Uber;' in contents
    assert 'Description: None;' in contents
    if update == 'two.rst':
        assert 'Edited' in contents
    else:
        contents = html.join('ignore.html').read()
        assert 'Edited' in contents


@pytest.mark.httpretty
def test_new_rst_old_id(tmpdir_module):
    """Add a new RST file but use a pre-existing Imgur ID.

    :param tmpdir_module: conftest fixture.
    """
    time.sleep(1.1)

    docs = tmpdir_module.join('docs')
    docs.join('contents.rst').write('    three\n', mode='a')
    assert not docs.join('three.rst').check()
    docs.join('three.rst').write('.. _three:\n\nThree\n=====\n\nTitle: :imgur-title:`a/VMlM6`;\n'
                                 'Description: :imgur-description:`pc8hc`;\n')
    html = tmpdir_module.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result == 0
    assert not stderr

    contents = html.join('three.html').read()
    assert 'Title: Screenshots;' in contents
    assert 'Description: Closeup of Nokia DT-900 charger wedged in my door panel.;' in contents


@pytest.mark.httpretty
def test_single_id_update(httpretty_common_mock, tmpdir_module):
    """Make sure only one ID is updated.

    :param httpretty_common_mock: conftest fixture.
    :param tmpdir_module: conftest fixture.
    """
    time.sleep(1.1)

    docs = tmpdir_module.join('docs')
    docs.join('three.rst').write('Title: :imgur-title:`hiX02`;\n', mode='a')
    html = tmpdir_module.join('html')
    result, stdout, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)

    assert result == 0
    assert not stderr
    actual = re.compile(r'^querying http.+$', re.MULTILINE).findall(stdout)
    assert actual == ['querying https://api.imgur.com/3/image/hiX02']

    contents = html.join('three.html').read()
    assert 'Title: None;' in contents


@pytest.mark.httpretty
def test_expire_everything_single_update(httpretty_common_mock, tmpdir_module):
    """Make sure only one API query is done when only one document is updated even though other entries are old.

    :param httpretty_common_mock: conftest fixture.
    :param tmpdir_module: conftest fixture.
    """
    time.sleep(1.1)

    docs = tmpdir_module.join('docs')
    docs.join('conf.py').write('imgur_api_cache_ttl = 1\n', mode='a')
    docs.join('three.rst').write('.. _three:\n\nThree\n=====\n\nTitle: :imgur-title:`a/VMlM6`;\n')
    html = tmpdir_module.join('html')
    result, stdout, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)

    assert result == 0
    assert not stderr
    actual = re.compile(r'^querying http.+$', re.MULTILINE).findall(stdout)
    assert actual == ['querying https://api.imgur.com/3/album/VMlM6']

    contents = html.join('three.html').read()
    assert 'Title: Screenshots;' in contents
