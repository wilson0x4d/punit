# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Core Mock class and Call dataclass.

Provides :class:`Mock` — a lightweight, single-class mocking framework that supports:
- **``isinstance`` conformance** via virtual-subclass registration.
- **Delegate forwarding** for partial doubles / spies
- **Fluent configuration** with call tracking and matcher-based assertions
- **Iteration support** via ``__iter__``/``__len__`` -- ``for x in mock.child`` yields
  from ``mock.child.returns([...])`` data; ``len(mock.child)`` reports item count.
- Context manager yielding independent child mocks (auto-reset on exit)

Usage::

    from punit.mocks import Mock, is_any, is_gt

    # Create a mock with origin conformance
    userservice = Mock(origin=UserService)
    userservice.is_authenticated.returns(False)
    userservice.get_user.returns('Guest')

    assert userservice.called_with(is_gt(0))

    # Constructor kwargs for fixture-style initialization
    row = Mock(migration='alpha', id=1)
    assert row.migration == 'alpha'
    assert row.id == 1
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Union,
)

from .matcher import Matcher


class MockError(Exception):
    """Exception raised when mock configuration is violated."""


@dataclass(frozen=True, init=False)
class Call:
    """
    Immutable record of a single mock call.

    Call records carry the full metadata set (timestamp, took, is_async, result, error) so that ``.calls`` and ``.mock_calls`` return semantically identical data.

    :ivar path: Absolute dotted path name (e.g. ``'Mock.foo.bar'``).
    :ivar timestamp: Time when the call occurred (``time.monotonic_ns()``).
    :ivar took: Time spent in the call, in seconds.
    :ivar is_async: Whether the call was made via ``await``.
    :ivar args: Positional arguments passed to the mock.
    :ivar kwargs: Keyword arguments passed to the mock.
    :ivar result: Return value from the call (``None`` if no return value).
    :ivar error: Exception raised by the call (``None`` if none).

    Examples::

        >>> Call('Mock.foo', (1,), {'key': 'val'})
        >>> Call(path='Mock.foo', timestamp=42.0, took=0.001, is_async=False, args=(1,), kwargs={'key': 'val'}, result='r', error=None)
    """

    path: str = ''
    timestamp: float = 0.0
    took: float = 0.0
    is_async: bool = False
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: BaseException | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Call:  # type: ignore[misc]
        _u = object.__new__(cls)

        if len(args) == 3 and isinstance(args[0], str):
            # detect if we get exactly 3 positional args, or if kwargs contains
            # both 'args' and 'kwargs' keys alongside a path-like value, ie:
            # `Call('Mock.foo', (1,), {})`
            object.__setattr__(_u, 'path', args[0])
            object.__setattr__(_u, 'timestamp', 0.0)
            object.__setattr__(_u, 'took', 0.0)
            object.__setattr__(_u, 'is_async', False)
            object.__setattr__(_u, 'args', args[1] if isinstance(args[1], tuple) else ())
            object.__setattr__(_u, 'kwargs', args[2] if isinstance(args[2], dict) else {})
            object.__setattr__(_u, 'result', None)
            object.__setattr__(_u, 'error', None)
        else:
            # "full" keyword form: explicit path='...' or positional path + keyword extras:
            _kw: dict[str, Any] = {
                'path': '',
                'timestamp': 0.0,
                'took': 0.0,
                'is_async': False,
                'args': (),
                'kwargs': {},
                'result': None,
                'error': None,
            }
            if len(args) == 1 and isinstance(args[0], str):
                _kw['path'] = args[0]
            elif args:
                # Handle any other positional edge cases via keywords
                pass
            _kw.update(kwargs)
            for _field in ('path', 'timestamp', 'took', 'is_async', 'args', 'kwargs', 'result', 'error'):
                object.__setattr__(_u, _field, _kw[_field])

        return _u

    def __repr__(self) -> str:  # type: ignore[override]
        if not self.kwargs and not self.path:
            return repr(self.args)
        args_repr = ', '.join(repr(a) for a in self.args)
        kwargs_items = [f'{k}={v!r}' for k, v in self.kwargs.items()]
        if args_repr and kwargs_items:
            sep = (f'({args_repr}), '
                   f'{", ".join(kwargs_items)}')
        elif args_repr:
            sep = f'({args_repr})'
        elif kwargs_items:
            sep = ', '.join(kwargs_items)
        else:
            sep = ''
        return f'{self.path}({sep})' if self.path else f'({sep})'

    def __eq__(self, other: Any) -> bool:  # type: ignore[override]
        return (
            self.path == other.path
            and self.args == other.args
            and self.kwargs == other.kwargs
        ) if isinstance(other, Call) else NotImplemented

    def __hash__(self) -> int:  # type: ignore[override]
        return hash((self.path, self.args, self.kwargs))


