"""Test Sphinx event handlers call order and count."""

from functools import wraps
from textwrap import dedent

import py
import pytest
from docutils.parsers.rst import directives, roles
from sphinx import application

from sphinxcontrib import imgur


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
        imgur_api_test_response = {{
            'a/abc1234': dict(title='Title', description='Desc'),
            '1234abc': dict(title='Title2', description='Desc2'),
        }}
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
    monkeypatch.setattr(directives, '_directives', getattr(directives, '_directives').copy())
    monkeypatch.setattr(roles, '_roles', getattr(roles, '_roles').copy())
    create_first_env(tmpdir)
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
