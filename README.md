# sphinx-imgur

Embed [Imgur](https://imgur.com) images and albums in Sphinx documents/pages.

* Python 3.6, 3.7, 3.8, and 3.9 supported on Linux, macOS, and Windows.

📖 Full documentation: https://sphinx-imgur.readthedocs.io

[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]
[![PyPI Downloads][pypi-dl-badge]][pypi-dl-link]

[github-ci]: https://github.com/Robpol86/sphinx-imgur/actions/workflows/ci.yml/badge.svg?branch=main
[github-link]: https://github.com/Robpol86/sphinx-imgur/actions/workflows/ci.yml
[codecov-badge]: https://codecov.io/gh/Robpol86/sphinx-imgur/branch/main/graph/badge.svg
[codecov-link]: https://codecov.io/gh/Robpol86/sphinx-imgur
[rtd-badge]: https://readthedocs.org/projects/sphinx-imgur/badge/?version=latest
[rtd-link]: https://sphinx-imgur.readthedocs.io/en/latest/?badge=latest
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black
[pypi-badge]: https://img.shields.io/pypi/v/sphinx-imgur.svg
[pypi-link]: https://pypi.org/project/sphinx-imgur
[pypi-dl-badge]: https://img.shields.io/pypi/dw/sphinx-imgur?label=pypi%20downloads
[pypi-dl-link]: https://pypistats.org/packages/sphinx-imgur

## Quickstart

To install run the following:

```bash
pip install sphinx-imgur
```

To use in Sphinx simply add to your `conf.py`:

```python
extensions = ["sphinx_imgur.imgur"]
```

And in your Sphinx documents:

```rst
.. imgur:: 611EovQ
```

Or to use Imgur's embed feature with an album:

```rst
.. imgur-embed:: a/9YZHA
```
