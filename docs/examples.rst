.. _examples:

========
Examples
========

This page shows several example use cases for the extension.

Embedded Items
==============

Embed Imgur albums or images using their JavaScript option. This is the same as the "Embed album" link when you view
an album on imgur.com.

Album With Details
------------------

.. code-block:: rst

    .. imgur-embed:: hWyW0
        :album: True

.. imgur-embed:: hWyW0
    :album: True

Album Without Details
---------------------

.. code-block:: rst

    .. imgur-embed:: 9YZHA
        :album: True
        :hide_post_details: True

.. imgur-embed:: 9YZHA
    :album: True
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
