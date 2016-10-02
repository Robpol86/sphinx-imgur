"""Test Imgur API data caching."""

import sys
import time
from multiprocessing import Process

import httpretty
import pytest
from sphinx import build_main


def build_child_process(argv, cached_responses):
    """Run Sphinx's build_main after setting up httpretty mock responses. Called by multiprocess.Process.

    Need to use this instead of httpretty pytest fixtures since forking doesn't exist in Windows and multiprocess runs
    in "spawn" mode. This means that everything setup by pytest is lost since subprocesses are generated from scratch on
    Windows.

    :raise: RuntimeError on Sphinx non-zero exit. This causes multiprocessing.Process().exitcode to be != 0.

    :param argv: Passed to build_main().
    :param dict cached_responses: URL keys and serialized JSON values.
    """
    if sys.platform == 'win32':
        httpretty.enable()
        if cached_responses:
            for url, body in cached_responses.items():
                httpretty.register_uri(httpretty.GET, url, body=body)
    result = build_main(argv)
    if result != 0:
        raise RuntimeError(result)


@pytest.mark.httpretty
def test_first_run(httpretty_common_mock, tmpdir_module, docs):
    """Run sphinx-build once. Persist output files in module-scoped tmpdir.

    :param httpretty_common_mock: conftest fixture.
    :param tmpdir_module: conftest fixture.
    :param docs: conftest fixture.
    """
    docs.copy(tmpdir_module.ensure_dir('docs'))
    html = tmpdir_module.join('html')

    argv = ('sphinx-build', str(tmpdir_module.join('docs')), str(html))
    child = Process(target=build_child_process, args=(argv, httpretty_common_mock))
    child.start()
    child.join()
    result = child.exitcode

    assert result == 0
    assert html.join('contents.html').check()

    contents = html.join('one.html').read()
    assert 'Title: 2010 JSW, 2012 Projects;' in contents
    assert 'Description: Screenshots of my various devices.;' in contents
    contents = html.join('two.html').read()
    assert 'Title: Work, June 1st, 2016: Uber;' in contents
    assert 'Description: None;' in contents


@pytest.mark.httpretty
def test_second_cached_run(tmpdir_module):
    """Run with nothing changed. Ensure no API queries happen.

    :param tmpdir_module: conftest fixture.
    """
    docs = tmpdir_module.join('docs')
    html = tmpdir_module.join('html')

    time.sleep(1.1)
    docs.join('one.rst').write('Edited\n', mode='a')

    argv = ('sphinx-build', str(docs), str(html))
    child = Process(target=build_child_process, args=(argv, None))
    child.start()
    child.join()
    result = child.exitcode

    assert result == 0

    contents = html.join('one.html').read()
    assert 'Title: 2010 JSW, 2012 Projects;' in contents
    assert 'Description: Screenshots of my various devices.;' in contents
    assert 'Edited' in contents
    contents = html.join('two.html').read()
    assert 'Title: Work, June 1st, 2016: Uber;' in contents
    assert 'Description: None;' in contents
