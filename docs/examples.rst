.. _examples:

========
Examples
========

This page shows several example use cases for the extension.

Embedded Directive
==================

Embed Imgur albums or images using their JavaScript option. This is the same as the "Embed album" link when you view
an album on imgur.com.

.. note::

    If you're viewing these docs locally (e.g. the URL starts with ``file://``), then the albums/images below won't
    load. The Imgur JavaScript is loaded from **//s.imgur.com/min/embed.js** so when viewing locally it tries and fails
    to find file://s.imgur.com/min/embed.js.

    A work around for this is to view these docs from a local HTTP server. You can quickly fire one up with one of these
    two commands:

    .. code-block:: bash

        cd docs/_build/html && python2.7 -m SimpleHTTPServer 8080
        cd docs/_build/html && python3.4 -m http.server 8080

    Then browse to: http://localhost:8080/

Album With Details
------------------

.. code-block:: rst

    .. imgur-embed:: a/hWyW0

.. imgur-embed:: a/hWyW0

Album Without Details
---------------------

.. code-block:: rst

    .. imgur-embed:: a/9YZHA
        :hide_post_details: True

.. imgur-embed:: a/9YZHA
    :hide_post_details: True

Image With Details
------------------

.. code-block:: rst

    .. imgur-embed:: 7WTPx0v

.. imgur-embed:: 7WTPx0v

Image Without Details
---------------------

.. code-block:: rst

    .. imgur-embed:: Srt4owo
        :hide_post_details: True

.. imgur-embed:: Srt4owo
    :hide_post_details: True

Image Directive
===============

.. code-block:: rst

    .. imgur-image:: 611EovQ

.. imgur-image:: 611EovQ
