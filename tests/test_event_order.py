"""Test Sphinx event handlers call order and count."""

import pytest
from docutils.parsers.rst import directives, roles
from sphinx import application

from sphinxcontrib import imgur
from tests.helpers import init_sample_docs, track_call

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
    'event_update_imgur_nodes'
])


@pytest.mark.parametrize('iteration', range(1))
def test(monkeypatch, tmpdir_module, iteration):
    """Test when sphinx-build runs multiple times."""
    calls = list()
    for func_name, func in ((f, getattr(imgur, f)) for f in dir(imgur) if f.startswith('event_')):
        monkeypatch.setattr(imgur, func_name, track_call(calls, func))

    monkeypatch.setattr(directives, '_directives', getattr(directives, '_directives').copy())
    monkeypatch.setattr(roles, '_roles', getattr(roles, '_roles').copy())
    srcdir = confdir = str(tmpdir_module)
    outdir = tmpdir_module.join('_build', 'html')
    doctree = outdir.join('doctrees')
    if not iteration:  # First run.
        init_sample_docs(tmpdir_module)
        doctree.ensure_dir()

    app = application.Sphinx(srcdir, confdir, str(outdir), str(doctree), 'html', warningiserror=True)
    app.builder.build_all()

    assert EXPECTED[iteration] == calls
