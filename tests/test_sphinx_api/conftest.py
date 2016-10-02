"""Fixtures for tests in this directory."""

import pytest


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
    pages = ['one', 'two']
    root.join('contents.rst').write(
        'Test\n'
        '====\n'
        '\n'
        'Sample documentation.\n'
        '\n'
        '.. toctree::\n' + ''.join('    {}\n'.format(p) for p in pages)
    )
    for page in pages:
        root.join('{}.rst'.format(page)).write('.. _{page}:\n\n{Page}\n{divider}\n\nHello World.\n'.format(
            page=page, Page=page.capitalize(), divider='=' * len(page)
        ))

    # Add roles/directives to some pages.
    root.join('one.rst').write('Title: :imgur-title:`a/V76cJ`;\nDescription: :imgur-description:`a/VMlM6`;\n', mode='a')
    root.join('two.rst').write('Title: :imgur-title:`611EovQ`;\nDescription: :imgur-description:`2QcXR3R`;\n', mode='a')

    return root
