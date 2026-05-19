# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Callable, Optional, Sequence, cast


def areSame(actual: Sequence[Any] | set[Any] | dict[Any, Any] | None, expected: Sequence[Any] | set[Any] | dict[Any, Any] | None, sort: bool = False, sort_function: Optional[Callable[[Any], Any]] = None) -> bool:
    """
    Check if two sequences contain the same elements in the same order.
    
    :param actual: The sequence to check
    :param expected: The sequence to compare against
    :param sort: Sort sequences before performing comparisons.
    :param sort_function: Custom function to use when sorting.
    :returns bool: True if the sequences contain the same elements in the same order, False otherwise.
    """
    if actual is expected:
        return True
    elif actual is None and expected is not None:
        return False
    elif actual is not None and expected is None:
        return False
    elif actual is not None and expected is not None:
        if len(actual) != len(expected):
            return False

        if sort:
            if isinstance(actual, dict) or isinstance(expected, dict):
                sort_function = sort_function if sort_function is not None else lambda e: e[0]
                actual = sorted(cast(dict, actual).items(), key=sort_function)
                expected = sorted(cast(dict, expected).items(), key=sort_function)
            else:
                sort_function = sort_function if sort_function is not None else lambda e: e
                actual = sorted(actual, key=sort_function)
                expected = sorted(expected, key=sort_function)

        if isinstance(actual, dict) or isinstance(expected, dict):
            for pairs in zip(cast(dict, actual).items(), cast(dict, expected).items()):
                if not areSame(pairs[0], pairs[1]):
                    return False            
        else:
            for pairs in zip(actual, expected):
                if isinstance(pairs[0], dict) or isinstance(pairs[1], dict):
                    if not areSame(pairs[0], pairs[1]):
                        return False            
                elif pairs[0] != pairs[1]:
                        return False
    return True

def hasLength(actual: Sequence[Any] | set[Any] | dict[Any, Any] | None, expected: int | None) -> bool:
    """
    Check if actual value has the expected number of elements.
    
    :param actual: The actual value to check.
    :param int|None expected: The expected number of elements
        
    :returns bool: True if the sequence has exactly the expected number of elements, False otherwise
    """
    if actual is None and (expected is None or expected == 0):
        return True
    elif actual is None and (expected is not None and expected != 0):
        return False
    elif actual is not None and expected is None:
        return False
    return actual is not None and len(actual) == expected

def isNoneOrEmpty(actual: Sequence[Any] | set[Any] | dict[Any, Any] | None) -> bool:
    """
    Check if actual value is None or empty.

    :param actual: The actual to check.
    :returns: True if the value is None or empty, False otherwise.
    """
    if actual is None:
        return True
    return len(actual) == 0
