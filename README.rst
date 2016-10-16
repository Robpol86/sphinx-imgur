===================
sphinxcontrib-imgur
===================

Embed `Imgur <http://imgur.com/>`_ images, albums, and their metadata in documents.

* Python 2.7, 3.3, 3.4, and 3.5 supported on Linux, OS X, and Windows (both 32 and 64 bit versions of Python).

📖 Full documentation: https://robpol86.github.io/sphinxcontrib-imgur

.. image:: https://img.shields.io/appveyor/ci/Robpol86/sphinxcontrib-imgur/master.svg?style=flat-square&label=AppVeyor%20CI
    :target: https://ci.appveyor.com/project/Robpol86/sphinxcontrib-imgur
    :alt: Build Status Windows

.. image:: https://img.shields.io/travis/Robpol86/sphinxcontrib-imgur/master.svg?style=flat-square&label=Travis%20CI
    :target: https://travis-ci.org/Robpol86/sphinxcontrib-imgur
    :alt: Build Status

.. image:: https://img.shields.io/codecov/c/github/Robpol86/sphinxcontrib-imgur/master.svg?style=flat-square&label=Codecov
    :target: https://codecov.io/gh/Robpol86/sphinxcontrib-imgur
    :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/sphinxcontrib-imgur.svg?style=flat-square&label=Latest
    :target: https://pypi.python.org/pypi/sphinxcontrib-imgur
    :alt: Latest Version

Quickstart
==========

Install:

.. code:: bash

    pip install sphinxcontrib-imgur

.. changelog-section-start

Changelog
=========

This project adheres to `Semantic Versioning <http://semver.org/>`_.

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
