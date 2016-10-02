"""Test Imgur API data caching."""

import time

import pytest


@pytest.mark.httpretty
def test_first_run(build_isolated, docs, httpretty_common_mock, tmpdir_module):
    """Run sphinx-build once. Persist output files in module-scoped tmpdir.

    :param build_isolated: conftest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    :param tmpdir_module: conftest fixture.
    """
    docs.copy(tmpdir_module.ensure_dir('docs'))
    docs = tmpdir_module.join('docs')
    html = tmpdir_module.join('html')
    result, stderr = build_isolated(docs, html, httpretty_common_mock)[::2]

    assert result == 0
    assert not stderr
    assert html.join('contents.html').check()

    contents = html.join('one.html').read()
    assert 'Title: 2010 JSW, 2012 Projects;' in contents
    assert 'Description: Screenshots of my various devices.;' in contents
    contents = html.join('two.html').read()
    assert 'Title: Work, June 1st, 2016: Uber;' in contents
    assert 'Description: None;' in contents


@pytest.mark.httpretty
def test_second_cached_run(build_isolated, tmpdir_module):
    """Run with nothing changed. Ensure no API queries happen.

    :param build_isolated: conftest fixture.
    :param tmpdir_module: conftest fixture.
    """
    time.sleep(1.1)

    docs = tmpdir_module.join('docs')
    docs.join('one.rst').write('Edited\n', mode='a')
    html = tmpdir_module.join('html')
    result, stderr = build_isolated(docs, html, None)[::2]

    assert result == 0
    assert not stderr

    contents = html.join('one.html').read()
    assert 'Title: 2010 JSW, 2012 Projects;' in contents
    assert 'Description: Screenshots of my various devices.;' in contents
    assert 'Edited' in contents
    contents = html.join('two.html').read()
    assert 'Title: Work, June 1st, 2016: Uber;' in contents
    assert 'Description: None;' in contents
