"""Helpers."""


def is_true(argument):
    """Return True if argument is the word "true" case insensitive.

    :param str argument: Argument/value passed to directive's option.

    :return: Is argument true/True/TRUE.
    :rtype: bool
    """
    return argument.lower() == "true"
