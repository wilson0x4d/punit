# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Lifecycle control for test classes.

The ``@lifecycle`` decorator specifies how class instances are managed across
test method executions within a test class.

Available lifecycles
--------------------

- **``PER_TEST``** (default) — A fresh class instance is created for each
  test method execution. ``@setup`` and ``@teardown`` run before and after
  each individual test, bound to that same instance.

- **``PER_RUN``** — A single class instance is created once and reused for
  all test methods in the class. ``@setup`` fires before the first test and
  ``@teardown`` fires after the last test, both on the same shared instance.

Example
-------

.. code-block:: python

    from punit import fact, lifecycle, Lifecycle

    @lifecycle(Lifecycle.PER_RUN)
    class SharedStateTests:
        counter = 0

        @fact
        def test_first(self):
            SharedStateTests.counter += 1
            assert SharedStateTests.counter == 1

        @fact
        def test_second(self):
            assert SharedStateTests.counter == 2

    @lifecycle(Lifecycle.PER_TEST)
    class IsolatedTests:
        @fact
        def test_a(self):
            ...  # gets a fresh instance

        @fact
        def test_b(self):
            ...  # gets another fresh instance

"""

import enum
from typing import Any


class Lifecycle(enum.StrEnum):
    """Controls class instance management for test classes."""

    PER_TEST = 'per_test'
    PER_RUN = 'per_run'


def lifecycle(lifecycle: Lifecycle = Lifecycle.PER_TEST):
    """Configure how test class instances are managed.

    This decorator may only be applied to a class. When applied to a function,
    method, or any other non-class target, the decorator is a no-op and has
    no effect (undefined behavior if misused).

    When used as ``@lifecycle`` (without parentheses), the default
    ``PER_TEST`` lifecycle is applied. When used as
    ``@lifecycle(Lifecycle.PER_RUN)``, the specified lifecycle is applied.

    Parameters
    ----------
    lifecycle : Lifecycle
        The lifecycle to apply. Defaults to ``PER_TEST``.

    Returns
    -------
    Callable
        If *target* is a class, returns the class with
        ``__punit_lifecycle`` attribute set. Otherwise returns *target*
        unchanged.

    """

    def decorator(target: Any):
        if isinstance(target, type):
            setattr(target, "__punit_lifecycle", lifecycle)
        return target

    # Handle bare @lifecycle (no parentheses): target is the class itself.
    if isinstance(lifecycle, type):
        return decorator(lifecycle)

    return decorator


def get_lifecycle(target: Any) -> Lifecycle:
    """Return the lifecycle for a class, defaulting to ``PER_TEST``."""
    return getattr(target, '__punit_lifecycle', Lifecycle.PER_TEST)
