# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Assertion helpers for pUnit tests.

With pUnit, assertions are typically performed using Python's ``assert`` statement.
This module provides several helper submodules that offer additional assertion
capabilities beyond the built-in ``assert`` keyword.

Sub-modules
-----------

* :py:mod:`punit.assertions.collections`; helpers for comparing sequences and collections.
* :py:mod:`punit.assertions.exceptions`; helpers for asserting raised exceptions.
* :py:mod:`punit.assertions.numeric`; helpers for approximate numeric comparisons.
* :py:mod:`punit.assertions.strings`; helpers for string comparisons and checks.

"""

from . import collections, exceptions, numeric, strings


__all__ = [
    'collections',
    'exceptions',
    'numeric',
    'strings'
]
