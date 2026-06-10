# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from punit import fact, teardown


# Module-level counter to verify class-scoped teardown invocation count.
_teardown_call_count = 0


class TeardownClassTests:
    """Tests that a class-scoped @teardown fires after each method."""

    @fact
    def fact_one(self) -> None:
        """First fact; triggers the class-scoped teardown once."""
        pass

    @fact
    async def async_fact_two(self) -> None:
        """Async fact; also triggers the class-scoped teardown."""
        await asyncio.sleep(0.01)
        pass

    @fact
    @classmethod
    def fact_three(cls) -> None:
        """Class method fact; also triggers the class-scoped teardown."""
        pass

    @fact
    def check_teardown_count(self) -> None:
        """Final fact; verify total class-scoped teardown count at this point.

        Three facts have already run (fact_one, async_fact_two, fact_three),
        so three teardowns should have fired before this test runs.
        """
        global _teardown_call_count
        assert _teardown_call_count == 3, \
            f"Expected class-scoped teardown to fire 3 times by now, got {_teardown_call_count}"

    @teardown
    def class_teardown(self) -> None:
        """Class-scoped teardown; fires after every test in this class."""
        global _teardown_call_count
        _teardown_call_count += 1
