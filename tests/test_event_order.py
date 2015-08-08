"""Test Sphinx event handlers call order and count."""

import time

import pytest
from docutils.parsers.rst import directives, roles
from sphinx import application

from sphinxcontrib import imgur
from tests.helpers import change_doc, init_sample_docs, remove_doc, track_call

EXPECTED = list()
EXPECTED.append([
    'event_purge_orphaned_ids',
    'event_discover_new_ids',
    'event_purge_orphaned_ids',
    'event_discover_new_ids',
    'event_purge_orphaned_ids',
    'event_discover_new_ids',
    'event_query_api_update_cache',
    'event_update_imgur_nodes',
    'event_update_imgur_nodes',
    'event_update_imgur_nodes',
])
EXPECTED.append([
    'event_query_api_update_cache',  # TODO remove
    'event_update_imgur_nodes',
    'event_update_imgur_nodes',
    'event_update_imgur_nodes',
])
EXPECTED.append([
    'event_purge_orphaned_ids',
    'event_discover_new_ids',
    'event_query_api_update_cache',
    'event_update_imgur_nodes',
    'event_update_imgur_nodes',
    'event_update_imgur_nodes',
])
EXPECTED.append([
    'event_purge_orphaned_ids',  # Purge IDs for removed file.
    'event_purge_orphaned_ids',  # index.rst changed too, this and next line is because of that.
    'event_discover_new_ids',
    'event_query_api_update_cache',
    'event_update_imgur_nodes',
    'event_update_imgur_nodes',
])


@pytest.mark.parametrize('iteration', range(4))
def test(monkeypatch, tmpdir_module, iteration):
    """Test when sphinx-build runs multiple times.

    Iterations:
    0: First run.
    1: No changes.
    2: One file changed.
    3: One file removed.
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
    out_doc2_html = outdir.join('doc2.html').read() if iteration != 3 else outdir.join('doc2.html').check()

    assert EXPECTED[iteration] == calls

    if iteration < 2:
        assert 'The title is: Title.' in out_doc1_html
        assert 'And the description: Desc' in out_doc1_html
        assert 'The title is: Title2.' in out_doc2_html
    elif iteration == 2:
        assert 'The title is now: New Title.' in out_doc1_html
        assert 'And the description: Desc' in out_doc1_html
        assert 'The title is: Title2.' in out_doc2_html
    else:
        assert 'The title is now: New Title.' in out_doc1_html
        assert 'And the description: Desc' in out_doc1_html
        assert out_doc2_html is False
