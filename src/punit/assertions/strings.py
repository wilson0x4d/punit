# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

"""String assertion helpers for comparison and checks.

Provides utilities for comparing string equality, checking length bounds,
and testing for None/empty/whitespace values.

Example
-------

.. code-block:: python

    from punit import strings

    assert strings.are_same('hello', 'hello')
    assert not strings.are_same('hello', 'world')
    assert strings.is_none_or_empty(None)
    assert strings.has_length('hello', min=3, max=10)

"""

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
    Check if actual value's length falls within the inclusive range [min, max].

    Args:
        actual: The string to check.
        min: Inclusive lower bound on length (``len(actual) >= min``).
        max: Inclusive upper bound on length (``len(actual) <= max``).

    Returns:
        True if the length satisfies the bounds, False otherwise.
        When actual is None, returns True only when both bounds are effectively zero.

    Example
    -------

    .. code-block:: python

        from punit import strings

        a = 'hello'

        assert strings.has_length(a, min=5)
        assert strings.has_length(a, max=5)
        assert strings.has_length(a, min=3, max=7)
        assert not strings.has_length(a, min=6)
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
        string: The string to check.

    Returns:
        True if the string is None or whitespace, False otherwise.

    Example
    -------

    .. code-block:: python

        from punit import strings

        assert not strings.is_none_or_whitespace('hello')
        assert strings.is_none_or_whitespace(' \t')
        assert strings.is_none_or_whitespace(None)
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
