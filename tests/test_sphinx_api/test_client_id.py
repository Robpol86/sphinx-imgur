"""Test client_id value."""

import pytest


@pytest.mark.parametrize('invalid', [False, True])
@pytest.mark.httpretty
def test_bad_client_id(tmpdir, docs, invalid):
    """Test unset or invalid client_id values.

    :param tmpdir: pytest fixture.
    :param docs: conftest fixture.
    :param bool invalid: Set invalid client_id instead of unsetting.
    """
    html = tmpdir.join('html')

    # Remove/invalidate client_id line.
    conf_py = '\n'.join(l for l in docs.join('conf.py').read().splitlines() if 'imgur_client_id' not in l)  # Remove.
    if invalid:
        conf_py += "\nimgur_client_id = 'inv@lid'"
    docs.join('conf.py').write(conf_py)

    # Run.
    result, stderr = pytest.build_isolated(docs, html, None)[::2]

    assert result != 0
    assert 'WARNING' not in stderr
    assert not html.listdir('*.html')
    if invalid:
        assert 'imgur_client_id config value must be 5-30 lower case hexadecimal characters only.' in stderr
    else:
        assert 'imgur_client_id config value must be set for Imgur API calls.' in stderr
