.. _usage:

=====
Usage
=====

Three directives are provided by the extension.

Images
======

.. imgur:: 611EovQ
    :alt: Example image

.. tabbed:: reStructuredText

    .. code-block:: rst

        .. imgur:: 611EovQ
            :alt: Example image

.. tabbed:: MyST Markdown

    .. code-block:: md

        ```{imgur} 611EovQ
        :alt: Example image
        ```

.. rst:directive:: imgur

    Equivalent to the built in `image directive <http://docutils.sourceforge.net/docs/ref/rst/directives.html#image>`_.
    Display an Imgur image in the document the same way a regular image is displayed.

    .. attribute:: align/alt/height/width/scale/target

        Same as the image directive.

    .. rst:directive:option:: ext

        Override the image file extension (useful for gifs). Can be implicitly set with ``.. imgur:: 7WTPx0v.gif``,
        otherwise the default extension is automatically used (can be changed with :option:`imgur_default_ext` in
        ``conf.py``).

        .. note:: Implicitly setting the extension implies :rst:dir:`imgur:fullsize` unless you set :rst:dir:`imgur:size`.

    .. rst:directive:option:: size

        Override the image size character (e.g. ``s``, ``b``, ``t``, ``m``, ``l``, ``h``). Can be implicitly set with
        ``.. imgur:: 611EovQs``, otherwise the default character is automatically used (can be changed with
        :option:`imgur_default_size` in ``conf.py``).

    .. rst:directive:option:: fullsize
        :type: flag

        Use the full size image URL instead of using smaller thumbnails. The example below will link to
        ``https://i.imgur.com/abcd123.jpg`` instead of ``https://i.imgur.com/abcd123h.jpg``:

        .. code-block:: rst

            .. imgur:: abcd123
                :fullsize:

    .. rst:directive:option:: img_src_format

        Override the image URL formatter used for the output. Otherwise the default formatter is used (can be changed with
        :option:`imgur_img_src_format` in ``conf.py``). Valid substitutions are ``%(id)s``, ``%(size)s``, and ``%(ext)s``.

    .. rst:directive:option:: notarget
        :type: flag

        When set the image won't automatically link to the full size image on Imgur. To override use the built in image
        ``:target:`` option.

Figures
=======

Just like the ``.. imgur::`` directive, ``imgur-figure`` is synonymous with the built in ``figure`` directive. The same
options are also available.

.. imgur-figure:: 611EovQ

    Put your caption here.

.. tabbed:: reStructuredText

    .. code-block:: rst

        .. imgur-figure:: 611EovQ
            
            Put your caption here.

.. tabbed:: MyST Markdown

    .. code-block:: md

        ```{imgur-figure} 611EovQ
        
        Put your caption here.
        ```

Albums
======

To embed albums use the ``imgur-embed`` directive, which relies on Imgur's official `embed unit`_.

.. imgur-embed:: a/hWyW0

.. tabbed:: reStructuredText

    .. code-block:: rst

        .. imgur-embed:: a/hWyW0

.. tabbed:: MyST Markdown

    .. code-block:: md

        ```{imgur-embed} a/hWyW0
        ```

.. rst:directive:: imgur-embed

    Besides :rst:dir:`imgur-embed:hide_post_details` the other options are mainly for sphinxext-opengraph_ compatibility.

    .. rst:directive:option:: hide_post_details

        Hide titles and descriptions in all album embeds when set to ``True``. Same as checking the **Hide Title** checkbox
        in the native Imgur `embed unit`_.

        .. note:: There's currently a bug where if you have two embed units on the same page, with just one of them with this
                  option, both embeds will shrink in vertical size causing the embed with titles and descriptions enabled to
                  appear cut off.

    .. rst:directive:option:: og_imgur_id

        Without this option Imgur album embeds will be ignored by sphinxext-opengraph_ (an embedded image works fine).
        Specify an image ID (typically one of the images in your album) so it shows up when posting your sphinx document link
        on Slack/Facebook/Discord/etc.

    .. rst:directive:option:: alt

        Passed to ``og:image:alt``, similar to the built in image ``:alt:`` option.

    .. rst:directive:option:: ext

        Override the file extension used in sphinxext-opengraph_, similar to :rst:dir:`imgur:ext`.

    .. rst:directive:option:: size

        Override the image size character for sphinxext-opengraph_. Similar to :rst:dir:`imgur:size`.

    .. rst:directive:option:: fullsize
        :type: flag

        Use the full size image URL instead of using smaller thumbnails for sphinxext-opengraph_. Similar to
        :rst:dir:`imgur:fullsize`.

    .. rst:directive:option:: img_src_format

        Override the image URL formatter for sphinxext-opengraph_. Similar to :rst:dir:`imgur:img_src_format`.

Configuration
=============

Set defaults for the extension in your ``conf.py`` file:

.. option:: imgur_default_ext

    *Default:* |LABEL_DEFAULT_EXT|

    Default file extension for images. When a document uses ``.. imgur:: abcd123`` the output will contain
    ``https://i.imgur.com/abcd123h.jpg``. This can be overridden implicitly in the directive by using
    ``.. imgur:: abcd123.gif`` or with the :rst:dir:`imgur:ext` option.

.. option:: imgur_default_size

    *Default:* |LABEL_DEFAULT_SIZE|

    Default image size to use in documents. To save visitors' bandwidth, when a document uses ``.. imgur:: abcd123``
    the output will contain ``https://i.imgur.com/abcd123h.jpg``. This can be overridden implicitly in the directive by using
    ``.. imgur:: abcd123s`` (for a small thumbnail) or with the :rst:dir:`imgur:size` option, or disabled all together
    with the :rst:dir:`imgur:fullsize` option. Current valid choices are ``s``, ``b``, ``t``, ``m``, ``l``, and ``h``.

.. option:: imgur_img_src_format

    *Default:* |LABEL_IMG_SRC_FORMAT|

    Image URL formatter used for the output. Valid substitutions are ``%(id)s``, ``%(size)s``, and ``%(ext)s``. This can be
    overridden in documents with the :rst:dir:`imgur:img_src_format` option.

.. option:: imgur_target_format

    *Default:* |LABEL_TARGET_FORMAT|

    URL formatter used for image links. Valid substitutions are ``%(id)s``, ``%(size)s``, and ``%(ext)s``. This can be
    disabled in documents with the :rst:dir:`imgur:notarget` option, and overridden with the built in image ``:target:``
    option.

.. option:: imgur_hide_post_details

    *Default:* |LABEL_HIDE_POST_DETAILS|

    Hide titles and descriptions in all album embeds when set to ``True``. Same as checking the **Hide Title** checkbox in
    the native Imgur `embed unit`_. This can be set in documents on a per embed basis with the
    :rst:dir:`imgur-embed:hide_post_details` option.

.. _embed unit: https://help.imgur.com/hc/en-us/articles/211273743-Embed-Unit
.. _sphinxext-opengraph: https://sphinxext-opengraph.readthedocs.io