class CallList(tuple):  # type: ignore[type-arg]
    """Tuple of :class:`Call` supporting partial-sublist matching via ``__contains__``."""

    def __contains__(self, item: object) -> bool:  # type: ignore[override]
        if isinstance(item, CallList):
            target = list(item)
            if not target:
                return True
            for i in range(len(self) - len(target) + 1):
                if all(CallList.__matches(self[i + j], target[j]) for j in range(len(target))):
                    return True
            return False
        return super().__contains__(item)

    @staticmethod
    def __matches(call: Call, other: Call) -> bool:
        return call.path == other.path and call.args == other.args and call.kwargs == other.kwargs


class Mock:
    """
    Lightweight mock object for dependency injection testing.

    Every :class:`Mock` instance can register itself as a virtual subclass of any type
    (ABC, ``@runtime_checkable`` Protocol, or concrete class) via the *origin* parameter
    -- making ``isinstance(mock, origin)`` return ``True``.

    Usage::

        from punit.mocks import Mock

        # Create a mock that conforms to UserService structurally
        mock = Mock(origin=UserService)
        mock.is_authenticated.returns(False)
        mock.get_user.returns('Guest')

        assert mock.called_with(42)

    Child mocks (returned by attribute access) are cached -- ``mock.foo is mock.foo``.
    """

    class _Untouchables:
        """Per-instance holder for Mock's internal framework state."""

        __slots__ = (
            'origin',
            'delegate',
            'name',
            'path',
            'parent',
            'children',
            'configured',
            'call_records',
            'child_call_records',
            'has_return_value',
            'has_side_effect',
            'side_effect_iter',
            'delegate_method',
            'when_conditions',
        )

        children: dict[str, Mock]
        configured: dict[str, Any]
        call_records: list[Call]
        child_call_records: list[Call]
        delegate: Any
        delegate_method: Any
        has_return_value: bool
        has_side_effect: bool
        name: str
        origin: Optional[type]
        path: str
        parent: Optional[Mock]
        side_effect_iter: Any
        when_conditions: list[tuple[tuple[Matcher, ...], dict[str, Matcher], Mock]]

        def __init__(self) -> None:
            self.origin = None
            self.delegate = None
            self.name = 'Mock'
            self.path = 'Mock'
            self.parent = None
            self.children = {}
            self.configured = {}
            self.call_records = []
            self.child_call_records = []
            self.has_return_value = False
            self.has_side_effect = False
            self.side_effect_iter = None
            self.delegate_method = None
            self.when_conditions = []

    @classmethod
    def register_origin(cls, origin: type) -> None:
        """Register *origin* so that Mock instances pass ``isinstance(_, origin)``.

        Dispatches to the origin's ``register`` method (for ABCs and
        runtime_checkable Protocols).

        :param origin: The type this mock stands in for.
        """
        if hasattr(origin, 'register') and callable(getattr(origin, 'register')):
            origin.register(cls)  # type: ignore[union-attr]

    def __init__(
        self,
        origin: Optional[type] = None,
        *,
        delegate: Any = None,
        name: str = 'Mock',
        _validate: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Create a new Mock instance.

        :param origin: The type this mock stands in for (enables isinstance checks).
        :param delegate: A real object whose methods are forwarded when not configured.
        :param name: Debug identifier for the mock. Defaults to ``'Mock'``.
        :param validate: If True, validate call arguments against inspectable signatures.
        :param kwargs: Arbitrary keyword arguments set as initial attribute values.
            Each key becomes an accessible attribute that returns the given value.
            The special key ``side_effect`` is applied to this mock's calling behavior.
        """
        # Allocate internal state in a dedicated container (keeps it insulated
        # from user-set kwargs which become accessible Mock attributes).
        self._u = Mock._Untouchables()
        self._u.name = name
        self._u.path = name

        if origin is not None:
            self.register_origin(origin)
            self._u.origin = origin
            self.__populate_members(origin)

        if delegate is not None:
            self._u.delegate = delegate

        # additional kwargs get initialized as attrs
        for key, value in kwargs.items():
            if key.startswith('_'):
                continue  # avoid corruption of state
            if key == 'side_effect':
                # mutate call semantics (applies to 'this' mock)
                self._u.configured['__side_effect__'] = value
                self._u.has_side_effect = True
                self._u.has_return_value = False
            else:
                self._u.configured[key] = value

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Record the call and evaluate configured behavior."""
        # Conditional dispatch (highest priority) — forward matching calls to subgraph.
        subgraph = self.__resolve_conditional(args, kwargs)
        if subgraph is not None:
            return subgraph(*args, **kwargs)  # delegate call through matched subgraph

        # Track timing and async context
        start = time.monotonic_ns()
        try:
            is_async = asyncio.current_task() is not None
        except RuntimeError:
            is_async = False

        # Evaluate side_effect priority: iterable → exception → callable → return_value → self
        result: Any = self
        error: BaseException | None = None

        has_side_effect = self._u.has_side_effect
        has_return_value = self._u.has_return_value

        try:
            if has_side_effect:
                side_effect = self._u.configured.get('__side_effect__')
                result = self.__evaluate_side_effect(side_effect, args, kwargs)
            elif has_return_value:
                rv = self._u.configured.get('__return_value__')
                if callable(rv):
                    result = rv(self)  # type: ignore[arg-type]
                else:
                    result = rv
            else:
                # Forward to delegate method (set by __getattr__ for attribute access)
                delegate_method = getattr(self._u, 'delegate_method', None)
                if delegate_method is not None and callable(delegate_method):
                    result = delegate_method(*args, **kwargs)
                else:
                    # Forward to top-level delegate (only works when mock has a name
                    # that matches a method on the delegate)
                    delegate = self._u.delegate
                    if delegate is not None:
                        name = self._u.name
                        attr_name = (
                            name.rsplit('.', 1)[-1] if name else '__call__'
                        )
                        method = getattr(delegate, attr_name, None)
                        if method is not None and callable(method):
                            result = method(*args, **kwargs)
        except BaseException as e:
            error = e
            raise

        # Always record call detail (even when an exception was raised)
        elapsed = (time.monotonic_ns() - start) / 1e9
        record = Call(
            path=self._u.path,
            timestamp=time.monotonic_ns(),
            took=elapsed,
            is_async=is_async,
            args=args,
            kwargs=dict(kwargs),
            result=result if error is None else None,
            error=error,
        )
        self._u.call_records.append(record)
        self.__propagate_call(record)
        return result

    def __enter__(self) -> Mock:
        """Clone self into a fresh child for independent configuration."""
        name_mangled = self._u.name
        clone_name = f'{name_mangled} (child)' if name_mangled else ''
        origin_val = self._u.origin
        delegate_val = self._u.delegate
        # __init__ creates _u with defaults; overwrite what we need.
        clone = Mock(name=clone_name)
        clone._u.origin = origin_val
        clone._u.delegate = delegate_val
        return clone

    def __eq__(self, other: Any) -> bool:  # type: ignore[override]
        """Identity-only comparison (two Mocks are never equal unless same object)."""
        return self is other

    def __hash__(self) -> int:  # type: ignore[override]
        """Hash by object id so mocks can be used in sets/dicts as unique keys."""
        return id(self)

    def __iter__(self) -> Iterator[Any]:
        """Yield items from the configured return value (if it is a sequence).

        This allows ``for e in mock`` and dict-set comprehension patterns like
        ``{e.attr: e.id for e in mock.query}`` when ``mock.query.returns([...])``
        has been used to configure child stubs.
        """
        rv = self._u.configured.get('__return_value__')
        if rv is None:
            raise TypeError(
                f'{type(self).__name__!r} object is not iterable -- '
                f'use .returns([...]) to configure iteration data'
            )
        try:
            return iter(rv)  # type: ignore[return-value]
        except TypeError as exc:
            raise TypeError(
                f'{type(rv).__name__!r} object is not iterable -- '
                f'use .returns() with a sequence (list, tuple, etc.)'
            ) from exc

    def __len__(self) -> int:
        """Return the number of items in the configured return value."""
        rv = self._u.configured.get('__return_value__')
        if rv is None:
            raise TypeError(
                f'{type(self).__name__!r} object has no len() -- '
                f'use .returns([...]) to configure data'
            )
        try:
            return len(rv)  # type: ignore[arg-type]
        except TypeError as exc:
            raise TypeError(
                f'{type(rv).__name__!r} object has no len() -- '
                f'use a sequence (list, tuple, etc.)'
            ) from exc

    def __exit__(
        self,
        _exc_type: Any,
        _exc_val: Any,
        _exc_tb: Any,
    ) -> None:
        """Reset call history on exit."""
        self.reset()

    def __getattr__(self, name: str) -> Mock:
        """Return a cached child Mock or pre-populated stub for the given attribute."""
        # Guard against infinite recursion during early init (before _u is set).
        try:
            u = object.__getattribute__(self, '_u')
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from None
        if name in u.configured:
            return self._u.configured[name]

        # Delegate-aware lookup: if a delegate is set and has this attribute,
        # create a Mock wrapper that forwards calls to it.
        delegate = self._u.delegate
        if delegate is not None and hasattr(delegate, name):
            child = Mock()
            child._u.name = f'{self._u.name}.{name}' if self._u.name else name
            child._u.path = f'{self._u.path}.{name}' if self._u.path else name
            child._u.parent = self
            # Store the real method reference for forwarding in __call__
            real_attr = getattr(delegate, name)
            child._u.delegate_method = real_attr  # type: ignore[attr-defined]
            self._u.children[name] = child
            return child

        # Return cached child or create new one
        if name not in self._u.children:
            child = Mock()
            child._u.name = f'{self._u.name}.{name}' if self._u.name else name
            child._u.path = f'{self._u.path}.{name}' if self._u.path else name
            child._u.parent = self
            self._u.children[name] = child
        return self._u.children[name]

    def __setattr__(self, name: str, value: Any) -> None:  # type: ignore[override]
        """Accept arbitrary attributes; raise MockError for configured stub clobbering."""
        # Check if this name corresponds to a configured mock stub (clobbering attempt).
        # _u may not exist yet during early init — skip the check in that case.
        try:
            u = object.__getattribute__(self, '_u')
            configured = u.configured
        except AttributeError:
            configured = None
        else:
            if name in configured:
                raise MockError(
                    f'Cannot overwrite mock configuration for "{name}". '
                    f'Use the fluent API (returns(), side_effect()) to configure.'
                )
        # compat: to ease test porting, we want `side_effect` assignment to delegate to the fluent api
        if name == 'side_effect':
            self.side_effect(value)
            return None  # __setattr__ must return None per Python data model
        object.__setattr__(self, name, value)

    def __evaluate_side_effect(
        self,
        side_effect: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        """Evaluate side_effect with priority: iterable → exception → callable."""
        # Exception instance or class -- raise it
        if isinstance(side_effect, BaseException):
            raise side_effect
        if isinstance(side_effect, type) and issubclass(side_effect, BaseException):
            raise side_effect()

        # Iterable -- iterate through values (cached iterator for sequential consumption)
        if isinstance(side_effect, Iterable) and not isinstance(side_effect, (str, bytes)):
            cached_iter = self._u.side_effect_iter
            if cached_iter is None:
                new_iter = iter(side_effect)
                self._u.side_effect_iter = new_iter
                return next(new_iter)
            return next(cached_iter)  # Raises StopIteration when exhausted

        # Callable -- invoke with args/kwargs
        if callable(side_effect):
            return side_effect(*args, **kwargs)

        return self

    def __matches_args(self, actual: tuple[Any, ...], expected: tuple[Any, ...]) -> bool:
        """Compare actual args against expected with matcher dispatch."""
        if len(actual) != len(expected):
            return False
        for act, exp in zip(actual, expected):
            if isinstance(exp, Mock):
                # It's a child mock -- compare by identity (same as __eq__)
                if exp is not None and exp != act:
                    return False
            elif hasattr(exp, '__eq__'):
                if not exp.__eq__(act):  # type: ignore[union-attr]
                    return False
            elif exp is not None and act is not None and exp != act:
                return False
        return True

    def __matches_kwargs(self, actual: dict[str, Any], expected: dict[str, Any]) -> bool:
        """Compare actual kwargs against expected with matcher dispatch."""
        for key, exp in expected.items():
            if key not in actual:
                return False
            act = actual[key]
            if isinstance(exp, Mock):
                if exp is not None and exp != act:
                    return False
            elif hasattr(exp, '__eq__'):
                if not exp.__eq__(act):  # type: ignore[union-attr]
                    return False
            elif exp is not None and act is not None and exp != act:
                return False
        return True

    def __resolve_conditional(
        self, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> Mock | None:
        """Return the subgraph for the first matching condition, or ``None``."""
        for (exp_args, exp_kwargs, subgraph) in self._u.when_conditions:
            if self.__matches_args(args, exp_args) and self.__matches_kwargs(kwargs, exp_kwargs):
                return subgraph
        return None

    def __populate_members(self, origin: type) -> None:
        """Pre-create child Mock stubs for all public members of the origin."""
        members: set[str] = set()

        if hasattr(origin, '__protocol_attrs__'):
            members.update(origin.__protocol_attrs__)
        elif hasattr(origin, '__annotations__'):
            all_attrs = set(dir(origin))
            for attr_name in all_attrs:
                if attr_name.startswith('_'):
                    continue
                if hasattr(origin, attr_name):
                    attr = getattr(origin, attr_name)
                    if callable(attr):
                        members.add(attr_name)

        if not members:
            for attr_name in dir(origin):
                if not attr_name.startswith('_'):
                    members.add(attr_name)

        ann = getattr(origin, '__annotations__', {})
        for attr_name in ann:
            if not attr_name.startswith('_'):
                members.add(attr_name)

        # Finally scan __dict__ directly for class-level attributes not found via annotations
        for attr_name in getattr(origin, '__dict__', {}):
            if not attr_name.startswith('_') and hasattr(origin, attr_name):
                members.add(attr_name)

        for name in members:
            child_name = f'{self._u.name}.{name}' if self._u.name else name
            child = Mock(name=child_name)
            child._u.parent = self
            self.__set_child_configured(name, child)

    def __propagate_call(self, record: Call) -> None:
        """Append *record* to ``child_call_records`` on ancestors (self-calls stay in ``call_records``)."""
        # Walk up parent chain for ancestor aggregation.
        obj = self._u.parent
        while obj is not None:
            obj._u.child_call_records.append(record)  # reached via attribute access on this ancestor
            obj = obj._u.parent

    def __set_child_configured(self, name: str, child: Mock) -> None:
        """Set a pre-configured child for a given attribute name."""
        self._u.configured[name] = child

    def __side_effect(
        self,
        eff: Union[Callable[..., Any], BaseException, type, Iterable[Any]] | None,
    ) -> Mock:
        """Set side effect (callable/exception/iterable). Clears `returns`."""
        self._u.configured['__side_effect__'] = eff
        self._u.has_side_effect = True
        self._u.has_return_value = False
        return self

    def __traverse(self):  # type: ignore[no-untyped-def]
        """Yield self and all descendants."""
        yield self
        for child in self._u.children.values():
            yield from child.__traverse()

    @property
    def all_calls(self) -> CallList:
        """Aggregate of self-invokations and child-invokations."""
        return CallList(self._u.call_records + self._u.child_call_records)

    @property
    def call_count(self) -> int:
        """Number of calls recorded for this mock."""
        return len(self._u.call_records)

    @property
    def calls(self) -> Sequence[Call]:
        """Immutable sequence of all recorded calls."""
        history = self._u.call_records
        return tuple(history)

    @property
    def called(self) -> bool:
        """Return True if this mock has been called (self-invocations.)"""
        return self.call_count > 0

    @property
    def child_calls(self) -> CallList:
        """Calls reached through child attribute access only (not self-invocations.)"""
        return CallList(self._u.child_call_records)

    @property
    def mock_calls(self) -> CallList:
        """All calls to this mock (self-invocations.)"""
        return CallList(self._u.call_records)

    @property
    def origin(self) -> Optional[type]:
        """The origin type this mock stands in for."""
        return self._u.origin

    @property
    def side_effect(self) -> Callable[[Union[Callable[..., Any], BaseException, type, Iterable[Any]] | None], Mock]:
        """Set side effect (callable/exception/iterable). Clears `returns`."""
        return self.__side_effect

    @side_effect.setter
    def side_effect(self, value: Union[Callable[..., Any], BaseException, type, Iterable[Any]] | None) -> None:
        self.__side_effect(value)

    def when(self, *args: Any, **kwargs: Any) -> Mock:
        """Create a conditionally-dispatched subgraph mock keyed by matcher arguments.

        Identical matcher tuples always return the same subgraph (dedup via canonical name).
        The matched subgraph's ``__call__`` is forwarded matching call args for dispatch
        to further nested conditions or flat config.

        :raises MockError: if no matcher arguments are provided (ambiguous condition).
        """
        if not args and not kwargs:
            raise MockError('when() requires at least one matcher argument')

        for (exp_args, exp_kwargs, subgraph) in self._u.when_conditions:
            if exp_args == tuple(args) and exp_kwargs == dict(kwargs):
                return subgraph

        canonical_name = '%s.when(%r,%r)' % (self._u.name, args, kwargs)

        subgraph = Mock(name=canonical_name)
        subgraph._u.parent = self
        self._u.children[canonical_name] = subgraph
        self._u.when_conditions.append((tuple(args), dict(kwargs), subgraph))
        return subgraph

    def returns(self, value_or_callable: Any) -> Mock:
        """Set fixed return value or callable. Callable receives the mocked instance as its sole argument. Clears side_effect."""
        self._u.configured['__return_value__'] = value_or_callable
        self._u.has_return_value = True
        self._u.has_side_effect = False
        return self

    def reset(
        self,
        *,
        preserve_stubs: bool = True,
        preserve_sideeffects: bool = True,
    ) -> None:
        """Reset this mock's call tracking and optionally its configuration.

        :param preserve_stubs: If ``True`` (default), retain child stubs created by
            attribute access or from an *origin*.  If ``False``, recursively clear
            all children so that subsequent attribute access creates fresh mocks.
        :param preserve_sideeffects: If ``True`` (default), keep fluent-configuration
            values such as ``__return_value__`` and ``__side_effect__`` intact.  If
            ``False``, wipe all ``__*-prefixed* configuration keys from
            ``_u.configured`` and reset the has_* flags, but leave structural
            stubs (origin-prepopulated members) untouched.
        """
        for m in self.__traverse():
            m._u.call_records = list[Call]()
            m._u.child_call_records = list[Call]()

        self._u.call_records = []
        self._u.side_effect_iter = None

        if not preserve_sideeffects:
            self._u.has_return_value = False
            self._u.has_side_effect = False
            keys_to_delete: list[str] = [k for k in self._u.configured if k.startswith('__')]
            for key in keys_to_delete:
                del self._u.configured[key]

        if not preserve_stubs:

            def _clear_children_recursively(m: Mock) -> None:
                for child in m._u.children.values():
                    child.reset(preserve_stubs=True, preserve_sideeffects=True)
                m._u.children = {}

            _clear_children_recursively(self)

    def called_with(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Return True if any recorded call matches *args* and **kwargs.

        Uses ``==`` dispatch for each argument, enabling matcher support.
        """
        history = self._u.call_records
        for record in history:
            if self.__matches_args(record.args, args) and \
               self.__matches_kwargs(record.kwargs, kwargs):
                return True
        return False


__all__ = [
    'Call',
    'CallList',
    'Mock',
    'MockError',
]
