"""PyTest fixtures."""

import pytest


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
