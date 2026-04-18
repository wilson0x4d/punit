# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Callable, Optional, cast, get_args


def isNoneOrWhiteSpace(input:str):
    return input is None or len(input.lstrip()) == 0


def isNoneOrEmpty(input:str):
    return input is None or len(input) == 0


class raises[TError:Exception]:
    
    __action:Callable
    __exact:bool
    __expect:Optional[TError|type]

    def __init__(self, action:Callable, *, exact:bool = False, expect:Optional[TError|type] = None) -> None:
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
                return issubclass(type(ex), cast(Any,expected))
        return False
