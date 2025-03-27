# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from src.assertions import *
from src.facts import fact
from src.theories import theory, inlinedata
from src.traits import trait

@theory
@inlinedata('1','2','3')
@inlinedata('2','3','4')
@trait('category', 'math')
def traited_theory_func(a, b, c) -> None:
    assert (a == '1' and b == '2' and c == '3') or (a == '2' and b == '3' and c == '4')

@fact
@trait('category', 'science')
async def traited_fact_func() -> None:
    await asyncio.sleep(0.1)
    assert True

@fact
@trait('integration')
async def traited_integration_test() -> None:
    await asyncio.sleep(0.1)
    assert False, 'unit test run excludes "integration" tests.'

    
