# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from punit import fact, theory, inlinedata


@fact(timeout=0.01)
async def test_async_timeout() -> None:
    pass


@theory(timeout=0.01)
@inlinedata(1, 2)
def test_theory_timeout(x: int, y: int) -> None:
    pass
