# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for the @parallel decorator."""

import inspect

from punit import fact, parallel, sequential


# A non-@parallel function for negative testing
@sequential
def sequential_bare_func() -> None:
    """A sequential (undecorated by @parallel) function."""
    pass


# ---------------------------------------------------------------------------
# Decorator-level tests (no execution framework – just marker verification)
# ---------------------------------------------------------------------------


@fact
@parallel
def parallel_bare_func() -> None:
    """@parallel on a bare function sets the marker."""
    unwrapped = inspect.unwrap(parallel_bare_func)
    assert getattr(unwrapped, '__punit_parallel', None) is True


@fact
def parallel_marker_not_on_undecorated() -> None:
    """Undecorated functions must NOT have the parallel marker."""
    assert getattr(inspect.unwrap(sequential_bare_func), '__punit_parallel', None) is not True


@fact
@parallel
async def async_parallel_func() -> None:
    """@parallel on an async function works too."""
    await __import__('asyncio').sleep(0.01)
    unwrapped = inspect.unwrap(async_parallel_func)
    assert getattr(unwrapped, '__punit_parallel', None) is True


# ---------------------------------------------------------------------------
# Method-level tests
# ---------------------------------------------------------------------------


class ParallelMethodTests:

    __counter: int = 0

    @fact
    @parallel
    def parallel_method(self) -> None:
        """@parallel on a method sets the marker."""
        unwrapped = inspect.unwrap(self.parallel_method)
        assert getattr(unwrapped, '__punit_parallel', None) is True

    @fact
    def non_parallel_method(self) -> None:
        """Non-parallel methods must NOT have the marker."""
        unwrapped = inspect.unwrap(self.non_parallel_method)
        assert getattr(unwrapped, '__punit_parallel', None) is not True


# ---------------------------------------------------------------------------
# Class-level @parallel — must apply to ALL methods
# ---------------------------------------------------------------------------


@parallel
class ParallelClassTests:
    """When @parallel decorates a class, all methods get the marker."""

    @fact
    def method_one(self) -> None:
        """All methods in a @parallel class get the marker."""
        unwrapped = inspect.unwrap(self.method_one)
        assert getattr(unwrapped, '__punit_parallel', None) is True

    @fact
    def method_two(self) -> None:
        """Even later-declared methods get the marker."""
        unwrapped = inspect.unwrap(self.method_two)
        assert getattr(unwrapped, '__punit_parallel', None) is True


# ---------------------------------------------------------------------------
# Interaction with @sequential
# ---------------------------------------------------------------------------


@fact
@parallel
@sequential
def parallel_and_sequential() -> None:
    """@parallel can be stacked with @sequential; both markers present."""
    unwrapped = inspect.unwrap(parallel_and_sequential)
    assert getattr(unwrapped, '__punit_parallel', None) is True
    assert getattr(unwrapped, '__punit_sequential', None) is True


# ---------------------------------------------------------------------------
# Decorator returns original target unchanged
# ---------------------------------------------------------------------------


@fact
def parallel_returns_target() -> None:
    """parallel() returns the original function unchanged."""

    def my_func() -> None:
        pass

    decorated = parallel(my_func)
    assert decorated is my_func
    unwrapped = inspect.unwrap(my_func)
    assert getattr(unwrapped, '__punit_parallel', None) is True


# ---------------------------------------------------------------------------
# Class @parallel returns original class unchanged
# ---------------------------------------------------------------------------


@fact
def parallel_class_decorator_returns_target() -> None:
    """parallel() on a class returns the class unchanged."""

    class MyClass:
        pass

    decorated = parallel(MyClass)
    assert decorated is MyClass
    assert getattr(MyClass, '__punit_parallel', None) is True


# ---------------------------------------------------------------------------
# @sequential on functions
# ---------------------------------------------------------------------------


@fact
def sequential_on_function_sets_marker() -> None:
    """@sequential on a function sets the marker on the unwrapped target."""

    def my_func() -> None:
        pass

    decorated = sequential(my_func)
    assert decorated is my_func
    unwrapped = inspect.unwrap(my_func)
    assert getattr(unwrapped, '__punit_sequential', None) is True


@fact
def sequential_on_async_function_sets_marker() -> None:
    """@sequential on an async function sets the marker on the unwrapped target."""

    async def my_async_func() -> None:
        pass

    decorated = sequential(my_async_func)
    assert decorated is my_async_func
    unwrapped = inspect.unwrap(my_async_func)
    assert getattr(unwrapped, '__punit_sequential', None) is True


# ---------------------------------------------------------------------------
# @sequential on methods
# ---------------------------------------------------------------------------


class SequentialMethodTests:
    """Tests for @sequential on individual methods."""

    @fact
    @sequential
    def sequential_method_marker_present(self) -> None:
        """@sequential on a method marks it."""
        unwrapped = inspect.unwrap(self.sequential_method_marker_present)
        assert getattr(unwrapped, '__punit_sequential', None) is True

    @fact
    def non_sequential_method_marker_absent(self) -> None:
        """Non-marked methods must NOT have the sequential marker."""
        unwrapped = inspect.unwrap(self.non_sequential_method_marker_absent)
        assert getattr(unwrapped, '__punit_sequential', None) is not True


# ---------------------------------------------------------------------------
# @sequential on classes — must apply to ALL methods
# ---------------------------------------------------------------------------


@sequential
class SequentialClassTests:
    """When @sequential decorates a class, all methods get the marker."""

    @fact
    def class_method_one(self) -> None:
        """All methods in a @sequential class get the marker."""
        unwrapped = inspect.unwrap(self.class_method_one)
        assert getattr(unwrapped, '__punit_sequential', None) is True
        assert getattr(SequentialClassTests, '__punit_sequential', None) is True

    @fact
    def class_method_two(self) -> None:
        """Even later-declared methods get the marker."""
        unwrapped = inspect.unwrap(self.class_method_two)
        assert getattr(unwrapped, '__punit_sequential', None) is True


# ---------------------------------------------------------------------------
# @sequential returns original target unchanged
# ---------------------------------------------------------------------------


@fact
def sequential_returns_target() -> None:
    """sequential() on a function returns the target unchanged."""

    def my_func() -> None:
        pass

    decorated = sequential(my_func)
    assert decorated is my_func
    assert getattr(my_func, '__punit_sequential', None) is True


@fact
def sequential_class_decorator_returns_target() -> None:
    """sequential() on a class returns the class unchanged."""

    class MyClass:
        pass

    decorated = sequential(MyClass)
    assert decorated is MyClass
    assert getattr(MyClass, '__punit_sequential', None) is True
