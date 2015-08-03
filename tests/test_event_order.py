"""Test Sphinx event handlers call order and count."""

from textwrap import dedent

import docutils.nodes
import py
import pytest
from docutils.parsers.rst import directives, roles
from sphinx import application

from sphinxcontrib import imgur


def create_first_env(tmpdir):
    """Create a new test environment."""
    # Write conf.py.
    conf_py = tmpdir.join('conf.py')
    conf_py.write(dedent("""\
        import sys
        sys.path.append('{}')
        extensions = ['sphinxcontrib.imgur']
        master_doc = 'index'
        nitpicky = True
        """).format(py.path.local(__file__).join('..', '..')))

    # Write rst files.
    index_rst, doc1_rst, doc2_rst = tmpdir.join('index.rst'), tmpdir.join('doc1.rst'), tmpdir.join('doc2.rst')
    index_rst.write(dedent("""\
        ====
        Main
        ====

        .. toctree::
            :maxdepth: 2

            doc1
            doc2
        """))
    doc1_rst.write(dedent("""\
        .. _doc1:

        Albums Go Here
        ==============

        The title is: :imgur-title:`a/abc1234`.
        And the description: :imgur-description:`a/abc1234`
        """))
    doc2_rst.write(dedent("""\
        .. _doc2:

        Images Go Here
        ==============

        The title is: :imgur-title:`1234abc`.
        """))


@pytest.mark.parametrize('parallel', [0, 1, 2])
def test(monkeypatch, tmpdir, parallel):
    """Test when sphinx-build runs for the first time."""
    create_first_env(tmpdir)
    monkeypatch.setattr(directives, '_directives', getattr(directives, '_directives').copy())
    monkeypatch.setattr(roles, '_roles', getattr(roles, '_roles').copy())

    srcdir = confdir = str(tmpdir)
    outdir = tmpdir.join('_build', 'html')
    doctreedir = outdir.join('doctrees').ensure(dir=True, rec=True)

    func_calls = list()

    def euin(*args):
        """Handle testing event_update_imgur_nodes()."""
        func_calls.append('event_update_imgur_nodes')
        for node_class in (imgur.nodes.ImgurDescriptionNode, imgur.nodes.ImgurTitleNode):
            for node in args[1].traverse(node_class):
                node.replace_self([docutils.nodes.Text('Placeholder')])

    monkeypatch.setattr(imgur, 'event_discover_new_ids', lambda *_: func_calls.append('event_discover_new_ids'))
    monkeypatch.setattr(imgur, 'event_merge_info', lambda *_: func_calls.append('event_merge_info'))
    monkeypatch.setattr(imgur, 'event_purge_orphaned_ids', lambda *_: func_calls.append('event_purge_orphaned_ids'))
    monkeypatch.setattr(imgur, 'event_query_api_update_cache',
                        lambda *_: func_calls.append('event_query_api_update_cache'))
    monkeypatch.setattr(imgur, 'event_update_imgur_nodes', euin)

    app = application.Sphinx(srcdir, confdir, str(outdir), str(doctreedir), 'html', warningiserror=True,
                             parallel=parallel)
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
    assert expected == func_calls
