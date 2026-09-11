# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Any, Callable, Optional, Union


class CallableMetadata:
    """
    Stores introspected metadata extracted from a callable.

    Usage
    -----

    .. code-block:: python

        from punit.metadata import CallableMetadata

        meta = CallableMetadata(my_function)
        print(meta.module_name)
        print(meta.class_name)
        print(meta.name)

    """

    __callable: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable[..., Any]]
    __class_name: str
    __module_name: str
    __name: str

    def __init__(self, callable: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable[..., Any]]) -> None:
        self.__callable = callable
        parts = callable.__qualname__.replace(f'{callable.__module__}.', '').split('.')[0:-1]
        self.__class_name = '.'.join(p for p in parts if p != '<locals>')
        self.__module_name = callable.__module__
        self.__name = callable.__name__

    @property
    def class_name(self) -> Optional[str]:
        """The fully-qualified class name if the callable is a method, otherwise None."""
        return self.__class_name

    @property
    def filter_name(self) -> str:
        """
        The name used for pattern matched "Test Filtering".
        """
        return f'{".".join(self.__module_name.split(".")[1:])}/{"" if self.__class_name is None or len(self.__class_name) == 0 else f"{self.__class_name}/"}{self.__name}'

    @property
    def module_name(self) -> str:
        """The module name where the callable is defined."""
        return self.__module_name

    @property
    def name(self) -> str:
        """The callable's function or method name."""
        return self.__name
