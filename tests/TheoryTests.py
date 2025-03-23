# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from src.assertions import *
from src.theories import theory, inlinedata

@theory
@inlinedata('1','2','3')
@inlinedata('2','3','4')
def theory_func(a, b, c) -> None:
    """Function BVT"""
    assert (a == '1' and b == '2' and c == '3') or (a == '2' and b == '3' and c == '4')

@theory
@inlinedata('1','2','3')
@inlinedata('2','3','4')
async def async_theory_func(a, b, c) -> None:
    """Async Function BVT"""
    await asyncio.sleep(0.1)
    assert (a == '1' and b == '2' and c == '3') or (a == '2' and b == '3' and c == '4')

class TheoryClass:

    __valueTest:int
    """Tests check this to verify that every test method execution gets a new class instance."""

    def __init__(self):
        self.__valueTest = 0

    @theory
    @inlinedata('3','4','5')
    @inlinedata('4','5','6')
    async def async_meth(self, a, b, c) -> None:
        """Async Method BVT"""
        self.__valueTest = self.__valueTest + 1
        await asyncio.sleep(0.1)
        assert self.__valueTest == 1
        assert (a == '3' and b == '4' and c == '5') or (a == '4' and b == '5' and c == '6')

    @theory
    @inlinedata('3','4','5')
    @inlinedata('4','5','6')
    def meth1(self, a, b, c) -> None:
        """Instance Method BVT"""
        self.__valueTest = self.__valueTest + 1
        assert (a == '3' and b == '4' and c == '5') or (a == '4' and b == '5' and c == '6')

    @theory
    @inlinedata('5','6','7')
    @inlinedata('6','7','8')
    @classmethod
    def meth2(cls, a, b, c) -> None:
        """Class Method BVT"""
        assert (a == '5' and b == '6' and c == '7') or (a == '6' and b == '7' and c == '8')

    @theory
    @inlinedata('7','8','9')
    @inlinedata('8','9','0')
    @staticmethod
    def meth3(a, b, c) -> None:
        """Static Method BVT"""
        assert (a == '7' and b == '8' and c == '9') or (a == '8' and b == '9' and c == '0')

@theory
def theory_nodata() -> None:
    assert False, '@theory with no data will not be run.'

@theory
@inlinedata()
def theory_nodata() -> None:
    assert False, '@theory with empty data will not be run.'
