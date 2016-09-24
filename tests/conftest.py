"""PyTest fixtures."""

import json
import logging
import os
import sys

import httpretty
import py
import pytest
import requests.packages

from sphinxcontrib.imgur.imgur_api import API_URL

CACHED_RESPONSES = dict()


class FakeApp(object):
    """Fake Sphinx app."""

    def __init__(self):
        """Constructor."""
        self.messages = list()

    def debug(self, message, *args, **kwargs):
        """Debug 'logger'.

        :param str message: Log message.
        """
        if args or kwargs:
            message = message % (args or kwargs)
        self.messages.append(['debug2', message])

    def debug2(self, message, *args, **kwargs):
        """Debug2 'logger'.

        :param str message: Log message.
        """
        if args or kwargs:
            message = message % (args or kwargs)
        self.messages.append(['debug2', message])

    def info(self, message):
        """Info 'logger'.

        :param str message: Log message.
        """
        self.messages.append(['info', message])

    def warn(self, message, location):
        """Warning 'logger'.

        :param str message: Log message.
        :param str location: file path and line number.
        """
        self.messages.append(['warn', message, location])


@pytest.fixture
def app():
    """Return FakeApp() instance."""
    return FakeApp()


@pytest.fixture(autouse=True, scope='session')
def config_httpretty():
    """Configure httpretty global variables."""
    httpretty.HTTPretty.allow_net_connect = False


@pytest.fixture(autouse=True, scope='session')
def config_requests():
    """Disable SSL warnings during testing."""
    if sys.version_info[:3] < (2, 7, 9):
        requests.packages.urllib3.disable_warnings()
    logging.getLogger('requests').setLevel(logging.WARNING)


@pytest.fixture(scope='module')
def tmpdir_module(request, tmpdir_factory):
    """A tmpdir fixture for the module scope. Persists throughout the module.

    :param request: pytest fixture.
    :param tmpdir_factory: pytest fixture.
    """
    return tmpdir_factory.mktemp(request.module.__name__)


@pytest.fixture
def reset_sphinx(request):
    """Reset Sphinx-related objects at the end of the test to prevent warnings between tests.

    :param request: pytest fixture.
    """
    def finalizer():
        from docutils.nodes import GenericNodeVisitor, SparseNodeVisitor
        for obj in (GenericNodeVisitor, SparseNodeVisitor):
            for attr in dir(obj):
                if 'imgur' in attr.lower():
                    delattr(obj, attr)
    request.addfinalizer(finalizer)


@pytest.fixture
def httpretty_common_mock():
    """Common mock Imgur data."""
    if not CACHED_RESPONSES:
        for path in py.path.local(__file__).dirpath().visit('response_*_*.json'):
            kind, imgur_id = os.path.splitext(path.basename)[0].split('_')[1:]
            url = API_URL.format(type=kind, id=imgur_id)
            body = json.dumps(json.load(path))  # Verify valid JSON here.
            CACHED_RESPONSES[url] = body
    for url, body in CACHED_RESPONSES.items():
        httpretty.register_uri(httpretty.GET, url, body=body)
