# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any

def areSame(a:str|None, b:str|None) -> bool:
    """
    Check if two strings contain the same characters in the same order.

    Args:
        a: The first string
        b: The second string
        
    Returns:
        True if the strings contain the same characters in the same order, False otherwise
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
        if a[i] != b[i]:
            return False
    return True

def isNoneOrEmpty(string:str|None) -> bool:
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

def isNoneOrWhitespace(string:str|None) -> bool:
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
