"""Interface with Sphinx."""

import re

from sphinx.errors import ExtensionError

from sphinxcontrib.imgur.cache import initialize

RE_CLIENT_ID = re.compile(r'^[a-f0-9]{5,30}$')


def event_before_read_docs(app, env, _):
    """Called by Sphinx before phase 1 (reading).

    * Verify config.
    * Initialize the cache dict before reading any docs with an empty dictionary if not exists.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param sphinx.environment.BuildEnvironment env: Sphinx build environment.
    :param _: Not used.
    """
    client_id = app.config['imgur_client_id']
    if not client_id:
        raise ExtensionError('imgur_client_id config value must be set for Imgur API calls.')
    if not RE_CLIENT_ID.match(client_id):
        raise ExtensionError('imgur_client_id config value must be 5-30 lower case hexadecimal characters only.')
    env.imgur_api_cache = initialize(getattr(env, 'imgur_api_cache', None), (), ())
    assert app


def setup(app, version):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str version: Version of sphinxcontrib-imgur.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('imgur_api_cache_ttl', 172800, False)
    app.add_config_value('imgur_api_test_response_albums', None, False)
    app.add_config_value('imgur_api_test_response_images', None, False)
    app.add_config_value('imgur_client_id', None, False)
    app.add_config_value('imgur_hide_post_details', False, True)

    app.connect('env-before-read-docs', event_before_read_docs)

    return dict(parallel_read_safe=False, version=version)
