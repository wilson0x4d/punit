# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from punit import fact, teardown, sequential
from punit.mocks import Mock


# Module-level mock to track module-scoped teardown invocation count.
_module_teardown_calls = Mock()


@teardown
def module_teardown() -> None:
    """Module-scoped teardown; fires after every test in this module."""
    _module_teardown_calls()


@fact
@sequential
def aaa_fact_one() -> None:
    """First fact triggers one teardown call."""
    # teardown fires AFTER this test, so count is still 0 during execution.
    pass


@fact
@sequential
async def async_fact_two() -> None:
    """Async fact also triggers the module-scoped teardown."""
    await asyncio.sleep(0.01)
    # After this test runs, teardown fires; count becomes 1.


@fact
@sequential
def fact_three() -> None:
    """Third fact; verify total teardown count after all tests run."""
    assert _module_teardown_calls.call_count == 2, \
        f"Expected teardown to fire 2 times by now, got {_module_teardown_calls.call_count}"
