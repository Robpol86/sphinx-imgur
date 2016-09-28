"""Common/helper code for all test modules."""

import os
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
        imgur_api_test_response_albums = {
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
