.. _usage:

=====
Usage
=====

This page documents how to get started with the extension.

Make sure that you've already :ref:`installed <install>` it.

Configuration
=============

If you're just trying to `embed <http://imgur.com/blog/2015/04/07/embed-your-post-anywhere/>`_ albums or images in your
Sphinx documents you don't need to add anything extra to your ``conf.py``. Just include ``sphinx_imgur.imgur`` in
``extensions``.

If you'd like to use other features in this extension then you'll need to generate a "Client ID" by going to the
`Register an Application <https://api.imgur.com/oauth2/addclient>`_ page on Imgur. You'll just need the very basics. As
of this writing you put in something in Application Name (e.g. your project name or title of your documentation), set
Authorization Type to "Anonymous usage without user authorization" and whatever for your email and description.

Here is a sample file with the two things you need to do for advanced features:

.. code-block:: python

    # General configuration.
    author = 'Your Name Here'
    copyright = '2015, Your Name Here'
    exclude_patterns = ['_build']
    extensions = ['sphinx_imgur.imgur']  # Add to this list.
    master_doc = 'index'
    project = 'my-cool-project'
    release = '1.0'
    version = '1.0'

All Config Options
==================

.. attribute:: imgur_hide_post_details

    *Default: False*

    The default value of ``hide_post_details`` for :rst:dir:`imgur-embed`. Overridden in the directive.

.. attribute:: imgur_target_default_page

    *Default: False*

    Links to the image's page on Imgur by default (with the share buttons, etc).

Directives
==========

These are the available Sphinx/RST `directives <http://www.sphinx-doc.org/en/stable/rest.html#directives>`_.
To see them in action visit the :ref:`Examples` section.

.. rst:directive:: imgur-embed

    Embed an Imgur image or album using Imgur's fancy javascript.

    .. attribute:: hide_post_details

        Overrides :attr:`imgur_hide_post_details` for this specific embed.

.. rst:directive:: imgur-image

    Equivalent to the built in `image directive <http://docutils.sourceforge.net/docs/ref/rst/directives.html#image>`_.
    Display an Imgur image in the document the same way a regular image is displayed.

    .. attribute:: align

        Same as the regular image directive. Align image horizontally. Valid values: "left", "center", or "right"

    .. attribute:: alt

        Same as the regular image directive. Alternate text in the ``<img>`` tag.

    .. attribute:: height

        Same as the regular image directive. Resizes the image vertically maintaining the aspect ratio.

    .. attribute:: scale

        Same as the regular image directive. Resizes the image maintaining the aspect ratio.

    .. attribute:: target_page

        Image will link to its page on Imgur (with the share buttons, etc).


    .. attribute:: target

        Same as the regular image directive. Image will link to this URL. Takes precedence over :attr:`target_page`.

    .. attribute:: width

        Same as the regular image directive. Resizes the image horizontally maintaining the aspect ratio.
