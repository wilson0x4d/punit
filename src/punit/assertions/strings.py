# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Optional


def are_same(a: str | None, b: str | None) -> bool:
    """
    Check if two strings contain the same characters in the same order.

    Args:
        a: The first string
        b: The second string

    Returns:
        True if the strings contain the same characters in the same order, False otherwise
    """
    if a is None and b is not None:
        return False
    elif a is not None and b is None:
        return False
    elif a is not None and b is not None:
        if len(a) != len(b):
            return False
        for i in range(len(a)):
            if a[i] != b[i]:
                return False
    return True


def has_length(actual: str | None, min: Optional[int] = None, max: Optional[int] = None) -> bool:
    """
    Check if actual value has the expected number of elements.

    :param actual: The actual value to check.
    :param int|None expected: The expected number of elements

    :returns bool: True if the sequence has exactly the expected number of elements, False otherwise
    """
    if actual is None:
        if ((min is None or min == 0) and (max is None or max == 0)):
            return True
        return not ((min is not None and min != 0) or (max is not None or max != 0))
    else:
        if ((min is None) and (max is None)):
            return False
        len_actual = len(actual)
        return (min is None or len_actual >= min) and (max is None or len_actual <= max)


def is_none_or_empty(string: str | None) -> bool:
    """
    Check if a string is None or empty.

    Args:
        string: The string to check

    Returns:
        True if the string is None or empty, False otherwise
    """
    if string is None:
        return True
    return len(string) == 0


def is_none_or_whitespace(string: str | None) -> bool:
    """
    Check if a string is None or whitespace.

    Args:
        string: The string to check

    Returns:
        True if the string is None or whitespace, False otherwise
    """
    if string is None:
        return True
    return len(string.strip()) == 0


# DEPRECATIONS
areSame = are_same
hasLength = has_length
isNoneOrEmpty = is_none_or_empty
isNoneOrWhitespace = is_none_or_whitespace


__all__ = [
    'are_same',
    'has_length',
    'is_none_or_empty',
    'is_none_or_whitespace',
    # deprecated (do not use):
    'areSame',
    'hasLength',
    'isNoneOrEmpty',
    'isNoneOrWhitespace'
]
