# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Callable, Sequence


def areSame(a:Sequence[Any]|None, b:Sequence[Any]|None, sort:bool=False, sortFunction:Callable[[Any], Any]=None) -> bool:
    """
    Check if two sequences contain the same elements in the same order.
    
    :param Sequence[Any]|None a: The sequence to check
    :param Sequence[Any]|None b: The sequence to compare against
    :param Optional[bool] sort: Sort sequences before performing comparisons.
    :param Optional[Callable[[Any], Any]] sortFunction: Custom function to use when sorting.
    :returns bool: True if the sequences contain the same elements in the same order, False otherwise.
    """
    if a is b:
        return True
    elif a is None and b is not None:
        return False
    elif a is not None and b is None:
        return False
    elif len(a) != len(b):
        return False

    if sort:
        if isinstance(a, dict) or isinstance(b, dict):
            sortFunction = sortFunction if sortFunction is not None else lambda e: e[0]
            a = sorted(a.items(), key=sortFunction)
            b = sorted(b.items(), key=sortFunction)
        else:
            sortFunction = sortFunction if sortFunction is not None else lambda e: e
            a = sorted(a, key=sortFunction)
            b = sorted(b, key=sortFunction)

    if isinstance(a, dict) or isinstance(b, dict):
        for pairs in zip(a.items(), b.items()):
            if not areSame(pairs[0], pairs[1]):
                return False            
    else:
        for pairs in zip(a, b):
            if isinstance(pairs[0], dict) or isinstance(pairs[1], dict):
                if not areSame(pairs[0], pairs[1]):
                    return False            
            elif pairs[0] != pairs[1]:
                    return False
    return True

def hasLength(sequence:Sequence[Any]|None, expected:int|None) -> bool:
    """
    Check if a sequence has the expected number of elements.
    
    :param Sequence[Any]|None sequence: The sequence to check
    :param int|None expected: The expected number of elements
        
    :returns bool: True if the sequence has exactly the expected number of elements, False otherwise
    """
    if sequence is None and (expected is None or expected == 0):
        return True
    elif sequence is None and (expected is not None and expected != 0):
        return False
    elif sequence is not None and expected is None:
        return False
    return len(sequence) == expected

def isNoneOrEmpty(sequence:Sequence[Any]|None) -> bool:
    """
    Check if a sequence is None or empty.

    :param Sequence[Any]|None sequence: The sequence to check
    :returns bool: True if the sequence is None or empty, False otherwise
    """
    if sequence is None:
        return True
    return len(sequence) == 0
