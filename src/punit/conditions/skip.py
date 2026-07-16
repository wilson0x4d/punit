# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Decorators for controlling test skip behavior.

Example
-------

.. code-block:: python

    from punit import fact, skip

    @fact
    @skip()
    def test_unconditionally_skipped():
        assert False  # never runs

    @fact
    @skip(lambda: os.name == 'posix')
    def test_conditional_skip():
        pass

"""

import inspect
from typing import Callable, Optional, TypeVar

T = TypeVar('T', bound=Callable[..., object])


def skip(when: Optional[bool] = None) -> Callable[[T], T]:
    """Decorator that marks a test for conditional or unconditional skip.

    Parameters
    ----------
    when : bool | Callable[..., bool] | None
        Controls skip behavior:

        - ``None`` (bare ``@skip`` or ``@skip()``) → test is unconditionally skipped
        - ``True`` → test is skipped
        - ``False`` → test runs normally (no-op)
        - ``Callable`` → invoke at test time; skip if it returns ``True``

    Returns
    -------
    T
        The original target with ``__punit_skip_condition`` set.

    Example
    -------

    .. code-block:: python

        from punit import skip

        @skip()
        def test_always_skipped():
            pass

        @skip(True)
        def test_skipped():
            pass

        @skip(False)
        def test_runs():
            pass

        @skip(lambda: os.name == 'posix')
        def test_conditional():
            pass

    """
    def decorator(target: T) -> T:
        unwrapped = inspect.unwrap(target)
        if not inspect.isfunction(unwrapped):
            raise Exception('@skip can only be applied to functions and methods.')

        # Determine the skip condition value.
        if when is None:
            # @skip() — unconditionally skip
            condition_value = True
        elif isinstance(when, bool):
            # @skip(True) or @skip(False)
            condition_value = when
        else:
            # At the decorator level, ``when`` is a callable.  We need to
            # distinguish between ``@skip(callable_arg)`` (user-provided skip
            # condition) and bare ``@skip(func)`` where ``when`` happens to be
            # the same object as ``target`` (the function being decorated).
            if target is when or inspect.unwrap(target) is when:
                # Bare ``@skip(func)``: the callable is the target itself,
                # not a condition function → unconditional skip.
                condition_value = True
            else:
                # ``@skip(callable_arg)``: genuine condition callable.
                condition_value = when

        setattr(unwrapped, '__punit_skip_condition', condition_value)
        return target

    # The dispatcher determines what to return based on ``when``.
    if when is None:
        # @skip() or @skip — unconditionally skip
        return decorator
    elif isinstance(when, bool):
        # @skip(True) or @skip(False)
        return decorator
    elif callable(when):
        if hasattr(when, '__punit_decorator'):
            # Bare ``@skip(func)`` stacked above another pUnit-decorated
            # function (the previous decorator has already marked it).
            # Set condition directly and return the function.
            unwrapped = inspect.unwrap(when)
            setattr(unwrapped, '__punit_skip_condition', True)
            return when  # type: ignore[return-value]
        # @skip(callable_arg) — user-provided condition callable
        return decorator
    else:
        return decorator
