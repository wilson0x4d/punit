# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Callable, Optional, Union, cast


class CallableMetadata:

    __callable: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]
    __class_name: str
    __module_name: str
    __name: str

    def __init__(self, callable: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]) -> None:
        self.__callable = callable
        parts = callable.__qualname__.replace(f'{callable.__module__}.', '').split('.')[0:-1]
        self.__class_name = '.'.join(p for p in parts if p != '<locals>')
        self.__module_name = callable.__module__
        self.__name = callable.__name__

    @property
    def class_name(self) -> Optional[str]:
        return self.__class_name

    @property
    def filter_name(self) -> str:
        """
        The name used for pattern matched "Test Filtering".
        """
        return f'{".".join(self.__module_name.split(".")[1:])}/{"" if self.__class_name is None or len(self.__class_name) == 0 else f"{self.__class_name}/"}{self.__name}'

    @property
    def module_name(self) -> str:
        return self.__module_name

    @property
    def name(self) -> str:
        return self.__name
