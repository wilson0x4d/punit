# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
``@synchronous`` decorator for pUnit.

When running tests with ``--concurrent-mode``, any test decorated with
``@synchronous`` is deferred to a sequential pass that runs after all
concurrent peers at the same scope have finished.
"""

from __future__ import annotations

from typing import Callable


def synchronous(target: Callable) -> Callable:
    """Mark a test function or method for **synchronous** (sequential) execution.

    When pUnit is started with ``--concurrent-mode N`` (where *N* > 1),
    tests decorated without ``@synchronous`` run in parallel up to *N* at
    any given point.  ``@synchronous`` tests are **not** added to the
    concurrent dispatch queue -- after all peers at the same scope finish
    concurrently, the synchronous tests run one after another in their
    definition order.

    The decorator returns the original ``target`` unchanged; it installs the
    ``__punit_synchronous`` marker attribute on the unwrapped function.

    Parameters
    ----------
    target : Callable
        The test function or method to mark.

    Returns
    -------
    Callable
        The original, undecorated target.

    Example
    -------

    .. code-block:: python

        from punit import fact, synchronous

        @fact
        @synchronous
        def my_test():
            assert True

        class MyTestCase:
            @fact
            @synchronous
            def test_one(self):
                assert True

    """
    import inspect

    unwrapped = inspect.unwrap(target)
    setattr(unwrapped, "__punit_synchronous", True)
    return target
