"""pytest fixtures."""
from pathlib import Path
from typing import List

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempdirFactory
from bs4 import BeautifulSoup, element
from sphinx.testing.path import path
from sphinx.testing.util import SphinxTestApp

pytest_plugins = "sphinx.testing.fixtures"  # pylint: disable=invalid-name


@pytest.fixture(scope="session")
def sphinx_test_tempdir(request: FixtureRequest, tmpdir_factory: TempdirFactory) -> path:
    """Used by sphinx.testing, return the temporary working directory used by Sphinx."""
    return path(tmpdir_factory.mktemp(request.session.name)).abspath()


@pytest.fixture(scope="session")
def rootdir() -> path:
    """Used by sphinx.testing, return the directory containing all test docs."""
    return path(__file__).parent.abspath() / "test_docs"


@pytest.fixture(name="sphinx_app")
def _sphinx_app(app: SphinxTestApp) -> SphinxTestApp:
    """Instantiate a new Sphinx app per test function."""
    app.build()
    yield app


@pytest.fixture(name="index_html")
def _index_html(sphinx_app: SphinxTestApp) -> BeautifulSoup:
    """Read and parse generated test index.html."""
    text = (Path(sphinx_app.outdir) / "index.html").read_text(encoding="utf8")
    return BeautifulSoup(text, "html.parser")


@pytest.fixture()
def img_tags(index_html: BeautifulSoup) -> List[element.Tag]:
    """Return all <img> tags in index.html."""
    return index_html.find_all("img")


@pytest.fixture()
def blockquote_tags(index_html: BeautifulSoup) -> List[element.Tag]:
    """Return all <blockquote> tags in index.html."""
    return index_html.find_all("blockquote")
