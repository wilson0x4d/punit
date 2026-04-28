# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Callable, Optional, Union, cast


class CallableMetadata:

    __callable:Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]
    __className:str
    __moduleName:str
    __name:str

    def __init__(self, callable:Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]) -> None:
        self.__callable = callable
        self.__className = '.'.join(callable.__qualname__.replace(f'{callable.__module__}.', '').split('.')[0:-1])
        self.__moduleName = callable.__module__
        self.__name = callable.__name__

    @property
    def className(self) -> Optional[str]:
        return self.__className

    @property
    def filterName(self) -> str:
        """
        The name used for pattern matched "Test Filtering".
        """
        return f'{".".join(self.__moduleName.split(".")[1:])}/{"" if self.__className is None or len(self.__className) == 0 else f"{self.__className}/"}{self.__name}'

    @property
    def moduleName(self) -> str:
        return self.__moduleName

    @property
    def name(self) -> str:
        return self.__name
