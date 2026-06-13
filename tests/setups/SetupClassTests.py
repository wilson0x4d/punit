# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact, setup
from punit.mocks import Mock


# Module-level mock to track class-scoped setup invocation count.
_setup_calls = Mock()


class SetupClassTests:
    """Tests that a class-scoped @setup fires before each method."""

    @fact
    def aaa_check_first(self) -> None:
        """First test; verifies setup fired once (from this test)."""
        assert _setup_calls.call_count == 1, \
            f"Expected class-scoped setup to fire 1 time, got {_setup_calls.call_count}"

    @fact
    def check_second(self) -> None:
        """Second test; verifies setup fired twice total."""
        assert _setup_calls.call_count == 2, \
            f"Expected class-scoped setup to fire 2 times, got {_setup_calls.call_count}"

    @fact
    def check_third(self) -> None:
        """Third test; verifies setup fired three times total."""
        assert _setup_calls.call_count == 3, \
            f"Expected class-scoped setup to fire 3 times, got {_setup_calls.call_count}"

    @setup
    def class_setup(self) -> None:
        """Class-scoped setup; fires before every test in this class."""
        _setup_calls()
