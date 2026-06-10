# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Theories are tests that validate behavior across a variant arrangement of state.

State is usually acquired from an external source, separated from the test definition.
A Theory requires at least one data decorator (such as ``@inlinedata``) in addition
to the ``@theory`` decorator for execution.

Example
-------

.. code-block:: python

    from punit import theory, inlinedata

    @theory
    @inlinedata(0, 1, 1)
    @inlinedata(1, 1, 2)
    @inlinedata(1, 2, 3)
    def test_addition(a, b, c):
        assert a + b == c

"""

from .Theory import Theory, theory, inlinedata
from .TheoryManager import TheoryManager


__all__ = [
    'Theory', 'theory', 'inlinedata',
    'TheoryManager'
]
