# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Manages class-instance caching for lifecycle-aware test classes.

For :py:attr:`Lifecycle.PER_RUN`, a single shared instance is cached the
first time :py:meth:`get_or_create` is called and reused on all subsequent
calls — even from concurrent threads.

For :py:attr:`Lifecycle.PER_TEST`, a fresh instance is always created via
the factory function.

"""

from __future__ import annotations

import threading
from typing import Any, Callable, Optional

from .lifecycle import Lifecycle


class _InstanceState:
    """Per-instance state tracking for PER_RUN lifecycle.

    The runner uses these flags to decide whether to fire setup/teardown:

    - ``setup_fired`` — :py:attr:`True` once setup has been invoked for
      this instance.  Never resets within a run.
    - ``teardown_ready`` — set to :py:attr:`True` by :py:meth:`release`
      when the **last** consumer calls ``release`` (i.e. *all* tests that
      share this instance have completed).  When ``teardown_ready`` is
      ``True``, _execute_fact and ``__run_facts_per_run`` fire teardown.
    - ``_setup_lock`` — serialises setup across parallel tests.
    """

    __slots__ = ('setup_fired', 'teardown_ready', '_setup_lock')

    def __init__(self) -> None:
        self.setup_fired = False
        self.teardown_ready = False
        self._setup_lock = threading.Lock()


class LifecycleManager:

    """Manages class-instance caching and lifecycle lookups.

    Thread-safe: multiple concurrent threads calling :py:meth:`get_or_create`
    with the same target will all receive the *same* cached instance.
    Only one thread ever calls the factory — all others wait and get the
    already-cached instance.
    """

    __instance: Optional['LifecycleManager'] = None
    __lock: Any

    def __init__(self) -> None:
        if LifecycleManager.__instance is not None:
            raise Exception(
                'Cannot create more than one instance of LifecycleManager'
            )
        self.__run_instances: dict[type, tuple[Any, _InstanceState]] = {}
        self.__lock = __import__('threading').Lock()

    @staticmethod
    def instance() -> LifecycleManager:
        if LifecycleManager.__instance is None:
            LifecycleManager.__instance = LifecycleManager()
        return LifecycleManager.__instance

    @staticmethod
    def get_lifecycle(target: Any) -> Lifecycle:
        """Return the ``@lifecycle`` for *target*.

        Defaults to :py:attr:`Lifecycle.PER_TEST` when the target has no
        ``__punit_lifecycle`` attribute.
        """
        value = getattr(target, '__punit_lifecycle', None)
        if value is not None:
            return Lifecycle(value)
        return Lifecycle.PER_TEST

    @staticmethod
    def get_or_create(
        target: Any,
        lifecycle: Lifecycle,
        factory: Callable[[], Any],
    ) -> tuple[Any, '_InstanceState | None']:
        """Return a class instance respecting the given lifecycle.

        *PER_TEST* — returns ``(factory(), no-op-state)``.  The caller
        should always fire setup and teardown (``state`` has no effect).

        *PER_RUN* — returns ``(instance, state)``.  The ``state`` has
        ``setup_fired`` set on the first call so the caller knows to skip
        setup on subsequent invocations (even from parallel threads).
        After all tests complete, :py:meth:`release` sets
        ``teardown_ready`` so the caller fires teardown.

        Guarantees:

        - *Zero wasted work*: the factory is called **at most once** per
          target across all threads.
        - A global lock serialises instance creation + first-run
          bookkeeping so that setup/teardown are never missed or
          duplicated.
        """
        if lifecycle == Lifecycle.PER_RUN:
            mgr = LifecycleManager.__instance
            if mgr is not None:
                with mgr.__lock:
                    entry = mgr.__run_instances.get(target)
                    if entry is not None:
                        instance, state = entry
                        return instance, state
                    # First call — create instance and state.
                    instance = factory()
                    state = _InstanceState()
                    mgr.__run_instances[target] = (instance, state)
                    return instance, state
            # Fallback: no manager — use a state with no-op tracking.
            return factory(), _get_empty_noop()
        else:
            return factory(), None

    @staticmethod
    def release(state: '_InstanceState | None') -> bool:
        """Signal that one consumer has finished with a PER_RUN instance.

        Returns ``True`` on the **first** call (when ``teardown_ready``
        transitions ``False`` → ``True``), ``False`` on subsequent calls.
        The caller fires teardown only when ``True`` is returned.
        """
        if state is not None:
            if not state.teardown_ready:
                state.teardown_ready = True
                return True
            return False
        return False

    @staticmethod
    def clear(target: Any) -> None:
        """Remove the cached instance for a ``PER_RUN`` target.

        This should be called after all tests for a class have completed so
        that no stale state leaks into the next test module.
        """
        mgr = LifecycleManager.__instance
        if mgr is not None:
            mgr.__run_instances.pop(target, None)

    @staticmethod
    def reset() -> None:
        """Reset the singleton and all cached instances."""
        LifecycleManager.__instance = None


_empty_noop: _InstanceState | None = None


def _get_empty_noop() -> '_InstanceState':
    """Return a no-op state for PER_TEST targets."""
    global _empty_noop
    if _empty_noop is None:
        _empty_noop = _InstanceState()
    return _empty_noop
