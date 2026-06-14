# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Patch mechanism for replacing module-level attributes with :class:`Mock` objects.

Provides both a **decorator** and **context manager** via the same :class:`patch` class,
with full async support. The patch atomically replaces an attribute on a module and
restores the original value when the patch is exited or the decorated function returns.

Usage::

    from punit.mocks import patch, Mock

    # Context manager
    with patch('myapp.database.connect') as m:
        m.returns('connected')

    # Decorator (sync)
    @patch('myapp.database.connect')
    def test_something(m):
        assert m.called

    # Decorator (async)
    @patch('myapp.database.connect')
    async def test_async(m):
        assert m.origin is not None

The patch instance itself is the Mock -- ``with patch(...) as m:`` yields a :class:`Mock`.
"""

from __future__ import annotations

import inspect
import sys
from typing import (
    Any,
    Callable,
    Optional,
    TypeVar,
)

from .mock import Mock

T = TypeVar('T', bound=Callable[..., Any])


class patch:
    """
    Patch a module-level attribute with a :class:`Mock`.

    Can be used as both a context manager and a decorator. The same instance
    handles both via ``__enter__/__exit__`` and ``__call__``.

    Usage::

        # As context manager:
        with patch('myapp.db.connect') as mock_connect:
            mock_connect.returns('connected')

        # As decorator:
        @patch('myapp.db.connect')
        def test_something(m):
            assert m.called
    """

    def __init__(
        self,
        target_path: str,
        origin: Optional[type] = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a new patch for the given dotted path.

        :param target_path: Dotted attribute path to replace (e.g. ``'myapp.database.connect'``).
        :param origin: Optional type for Mock virtual-subclass registration.
        :param kwargs: Additional keyword arguments forwarded to the Mock constructor.
        """
        self._module, self._attr_name = self.__resolve_path(target_path)
        self._original = getattr(self._module, self._attr_name)
        self._kwargs = {**kwargs}
        if origin is not None:
            self._kwargs['origin'] = origin
        self._mock = Mock(**self._kwargs)

    def __enter__(self) -> Mock:
        """Replace the module attribute with the Mock and return it."""
        setattr(self._module, self._attr_name, self._mock)
        return self._mock

    def __exit__(
        self,
        _exc_type: Any,
        _exc_val: Any,
        _exc_tb: Any,
    ) -> None:
        """
        Restore the original value after the patch."""
        setattr(self._module, self._attr_name, self._original)

    def __call__(self, func: T) -> T:
        """
        Decorate *func* so each invocation is wrapped in a patch/unpatch cycle.

        Detects async functions and wraps them in an ``async_wrapper`` that
        ensures the mock lives only for the duration of the test call.
        """
        if inspect.iscoroutinefunction(func):

            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                mock_instance = self.__enter__()  # type: ignore[assignment]
                try:
                    return await func(mock_instance, *args, **kwargs)
                finally:
                    self.__exit__(None, None, None)

            async_wrapper.__name__ = func.__name__
            async_wrapper.__doc__ = func.__doc__
            async_wrapper.__wrapped__ = func  # type: ignore[attr-defined]
            return async_wrapper  # type: ignore[return-value]
        else:

            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                mock_instance = self.__enter__()  # type: ignore[assignment]
                try:
                    return func(mock_instance, *args, **kwargs)
                finally:
                    self.__exit__(None, None, None)

            sync_wrapper.__name__ = func.__name__
            sync_wrapper.__doc__ = func.__doc__
            sync_wrapper.__wrapped__ = func  # type: ignore[attr-defined]
            return sync_wrapper  # type: ignore[return-value]

    def __resolve_path(self, target_path: str) -> tuple[Any, str]:
        """
        Resolve a dotted path (e.g. ``'myapp.database.connect'``) to ``(parent, attr_name)``.

        The parent can be a module, class, or any object -- it is the container that holds
        the target attribute as an attribute name. For paths like
        ``'tests.mocks.fake.TestFake.apply'``, the parent is the ``TestFake`` class and
        ``attr_name`` is ``'apply'``.

        :param target_path: Dotted attribute path.
        :returns: A tuple of the resolved parent object and the last segment as *attr_name*.
        :raises AttributeError: If the module or attribute does not exist.
        """
        parts = target_path.split('.')
        module_path_parts: list[str] = []

        # Walk through parts, trying to import each as a submodule.
        # Track the deepest successfully imported prefix and its sys.modules reference.
        for i in range(len(parts)):
            current_module_path = '.'.join(parts[:i + 1])
            try:
                __import__(current_module_path)
            except (ModuleNotFoundError, ImportError):
                break
            module_path_parts = parts[:i + 1]

        if not module_path_parts:
            raise AttributeError(
                f'Cannot find module containing attribute "{target_path}"'
            )

        attr_name = parts[-1]
        resolved_module = sys.modules['.'.join(module_path_parts)]

        # Walk through remaining parts (between the import boundary and the target)
        # via getattr to reach the actual parent.
        obj: Any = resolved_module
        intermediates = parts[len(module_path_parts):-1]
        if len(intermediates) > 0:
            for remaining_part in intermediates:
                obj = getattr(obj, remaining_part)
            return (obj, attr_name)

        # All prefix segments were importable as modules, but none remain to walk.
        # When namespace packages are involved, an intermediate path segment (e.g. the
        # class ``TestFake`` in ``'tests.mocks.fake.TestFake.apply'``) is itself both a
        # submodule and a non-module object inside its parent package. Walk backwards
        # from each consumed module, looking for a non-module item that has the target.
        if len(parts) < 2:
            raise AttributeError(
                f'Cannot find module containing attribute "{target_path}"'
            )

        import types as _types

        for i in range(len(module_path_parts) - 1, 0, -1):
            parent_pkg = sys.modules['.'.join(module_path_parts[:i])]
            candidate_name = module_path_parts[i]
            # First check the part's own namespace (it may be a class/function name).
            try:
                candidate = getattr(parent_pkg, candidate_name)
            except AttributeError:
                continue  # only registered in sys.modules, not an attr on parent
            if isinstance(candidate, _types.ModuleType):
                # It is a real submodule -- also check the module's __dict__ for
                # an item sharing the same name (namespace package edge case).
                mod_dict = getattr(sys.modules['.'.join(module_path_parts[:i + 1])], '__dict__', {})
                inner_candidate = mod_dict.get(candidate_name) if candidate_name else None
                if inner_candidate is not None and isinstance(inner_candidate, type):
                    if hasattr(inner_candidate, attr_name):
                        return (inner_candidate, attr_name)
                continue
            if hasattr(candidate, attr_name):
                return (candidate, attr_name)

        # No non-module intermediary found -- use the deepest consumed module as parent.
        # This handles cases where the target lives at module level (no class/function bridge).
        return (resolved_module, attr_name)


__all__ = ['patch']
