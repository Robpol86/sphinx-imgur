"""Common/helper code for all test modules."""

import os
from functools import wraps
from textwrap import dedent


BASE_CONFIG = dedent("""\
    import sys
    sys.path.append('{}')
    extensions = ['sphinxcontrib.imgur']
    master_doc = 'index'
    nitpicky = True
    """).format(os.path.join(os.path.dirname(__file__), '..'))


def init_sample_docs(tmpdir):
    """Create sample Sphinx documentation.

    :param tmpdir: PyTest builtin tmpdir fixture (py.path instance).
    """
    # Write conf.py.
    conf_py = tmpdir.join('conf.py')
    conf_py.write(BASE_CONFIG + dedent("""\
        imgur_api_test_response = {
            'a/abc1234': dict(title='Title', description='Desc'),
            '1234abc': dict(title='Title2', description='Desc2'),
        }
        """))

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

        | The title is: :imgur-title:`a/abc1234`.
        | And the description: :imgur-description:`a/abc1234`
        """))
    doc2_rst.write(dedent("""\
        .. _doc2:

        Images Go Here
        ==============

        | The title is: :imgur-title:`1234abc`.
        """))


def change_doc(tmpdir):
    """Change one document.

    :param tmpdir: PyTest builtin tmpdir fixture (py.path instance).
    """
    tmpdir.join('doc1.rst').write(dedent("""\
        .. _doc1:

        Albums Go Here
        ==============

        | The title is still: :imgur-title:`a/abc1234`.
        | And the description: :imgur-description:`a/abc1234`
        """))


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
