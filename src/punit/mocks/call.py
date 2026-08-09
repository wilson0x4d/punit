# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
