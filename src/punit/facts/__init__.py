# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Facts are tests that validate an invariant arrangement of state.

State is usually hardcoded as part of the test definition itself. Unlike Theories,
Facts do not require data providers; each decorated function runs exactly once.

Example
-------

.. code-block:: python

    from punit import fact

    @fact
    def test_equality():
        assert 1 == 1

    class MyTestClass:
        @fact
        def test_method(self):
            assert True

"""

from .Fact import Fact, fact
from .FactManager import FactManager


__all__ = [
    'Fact', 'fact',
    'FactManager'
]
