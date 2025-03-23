# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from src.assertions import *
from src.facts import fact

@fact
def fact_func() -> None:
    """Function BVT"""
    assert 1 == 1

@fact
async def async_fact_func() -> None:
    """Async Function BVT"""
    await asyncio.sleep(0.1)
    assert 1 == 1

class FactClass:

    __valueTest:int
    """Tests check this to verify that every test method execution gets a new class instance."""

    def __init__(self):
        self.__valueTest = 0

    @fact
    async def async_meth(self) -> None:
        """Async Method BVT"""
        self.__valueTest = self.__valueTest + 1
        await asyncio.sleep(0.1)
        assert self.__valueTest == 1

    @fact
    def meth1(self) -> None:
        """Instance Method BVT"""
        self.__valueTest = self.__valueTest + 1
        assert self.__valueTest == 1

    @fact
    @classmethod
    def meth2(cls) -> None:
        """Class Method BVT"""
        assert not hasattr(cls, '__valueTest')

    @fact
    @staticmethod
    def meth3() -> None:
        """Static Method BVT"""
        assert not hasattr(FactClass, '__valueTest')
