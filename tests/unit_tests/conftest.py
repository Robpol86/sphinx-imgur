"""pytest fixtures."""
from pathlib import Path
from typing import Dict, List

import pytest
from bs4 import BeautifulSoup, element
from sphinx.testing.path import path
from sphinx.testing.util import SphinxTestApp
from TexSoup import TexNode, TexSoup

pytest_plugins = "sphinx.testing.fixtures"  # pylint: disable=invalid-name


@pytest.fixture(scope="session")
def rootdir() -> path:
    """Used by sphinx.testing, return the directory containing all test docs."""
    return path(__file__).parent.abspath() / "test_docs"


@pytest.fixture(name="sphinx_app")
def _sphinx_app(app: SphinxTestApp) -> SphinxTestApp:
    """Instantiate a new Sphinx app per test function."""
    app.build()
    yield app


@pytest.fixture()
def ls_out_files(sphinx_app: SphinxTestApp) -> Dict[str, int]:
    """Return file names and sizes in output directory."""
    results = {}
    outdir = sphinx_app.outdir
    for name in outdir.listdir():
        file_ = outdir / name
        if file_.isfile():
            results[name] = file_.stat().st_size
    return results


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


@pytest.fixture(name="python_tex")
def _python_tex(sphinx_app: SphinxTestApp) -> TexSoup:
    """Read and parse generated test LaTeX python.tex."""
    try:
        text = (Path(sphinx_app.outdir) / "python.tex").read_text(encoding="utf8")
    except FileNotFoundError:
        text = (Path(sphinx_app.outdir) / "Python.tex").read_text(encoding="utf8")
    return TexSoup(text)


@pytest.fixture()
def latex_graphics(python_tex: TexSoup) -> List[TexNode]:
    """Return all sphinxincludegraphics in python.tex."""
    return python_tex.find_all("sphinxincludegraphics")
