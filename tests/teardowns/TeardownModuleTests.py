# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from punit import fact, teardown


# Module-level counter to verify teardown invocation count.
_teardown_call_count = 0


@teardown
def module_teardown() -> None:
    """Module-scoped teardown — fires after every test in this module."""
    global _teardown_call_count
    _teardown_call_count += 1


@fact
def aaa_fact_one() -> None:
    """First fact triggers one teardown call."""
    # teardown fires AFTER this test, so count is still 0 during execution.
    pass


@fact
async def async_fact_two() -> None:
    """Async fact also triggers the module-scoped teardown."""
    await asyncio.sleep(0.01)
    # After this test runs, teardown fires — count becomes 1.


@fact
def fact_three() -> None:
    """Third fact — verify total teardown count after all tests run."""
    global _teardown_call_count
    assert _teardown_call_count == 2, \
        f"Expected teardown to fire 2 times by now, got {_teardown_call_count}"
