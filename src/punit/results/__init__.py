# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Decorators for controlling test results.

Example
-------

.. code-block:: python

    from punit import fact, fails

    @fact
    @fails(reason='bug #123')
    def test_known_issue():
        assert False  # expected to fail

"""

from .fails import fails

__all__ = ['fails']
