"""Test Sphinx event handlers call order and count."""

import pytest
from docutils.parsers.rst import directives, roles
from sphinx import application

from sphinxcontrib import imgur
from tests.helpers import init_sample_docs, track_call


@pytest.mark.parametrize('parallel', [0, 1, 2])
def test(monkeypatch, tmpdir, parallel):
    """Test when sphinx-build runs for the first time."""
    monkeypatch.setattr(directives, '_directives', getattr(directives, '_directives').copy())
    monkeypatch.setattr(roles, '_roles', getattr(roles, '_roles').copy())
    init_sample_docs(tmpdir)
    srcdir = confdir = str(tmpdir)
    outdir = tmpdir.join('_build', 'html')
    doctree = outdir.join('doctrees').ensure(dir=True, rec=True)
    calls = list()
    monkeypatch.setattr(imgur, 'event_discover_new_ids', track_call(calls, imgur.event_discover_new_ids))
    monkeypatch.setattr(imgur, 'event_merge_info', track_call(calls, imgur.event_merge_info))
    monkeypatch.setattr(imgur, 'event_purge_orphaned_ids', track_call(calls, imgur.event_purge_orphaned_ids))
    monkeypatch.setattr(imgur, 'event_query_api_update_cache', track_call(calls, imgur.event_query_api_update_cache))
    monkeypatch.setattr(imgur, 'event_update_imgur_nodes', track_call(calls, imgur.event_update_imgur_nodes))

    app = application.Sphinx(srcdir, confdir, str(outdir), str(doctree), 'html', warningiserror=True, parallel=parallel)
    app.builder.build_all()

    expected = [
        'event_purge_orphaned_ids',
        'event_discover_new_ids',
        'event_purge_orphaned_ids',
        'event_discover_new_ids',
        'event_purge_orphaned_ids',
        'event_discover_new_ids',
        'event_query_api_update_cache',
        'event_update_imgur_nodes',
        'event_update_imgur_nodes',
        'event_update_imgur_nodes'
    ]
    assert expected == calls
