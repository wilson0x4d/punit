# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact, setup


# Module-level counter to verify class-scoped setup invocation count.
_setup_call_count = 0


class SetupClassTests:
    """Tests that a class-scoped @setup fires before each method."""

    @fact
    def aaa_check_first(self) -> None:
        """First test; verifies setup fired once (from this test)."""
        global _setup_call_count
        assert _setup_call_count == 1, \
            f"Expected class-scoped setup to fire 1 time, got {_setup_call_count}"

    @fact
    def check_second(self) -> None:
        """Second test; verifies setup fired twice total."""
        global _setup_call_count
        assert _setup_call_count == 2, \
            f"Expected class-scoped setup to fire 2 times, got {_setup_call_count}"

    @fact
    def check_third(self) -> None:
        """Third test; verifies setup fired three times total."""
        global _setup_call_count
        assert _setup_call_count == 3, \
            f"Expected class-scoped setup to fire 3 times, got {_setup_call_count}"

    @setup
    def class_setup(self) -> None:
        """Class-scoped setup; fires before every test in this class."""
        global _setup_call_count
        _setup_call_count += 1
