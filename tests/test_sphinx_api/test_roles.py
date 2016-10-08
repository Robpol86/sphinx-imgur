"""Test Sphinx roles."""

import pytest


@pytest.mark.parametrize('role', ['imgur-title', 'imgur-description'])
@pytest.mark.parametrize('album', [False, True])
@pytest.mark.httpretty
def test_bad_imgur_id(tmpdir, docs, album, role):
    """Test invalid imgur_id value.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param bool album: Invalid album vs image ID.
    :param str role: Sphinx role to test.
    """
    iid = 'a/inv@lid' if album else 'inv@lid'
    docs.join('one.rst').write('Testing: :{}:`{}`;\n'.format(role, iid), mode='a')
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result != 0
    assert 'WARNING' not in stderr
    assert not html.listdir('*.html')
    expected = 'Invalid Imgur ID specified. Must be 5-10 letters and numbers. Got "{id}" from ":{role}:`{id}`".'
    assert expected.format(id=iid, role=role) in stderr


@pytest.mark.httpretty
def test_valid(tmpdir, docs, httpretty_common_mock):
    """Test valid imgur_id value.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param httpretty_common_mock: conftest fixture.
    """
    pytest.add_page(docs, 'one', (
        'Album Title: :imgur-title:`a/VMlM6`;\n'
        'Album Description: :imgur-description:`a/VMlM6`;\n'
        'Image Title: :imgur-title:`611EovQ`;\n'
        'Image Description: :imgur-description:`611EovQ`;\n'
    ))
    html = tmpdir.join('html')
    result, stderr = pytest.build_isolated(docs, html, httpretty_common_mock)[::2]

    assert result == 0
    assert not stderr
    contents = html.join('one.html').read()
    assert 'Album Title: Screenshots;' in contents
    assert 'Album Description: Screenshots of my various devices.;' in contents
    assert 'Image Title: Work, June 1st, 2016: Uber;' in contents
    expected = ('Image Description: Right before I moved desks for the 6th time in 1.5 years. '
                'I lost my nice window desk, oh well.;')
    assert expected in contents
