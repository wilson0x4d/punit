# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact, setup


# Module-level counter to verify module-scoped setup invocation count.
_setup_call_count = 0


@setup
def module_setup() -> None:
    """Module-scoped setup; fires before every test in this module."""
    global _setup_call_count
    _setup_call_count += 1


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
    global _setup_call_count
    assert _setup_call_count == 2, \
        f"Expected setup to fire 2 times, got {_setup_call_count}"


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
    global _setup_call_count
    assert _setup_call_count == 4, \
        f"Expected setup to fire 4 times, got {_setup_call_count}"
