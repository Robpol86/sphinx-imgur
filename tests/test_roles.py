"""Test roles."""

from textwrap import dedent

import pytest
from docutils.parsers.rst import directives, roles
from sphinx import application

from sphinxcontrib.imgur.directives import ImgurError
from tests.helpers import BASE_CONFIG

TEST_CASES = [
    {'imgur-description': 'inv@lid', 'imgur-title': 'valid'},
    {'imgur-description': 'a/valid', 'imgur-title': 'inv@lid'},
    {'imgur-description': 'a/valid', 'imgur-title': 'valid'},
]


@pytest.mark.usefixtures('reset_sphinx')
@pytest.mark.parametrize('test_case', TEST_CASES)
def test(monkeypatch, tmpdir, test_case):
    """Test valid and invalid values.

    :param monkeypatch: pytest fixture.
    :param tmpdir: pytest fixture.
    :param dict test_case: Dict from TEST_CASES list.
    """
    # Write conf.py.
    conf_py = tmpdir.join('conf.py')
    conf_py.write(BASE_CONFIG + dedent("""\
        imgur_api_test_response_albums = {
            'a/valid': dict(title='!!One!!', description='!!Two!!'),
            'valid': dict(title='!!Three!!', description='!!Four!!'),
        }
        """))

    # Write index.rst.
    index_rst = tmpdir.join('index.rst')
    index_rst.write('====\nMain\n====\n\n.. toctree::\n    :maxdepth: 2\n\n')
    for k, v in test_case.items():
        index_rst.write(':{}:`{}`\n'.format(k, v), mode='a')

    monkeypatch.setattr(directives, '_directives', getattr(directives, '_directives').copy())
    monkeypatch.setattr(roles, '_roles', getattr(roles, '_roles').copy())

    srcdir = confdir = str(tmpdir)
    outdir = tmpdir.join('_build', 'html')
    doctreedir = outdir.join('doctrees').ensure(dir=True, rec=True)
    app = application.Sphinx(srcdir, confdir, str(outdir), str(doctreedir), 'html', warningiserror=True)

    if sorted(test_case.values()) == ['a/valid', 'valid']:
        app.builder.build_all()
        html_body = outdir.join('index.html').read()
        assert '!!Two!!' in html_body
        assert '!!Three!!' in html_body
        return

    with pytest.raises(ImgurError) as exc:
        app.builder.build_all()
    expected_error_base = 'Invalid Imgur ID specified. Must be 5-10 letters and numbers. Got "inv@lid" from "{}".'
    if test_case['imgur-description'] == 'inv@lid':
        expected_error = expected_error_base.format(':imgur-description:`inv@lid`')
    else:
        expected_error = expected_error_base.format(':imgur-title:`inv@lid`')
    assert expected_error == exc.value.args[0]
