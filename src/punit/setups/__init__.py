# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Setups provide a mechanism for performing initialization before test execution.

A ``@setup``-decorated function is executed immediately before each test runs,
allowing you to prepare resources or reset state without cluttering test bodies
with try/finally blocks.

Scopes
------

* **Module-scoped**;  a bare function decorated with ``@setup``; fires once per
  test across the entire module.
* **Class-scoped**;  a method inside a test class decorated with ``@setup``; fires
  once per test within that specific class only.

Example
-------

.. code-block:: python

    from punit import fact, setup

    @setup
    def db_setup():
        global _connection
        _connection = connect_to_database()

    @fact
    def test_query():
        assert query(_connection) is not None

"""

from .Setup import Setup, setup
from .SetupManager import SetupManager


__all__ = [
    'Setup', 'setup',
    'SetupManager'
]
