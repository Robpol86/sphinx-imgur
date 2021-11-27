"""PyTest fixtures."""

import pytest
from freezegun import freeze_time


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
        self.messages.append(["debug", message])

    def debug2(self, message, *args, **kwargs):
        """Debug2 'logger'.

        :param str message: Log message.
        """
        if args or kwargs:
            message = message % (args or kwargs)
        self.messages.append(["debug2", message])

    def info(self, message):
        """Info 'logger'.

        :param str message: Log message.
        """
        self.messages.append(["info", message])

    def warn(self, message, location):
        """Warning 'logger'.

        :param str message: Log message.
        :param str location: file path and line number.
        """
        self.messages.append(["warn", message, location])


@pytest.fixture
def app():
    """Return FakeApp() instance."""
    return FakeApp()


@pytest.yield_fixture
def freezer():
    """Mock a specific tine."""
    with freeze_time("2016-09-20") as frozen_datetime:
        yield frozen_datetime


@pytest.fixture(scope="module")
def tmpdir_module(request, tmpdir_factory):
    """A tmpdir fixture for the module scope. Persists throughout the module.

    :param request: pytest fixture.
    :param tmpdir_factory: pytest fixture.
    """
    return tmpdir_factory.mktemp(request.module.__name__)
