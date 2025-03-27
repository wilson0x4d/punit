# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Sequence

def areSame(a:Sequence[Any]|None, b:Sequence[Any]|None) -> bool:
    """
    Check if two sequences contain the same elements in the same order.
    
    Args:
        a: The sequence to check
        b: The sequence to compare against
        
    Returns:
        True if the sequences contain the same elements in the same order, False otherwise
    """
    if a is b:
        return True
    elif a is None and b is not None:
        return False
    elif a is not None and b is None:
        return False
    elif len(a) != len(b):        
        return False
    for i in range(len(a)):
        if not a[i] == b[i]:
            return False
    return True

def hasLength(sequence:Sequence[Any]|None, expected:int|None) -> bool:
    """
    Check if a sequence has the expected number of elements.
    
    Args:
        sequence: The sequence to check
        expected: The expected number of elements
        
    Returns:
        True if the sequence has exactly the expected number of elements, False otherwise
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

    Args:
        sequence: The sequence to check
        
    Returns:
        True if the sequence is None or empty, False otherwise
    """
    if sequence is None:
        return True
    return len(sequence) == 0
