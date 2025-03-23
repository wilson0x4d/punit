# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Callable, get_args

def isNoneOrWhiteSpace(input:str):
    return input is None or len(input.lstrip()) == 0

def isNoneOrEmpty(input:str):
    return input is None or len(input) == 0

class raises[TError:Exception]:
    
    __action:Callable
    __exact:bool
    __expect:TError

    def __init__(self, action:Callable, *, exact:bool = False, expect:TError = None) -> None:
        self.__action = action
        self.__exact = exact
        self.__expect = expect

    def __bool__(self) -> bool:
        try:
            self.__action()
        except BaseException as ex:
            expected = self.__expect
            if expected is None:
                expected = get_args(self.__orig_class__)[0]
            if self.__exact:
                return type(ex) is expected
            else:
                return issubclass(type(ex), expected)
        return False
