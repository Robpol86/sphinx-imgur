"""Helpers."""
from typing import Any, Dict, Optional, Tuple


def imgur_id_size_ext(arg: str, options: Dict[str, Any], config: Dict[str, Any]) -> Tuple[str, str, str]:
    """Determine the image ID, size, and file extension.

    :param arg: First argument given to directive.
    :param options: Directive options.
    :param config: Sphinx config.
    """
    # Extension.
    if "." in arg:
        imgur_id, ext = arg.rsplit(".", 1)
        if not ext:
            ext = config["imgur_default_ext"]
    else:
        imgur_id = arg
        ext = config["imgur_default_ext"]
    if "ext" in options:
        ext = options["ext"]

    # Size.
    if len(imgur_id) % 2 == 0:  # If even (user specified size).
        # As far as I know imgur IDs are odd. If it's even then size was specified by the user.
        size = imgur_id[-1]
        imgur_id = imgur_id[:-1]
    elif "." in arg:
        # User specified extension in the argument, interpreting it as requesting full size (e.g. a gif).
        size = ""
    else:
        size = config["imgur_default_size"]
    if "fullsize" in options:
        size = ""
    elif "size" in options:
        size = options["size"]

    return imgur_id, size, ext


def img_src_target_formats(options: Dict[str, Any], config: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    """Determine image URL and link target formatting.

    When target formatting is None this indicates user does not want image to be linked.

    :param options: Directive options.
    :param config: Sphinx config.
    """
    # img src
    if "img_src_format" in options:
        img_src_format = options["img_src_format"]
    else:
        img_src_format = config["imgur_img_src_format"]

    # target
    if "target" in options:
        target_format = options["target"]
    elif "notarget" not in options:
        target_format = config["imgur_target_format"]
    else:
        target_format = None

    return img_src_format, target_format
