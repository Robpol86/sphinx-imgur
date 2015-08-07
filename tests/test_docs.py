"""Make sure documentation builds successfully."""

from subprocess import check_output, STDOUT
from textwrap import dedent

import py


def test(tmpdir):
    """Test documentation."""
    docs_dir = py.path.local(__file__).dirpath().join('..', 'docs')
    for file_path in docs_dir.visit(fil=lambda p: p.ext in ('.py', '.rst')):
        if '_build' in file_path.dirname:
            continue
        target_path = tmpdir.join(file_path.relto(docs_dir))
        target_path.dirpath().ensure_dir()
        file_path.copy(target_path)

    tmpdir.join('conf.py').write(mode='a', data=dedent("""\
        imgur_api_test_response = {
            'a/hWyW0': dict(description='Desc.', title='Title'),
            '7WTPx0v': dict(description='Desc2.', title='Title2'),
        }
        """))

    command = ['sphinx-build', '-a', '-E', '-n', '-N', '-W', '-b', 'html', '.', '_build/html']
    check_output(command, cwd=str(tmpdir), stderr=STDOUT)
