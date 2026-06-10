# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Teardowns provide a mechanism for performing cleanup after test execution.

A ``@teardown``-decorated function is executed immediately after each test runs,
allowing you to release resources or reset state without cluttering test bodies
with try/finally blocks.

Scopes
------

* **Module-scoped**;  a bare function decorated with ``@teardown``; fires once per
  test across the entire module.
* **Class-scoped**;  a method inside a test class decorated with ``@teardown``; fires
  once per test within that specific class only.

Example
-------

.. code-block:: python

    from punit import fact, teardown

    @teardown
    def my_teardown():
        cleanup_database()

    @fact
    def test_something():
        assert True

"""

from .Teardown import Teardown, teardown
from .TeardownManager import TeardownManager


__all__ = [
    'Teardown', 'teardown',
    'TeardownManager'
]
