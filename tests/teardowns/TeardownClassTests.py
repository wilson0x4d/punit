# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from punit import fact, teardown
from punit.mocks import Mock


# Module-level mock to track class-scoped teardown invocation count.
_class_teardown_calls = Mock()


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
        assert _class_teardown_calls.call_count == 3, \
            f"Expected class-scoped teardown to fire 3 times by now, got {_class_teardown_calls.call_count}"

    @teardown
    def class_teardown(self) -> None:
        """Class-scoped teardown; fires after every test in this class."""
        _class_teardown_calls()
