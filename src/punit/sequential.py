# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
``@sequential`` decorator for pUnit.

When running tests with ``--parallel``, any test decorated with
``@sequential`` is deferred to a sequential pass that runs after all
parallel peers at the same scope have finished.
"""

from __future__ import annotations

from typing import Any, Callable


def sequential(target: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a test function or method for **sequential** (sequential) execution.

    When pUnit is started with ``--parralel THREADS`` (where *THREADS* > 1),
    tests decorated without ``@sequential`` run in parallel up to *N* at
    any given point.  ``@sequential`` tests are **not** added to the
    concurrent dispatch queue -- after all peers at the same scope finish
    concurrently, the sequential tests run one after another in their
    definition order.

    The decorator returns the original ``target`` unchanged; it installs the
    ``__punit_sequential`` marker attribute on the unwrapped function.

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

        from punit import fact, sequential

        @fact
        @sequential
        def my_test():
            assert True

        class MyTestCase:
            @fact
            @sequential
            def test_one(self):
                assert True

    """
    import inspect

    unwrapped = inspect.unwrap(target)
    setattr(unwrapped, "__punit_sequential", True)
    return target
