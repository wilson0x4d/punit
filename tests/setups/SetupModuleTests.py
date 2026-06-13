# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact, setup
from punit.mocks import Mock


# Module-level mock to track module-scoped setup invocation count.
_module_setup_calls = Mock()


@setup
def module_setup() -> None:
    """Module-scoped setup; fires before every test in this module."""
    _module_setup_calls()


@fact
def aaa_fact_one() -> None:
    """First fact; triggers the module-scoped setup once."""
    pass


@fact
def verify_setup_counter() -> None:
    """Verify the module-scoped setup has fired exactly twice so far.

    Both aaa_fact_one and bbb_verify_setup_counter have triggered their own
    setups before this test runs, so count should be 2.
    """
    assert _module_setup_calls.call_count == 2, \
        f"Expected setup to fire 2 times, got {_module_setup_calls.call_count}"


@fact
def fact_three() -> None:
    """Third fact; another trigger of the module-scoped setup."""
    pass


@fact
def verify_final_count() -> None:
    """Verify the module-scoped setup has fired exactly 4 times total.

    All four facts (aaa_fact_one, bbb_verify_setup_counter, ccc_fact_three,
    and this fact) have triggered setups before this assertion runs.
    """
    assert _module_setup_calls.call_count == 4, \
        f"Expected setup to fire 4 times, got {_module_setup_calls.call_count}"
