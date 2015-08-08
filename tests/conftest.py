"""PyTest fixtures."""

import pytest

TMPDIRS = dict()


@pytest.fixture
def tmpdir_module(request, tmpdir):
    """A tmpdir fixture for the module scope. Persists throughout the module."""
    return TMPDIRS.setdefault(request.module.__name__, tmpdir)
