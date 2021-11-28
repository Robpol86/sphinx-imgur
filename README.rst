============
sphinx-imgur
============

Embed `Imgur <http://imgur.com/>`_ images and albums in documents.

📖 Full documentation: https://robpol86.github.io/sphinx-imgur

.. image:: https://img.shields.io/appveyor/ci/Robpol86/sphinx-imgur/main.svg?style=flat-square&label=AppVeyor%20CI
    :target: https://ci.appveyor.com/project/Robpol86/sphinx-imgur
    :alt: Build Status Windows

.. image:: https://img.shields.io/travis/Robpol86/sphinx-imgur/main.svg?style=flat-square&label=Travis%20CI
    :target: https://travis-ci.org/Robpol86/sphinx-imgur
    :alt: Build Status

.. image:: https://img.shields.io/codecov/c/github/Robpol86/sphinx-imgur/main.svg?style=flat-square&label=Codecov
    :target: https://codecov.io/gh/Robpol86/sphinx-imgur
    :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/sphinx-imgur.svg?style=flat-square&label=Latest
    :target: https://pypi.python.org/pypi/sphinx-imgur
    :alt: Latest Version

Quickstart
==========

Install:

.. code:: bash

    pip install sphinx-imgur

.. changelog-section-start

Changelog
=========

This project adheres to `Semantic Versioning <http://semver.org/>`_.

Unreleased
----------

Added
    * Sphinx 1.8 support.

Changed
    * Renamed project from ``sphinxcontrib-imgur`` to ``sphinx-imgur``
    * Re-licensed from MIT to BSD 2-Clause

Removed
    * Title and description roles.
    * Support for albums in image directive.
    * ``imgur_target_default_gallery`` and ``target_gallery`` options.
    * Caching and querying the Imgur API.
    * Auto-detecting size, extension/type, and album images.
    * Dropped Python 2.7 and <3.6 support

2.0.1 - 2016-10-15
------------------

Changed
    * Adding newlines after imgur-image image/a HTML tags. Without those newlines Chrome doesn't display gaps between
      images on the same line.

2.0.0 - 2016-10-15
------------------

Added
    * Python 3.5 support (Linux/OS X and Windows).
    * ``imgur-image`` directive.
    * ``imgur_target_default_gallery``, ``imgur_target_default_largest``, and ``imgur_target_default_page`` conf
      variables.

Changed
    * Rewrote most of the library. Previous code was ugly, complicated, and hard to follow.

Removed
    * PyPy support.
    * ``imgur_api_test_response`` conf variable.

1.0.0 - 2015-08-09
------------------

* Initial release.

.. changelog-section-end
