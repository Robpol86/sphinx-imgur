"""Test Sphinx event handlers call order and count."""

import time
from functools import wraps

import pytest
from docutils.parsers.rst import directives, roles
from sphinx import application

from sphinxcontrib import imgur
from tests.helpers import change_doc, init_sample_docs

EXPECTED = list()
EXPECTED.append([
    'event_doctree_read',
    'event_doctree_read',
    'event_doctree_read',
    'event_env_updated',
    'event_doctree_resolved',
    'event_doctree_resolved',
    'event_doctree_resolved',
])
EXPECTED.append([
    'event_env_updated',
    'event_doctree_resolved',
    'event_doctree_resolved',
    'event_doctree_resolved',
])
EXPECTED.append([
    'event_doctree_read',
    'event_env_updated',
    'event_doctree_resolved',
    'event_doctree_resolved',
    'event_doctree_resolved',
])
EXPECTED.append([
    'event_doctree_read',
    'event_env_updated',
    'event_doctree_resolved',
    'event_doctree_resolved',
])


def remove_doc(tmpdir, outdir):
    """Remove one document.

    :param tmpdir: PyTest builtin tmpdir fixture (py.path instance).
    :param outdir: py.path instance to output directory.
    """
    index_rst = tmpdir.join('index.rst').read()
    new_index = '\n'.join(index_rst.splitlines()[:-1])
    tmpdir.join('index.rst').write(new_index)
    tmpdir.join('doc2.rst').remove()
    outdir.join('doc2.html').remove()


def track_call(call_list, func):
    """Decorator that appends to list the function name before calling said function.

    :param list call_list: List to append to.
    :param func: Function to call.

    :return: Wrapped function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        call_list.append(func.__name__)
        return func(*args, **kwargs)
    return wrapper


@pytest.mark.usefixtures('reset_sphinx')
@pytest.mark.parametrize('iteration', range(4))
def test(monkeypatch, tmpdir_module, iteration):
    """Test when sphinx-build runs multiple times.

    Iterations:
    0: First run.
    1: No changes.
    2: One file changed.
    3: One file removed.

    :param monkeypatch: pytest fixture.
    :param tmpdir_module: conftest fixture.
    :param int iteration: Scenario to test.
    """
    calls = list()
    for func_name, func in ((f, getattr(imgur, f)) for f in dir(imgur) if f.startswith('event_')):
        monkeypatch.setattr(imgur, func_name, track_call(calls, func))

    monkeypatch.setattr(directives, '_directives', getattr(directives, '_directives').copy())
    monkeypatch.setattr(roles, '_roles', getattr(roles, '_roles').copy())
    srcdir = confdir = str(tmpdir_module)
    outdir = tmpdir_module.join('_build', 'html')
    doctree = outdir.join('doctrees')

    if iteration == 0:
        init_sample_docs(tmpdir_module)
        doctree.ensure_dir()
    elif iteration == 2:
        time.sleep(2)
        change_doc(tmpdir_module)
    elif iteration == 3:
        time.sleep(2)
        remove_doc(tmpdir_module, outdir)

    app = application.Sphinx(srcdir, confdir, str(outdir), str(doctree), 'html', warningiserror=True)
    app.builder.build_all()
    out_doc1_html = outdir.join('doc1.html').read()
    out_doc2_html = outdir.join('doc2.html').read() if iteration < 3 else outdir.join('doc2.html').check()

    assert EXPECTED[iteration] == calls

    if iteration < 2:
        assert 'The title is: Title.' in out_doc1_html
        assert 'And the description: Desc' in out_doc1_html
        assert 'The title is: Title2.' in out_doc2_html
        return
    assert 'The title is still: Title.' in out_doc1_html
    assert 'And the description: Desc' in out_doc1_html
    if iteration < 3:
        assert 'The title is: Title2.' in out_doc2_html
    else:
        assert out_doc2_html is False
