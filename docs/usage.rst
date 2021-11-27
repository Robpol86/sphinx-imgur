.. _usage:

=====
Usage
=====

This page documents how to get started with the extension.

Make sure that you've already :ref:`installed <install>` it.

Configuration
=============

If you're just trying to `embed <http://imgur.com/blog/2015/04/07/embed-your-post-anywhere/>`_ albums or images in your
Sphinx documents you don't need to add anything extra to your ``conf.py``. Just include ``sphinxcontrib.imgur`` in
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
    extensions = ['sphinxcontrib.imgur']  # Add to this list.
    master_doc = 'index'
    project = 'my-cool-project'
    release = '1.0'
    version = '1.0'

    # Options for extensions.
    imgur_client_id = 'abc123def456789'  # Add this line to conf.py.

All Config Options
==================

.. attribute:: imgur_api_cache_ttl

    *Default: 172800 seconds (2 days)*

    Time in seconds before cached Imgur API entries are considered expired. Imgur's API has a request limit (even for
    simple things like getting an image's title) so this extension caches API replies. This lets you keep making
    multiple changes in your documentation without bombarding the API. Does not apply to embedded albums/images.

.. attribute:: imgur_client_id

    Imgur API Client ID to include in request headers. Required for API calls. More information in the section above.

.. attribute:: imgur_hide_post_details

    *Default: False*

    The default value of ``hide_post_details`` for :rst:dir:`imgur-embed`. Overridden in the directive.

.. attribute:: imgur_target_default_largest

    *Default: False*

    All :rst:dir:`imgur-image` images by default don't link to anything. Setting this to ``true`` results in all Imgur
    images to link to the original/full size version of the image by default. Ignored for albums.

.. attribute:: imgur_target_default_page

    *Default: False*

    Like :attr:`imgur_target_default_largest` but instead links to the image's page on Imgur by default (with the share
    buttons, etc). Overrides :attr:`imgur_target_default_largest` if both are set.

.. attribute:: imgur_target_default_gallery

    *Default: False*

    Like :attr:`imgur_target_default_largest` but instead links to the albums's gallery on Imgur by default. Only
    applies images or albums (which :rst:dir:`imgur-image` displays the cover image) released to the Imgur gallery,
    ignored otherwise. Overrides :attr:`imgur_target_default_largest` and :attr:`imgur_target_default_page` if all are
    set and image/album is in the gallery.

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

    .. attribute:: target_largest

        Image will link directly to the original/full size version. Not available for albums.

    .. attribute:: target_page

        Image will link to its page on Imgur (with the share buttons, etc). Takes precedence over
        :attr:`target_largest`.

    .. attribute:: target_gallery

        Image will link to its gallery page on Imgur if there is one, otherwise will be ignored. Takes precedence over
        :attr:`target_largest` and :attr:`target_page` if image is in Imgur gallery.

    .. attribute:: target

        Same as the regular image directive. Image will link to this URL. Takes precedence over :attr:`target_largest`,
        :attr:`target_page`, and :attr:`target_gallery`.

    .. attribute:: width

        Same as the regular image directive. Resizes the image horizontally maintaining the aspect ratio.
