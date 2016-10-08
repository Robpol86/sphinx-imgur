"""Fixtures for tests in this directory."""

import multiprocessing
import multiprocessing.queues
import sys

import httpretty
import pytest
from sphinx import build_main


def run_build_main(docs_dir, html_dir, overflow):
    """Run build_main().

    :param str docs_dir: Path to input docs directory.
    :param str html_dir: Path to output html directory.
    :param iter overflow: Append these args to sphinx-build call.

    :return: Value from build_main().
    :rtype: int
    """
    argv = ('sphinx-build', str(docs_dir), str(html_dir))
    if overflow:
        argv += overflow
    result = build_main(argv)
    return result


def run_build_main_post_multiprocessing(docs_dir, html_dir, cached_responses, queue, overflow):
    """Run Sphinx's build_main after setting up httpretty mock responses. Called by multiprocess.Process.

    Need to use this instead of httpretty pytest fixtures since forking doesn't exist in Windows and multiprocess runs
    in "spawn" mode. This means that everything setup by pytest is lost since subprocesses are generated from scratch on
    Windows.

    :raise: RuntimeError on Sphinx non-zero exit. This causes multiprocessing.Process().exitcode to be != 0.

    :param str docs_dir: Path to input docs directory.
    :param str html_dir: Path to output html directory.
    :param dict cached_responses: URL keys and serialized JSON values.
    :param multiprocessing.queues.Queue queue: Queue to transmit stdout/err back to parent process.
    :param iter overflow: Append these args to sphinx-build call.
    """
    # Capture stdout/stderr after forking/spawning.
    capture = __import__('_pytest').capture
    try:
        capsys = capture.CaptureFixture(capture.SysCapture)
    except TypeError:
        capsys = capture.CaptureFixture(capture.SysCapture, None)
    getattr(capsys, '_start')()

    # Re-run httpretty on Windows (due to lack of forking).
    if sys.platform == 'win32':
        httpretty.enable()
        if cached_responses:
            for url, body in cached_responses.items():
                httpretty.register_uri(httpretty.GET, url, body=body)

    # Run.
    result = run_build_main(docs_dir, html_dir, overflow)
    stdout, stderr = capsys.readouterr()
    queue.put((stdout, stderr))
    if result != 0:
        raise RuntimeError(result, stdout, stderr)


def pytest_namespace():
    """Add objects to the pytest namespace.

    E.g. Returning {'func': lambda: True} allows import pytest; assert pytest.func() is True.

    :return: Namespace names and objects.
    :rtype: dict
    """
    def add_page(root, name, append=''):
        """Add a page to the sample Sphinx docs.

        :param py.path.local root: Path to docs root dir.
        :param str name: Page name.
        :param str append: Append text to RST document body.

        :return: Path to new page RST file.
        :rtype: py.path.local
        """
        root.join('contents.rst').write('    {}\n'.format(name), mode='a')
        page = root.join('{}.rst'.format(name))
        page.write('.. _{}:\n\n{}\n{}\n\n{}'.format(name, name.capitalize(), '=' * len(name), append))
        return page

    def build_isolated(docs_dir, html_dir, cached_responses, overflow=None):
        """Run build_main() through multiprocessing.Process.

        :param str docs_dir: Path to input docs directory.
        :param str html_dir: Path to output html directory.
        :param dict cached_responses: URL keys and serialized JSON values.
        :param iter overflow: Append these args to sphinx-build call.

        :return: Exit code of subprocess, stdout, and stderr.
        :rtype: tuple
        """
        queue = multiprocessing.Queue()
        args = docs_dir, html_dir, cached_responses, queue, overflow
        child = multiprocessing.Process(target=run_build_main_post_multiprocessing, args=args)
        child.start()
        child.join()
        result = child.exitcode
        try:
            stdout, stderr = queue.get(False)
        except multiprocessing.queues.Empty:
            stdout, stderr = '', ''
        return result, stdout, stderr

    return dict(add_page=add_page, build_isolated=build_isolated)


@pytest.fixture
def docs(tmpdir):
    """Create sample docs used in this test module.

    :param tmpdir: pytest fixture.

    :return: Path to docs root.
    :rtype: py.path
    """
    root = tmpdir.ensure_dir('docs')

    # Create Sphinx config.
    root.join('conf.py').write("extensions = ['sphinxcontrib.imgur']\nimgur_client_id = 'a0b1c2d3e4f56789'\n")

    # Create Sphinx docs.
    root.join('contents.rst').write(
        'Test\n'
        '====\n'
        '\n'
        'Sample documentation.\n'
        '\n'
        '.. toctree::\n'
        '    ignore\n'
    )
    root.join('ignore.rst').write('.. _ignore:\n\nIgnore\n======\n\nHello World.\n')

    return root
