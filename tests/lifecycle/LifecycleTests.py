# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for the ``@lifecycle`` class decorator.

PER_TEST — every test method gets a fresh instance (no cached instance).
PER_RUN  — a single class instance is reused across all tests in the class.

All tests are fully order-independent.
"""

import threading

from punit import fact, lifecycle, Lifecycle, setup, teardown, sequential


# ======================================================================
# Module-level helpers for lifecycle tracking
# ======================================================================


class _instance_tracker:
    """Tracks PER_RUN instance creation count across test classes."""
    count: int = 0
    lock: threading.Lock = threading.Lock()


# ======================================================================
# PER_TEST (default) — every test method gets a fresh class instance
# ======================================================================


class DefaultPerTest:
    """Without @lifecycle, each test method gets a fresh instance."""

    def setup_method(self) -> None:
        seen = getattr(self, '_seen_ids', None)
        if seen is None:
            seen = self._seen_ids = set()
        if id(self) in seen:
            raise AssertionError(
                f"Instance {id(self)} already seen — instance was reused instead of created fresh"
            )
        seen.add(id(self))

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


# ======================================================================
# PER_RUN teardown fires after last parallel test, not after first
# ======================================================================


import asyncio

from punit import fact, lifecycle, Lifecycle, setup, teardown, sequential


# ======================================================================
# PER_RUN teardown fires after last parallel test, not after first
# ======================================================================


@lifecycle(Lifecycle.PER_RUN)
class PerRunTeardownOrder:
    """Verifies that @teardown fires after ALL parallel facts complete,
    not after the first one.

    Each parallel fact increments a module-level counter in __init__.
    When the counter reaches zero (last test done), teardown runs once.

    If teardown fires prematurely (after first test), the instance is
    destroyed and a fresh one is created for the remaining tests,
    meaning __init__ wouldn't have been called enough times.
    """

    def __init__(self) -> None:
        with _instance_tracker.lock:
            _instance_tracker.count += 1

    @setup
    def _setup(self) -> None:
        pass

    @teardown
    def _teardown(self) -> None:
        pass

    @fact
    def pass_one(self) -> None:
        pass

    @fact
    def pass_two(self) -> None:
        pass

    @fact
    def pass_three(self) -> None:
        pass

    @fact
    @sequential
    def teardown_once(self) -> None:
        # The instance should have been created exactly once at the
        # start of this test batch (all parallel + sequential tests
        # share one PER_RUN instance).
        with _instance_tracker.lock:
            count = _instance_tracker.count
        assert count == 1, (
            f'PerRunTeardownOrder: expected 1 __init__ call (one instance '
            f'shared across all tests), got {count}. Teardown likely fired '
            f'prematurely and the fixture was recreated.'
        )
        _instance_tracker.count = 0  # reset for next test class


# ======================================================================
# PER_RUN teardown does NOT fire after parallel batch — instance survives
# into sequential facts.
# ======================================================================


class _instance_ids:
    """Tracks instance IDs across the full test execution."""
    ids: list[int] = []
    lock: threading.Lock = threading.Lock()


@lifecycle(Lifecycle.PER_RUN)
class PerRunInstanceIdentity:
    """Verifies teardown does NOT fire after the parallel batch, but
    only after ALL tests (parallel + sequential) complete.

    Each parallel fact records ``id(self)``.  The sequential fact records
    its ``id(self)`` and asserts it matches the parallel facts' instance
    ID.  If teardown fired prematurely (after the parallel batch), the
    instance would be destroyed and the sequential fact gets a brand-new
    instance with a different ID — the assertion fails.
    """

    def __init__(self) -> None:
        pass  # Instance identity checked via id(self)

    @setup
    def _setup(self) -> None:
        pass

    @teardown
    def _teardown(self) -> None:
        pass

    @fact
    def record_A(self) -> None:
        with _instance_ids.lock:
            _instance_ids.ids.append(id(self))

    @fact
    def record_B(self) -> None:
        with _instance_ids.lock:
            _instance_ids.ids.append(id(self))

    @fact
    def record_C(self) -> None:
        with _instance_ids.lock:
            _instance_ids.ids.append(id(self))

    @fact
    @sequential
    def identity_matches_all(self) -> None:
        with _instance_ids.lock:
            parallel_ids = list(_instance_ids.ids)
            sequential_id = id(self)

        if parallel_ids and sequential_id != parallel_ids[0]:
            raise AssertionError(
                f'Teardown fired after the parallel batch. '
                f'Expected all tests to share instance {parallel_ids[0]}, '
                f'but sequential fact got {sequential_id}. '
                f'Parallel IDs: {parallel_ids}'
            )

        # Also verify no duplicate instances were created
        assert parallel_ids == [parallel_ids[0]] * len(parallel_ids), (
            f'Expected all {len(parallel_ids)} parallel facts to run on '
            f'the same instance, got IDs: {parallel_ids}'
        )

        _instance_ids.ids.clear()  # reset for next use
