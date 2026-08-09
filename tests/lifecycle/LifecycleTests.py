# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for the ``@lifecycle`` class decorator.

PER_TEST — every test method gets a fresh instance (no cached instance).
PER_RUN  — a single class instance is reused across all tests in the class.

All tests are fully order-independent.
"""

from punit import fact, lifecycle, Lifecycle, setup, teardown, sequential


# ======================================================================
# PER_TEST (default) — every test method gets a fresh class instance
# ======================================================================


class _per_test_instance_ids:
    """Module-level list tracking instance IDs seen across all PER_TEST tests."""
    ids: list[int] = []


class DefaultPerTest:
    """Without @lifecycle, each test method gets a fresh instance."""

    @setup
    def setup_method(self) -> None:
        if id(self) in _per_test_instance_ids.ids:
            raise AssertionError(
                f"Instance {id(self)} already seen — instance was reused instead of created fresh"
            )
        _per_test_instance_ids.ids.append(id(self))

    @teardown
    def teardown_method(self) -> None:
        pass

    @fact
    def test_a(self) -> None:
        assert self is not None

    @fact
    def test_b(self) -> None:
        assert self is not None


# ======================================================================
# PER_RUN — one instance shared by all methods in the class
# ======================================================================


@lifecycle(Lifecycle.PER_RUN)
class PerRunSharedInstance:

    def __init__(self) -> None:
        self._run_count = 0

    @setup
    def run_once(self) -> None:
        self._run_count += 1

    @teardown
    def run_teardown(self) -> None:
        pass

    @fact
    def increment_once(self) -> None:
        self._run_count += 1

    @fact
    def increment_twice(self) -> None:
        self._run_count += 1

    @fact
    @sequential
    def verify_count(self) -> None:
        # Only fires after parallel tests finish.
        # @setup runs once, fact_increment_once runs once,
        # fact_increment_twice runs once → total = 3
        assert self._run_count == 3, f'expected 3, got {self._run_count}'
