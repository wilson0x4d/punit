# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Exception assertion helpers for verifying raised exceptions.

Provides the ``raises`` class which can verify that a callable raises an
exception of the expected type using either Python 3.11+ generic syntax or
an explicit ``expect`` keyword argument.

Example
-------

.. code-block:: python

    from punit import exceptions

    class MyException(Exception):
        pass

    def raises_exception():
        raise MyException()

    assert exceptions.raises[MyException](raises_exception)
    assert exceptions.raises[MyException](raises_exception, exact=True)

"""

from typing import Any, Callable, Generic, Optional, TypeVar, cast, get_args


TError = TypeVar('TError', bound=Exception)


class raises(Generic[TError]):
    """Assert that a callable raises an expected exception.

    Use ``raises`` to verify that a function, method, or lambda expression
    raises an exception of the expected type. Two syntaxes are supported:

    * Python >=3.11 generic syntax: ``raises[MyException](action)``
    * Explicit expect argument (for <=3.11): ``raises(action, expect=MyException)``

    The ``exact`` parameter controls whether the raised exception must be an exact
    type match (not a subclass) of the expected type.

    Example
    -------

    .. code-block:: python

        class MyException(Exception):
            pass

        def raises_exception():
            raise MyException()

        assert raises[MyException](raises_exception)
        assert not raises[ValueError](raises_exception)
        assert raises[MyException](raises_exception, exact=True)
    """

    __action: Callable[[], Any]
    __exact: bool
    __expect: Optional[TError | type]

    def __init__(self, action: Callable[[], Any], *, exact: bool = False, expect: Optional[TError | type] = None) -> None:
        self.__action = action
        self.__exact = exact
        self.__expect = expect

    def __bool__(self) -> bool:
        try:
            self.__action()
        except BaseException as ex:
            expected = self.__expect
            if expected is None and hasattr(self, '__orig_class__') is not None:
                expected = get_args(getattr(self, '__orig_class__'))[0]
            if self.__exact:
                return type(ex) is expected
            elif expected is not None:
                return issubclass(type(ex), cast(Any, expected))
        return False


__all__ = [
    'raises'
]
