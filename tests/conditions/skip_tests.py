# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for the @skip decorator and its runner/report integration."""

import json

import xml.etree.ElementTree as et  # type: ignore[import-untyped]

from punit import fact, skip
from punit.TestResult import TestResult
from punit.runner import _get_skip_condition
from punit.reports.HtmlReportGenerator import HtmlReportGenerator
from punit.reports.JUnitReportGenerator import JUnitReportGenerator
from punit.reports.JsonReportGenerator import JsonReportGenerator


class _SimulatedDecorator:
    """Simulates a decorator that sets __punit_decorator."""

    def __call__(self, func):
        if not hasattr(func, '__punit_decorator'):
            setattr(func, '__punit_decorator', '@simulated')
        return func


# --- Basic @skip decorator behavior ---


@fact
def check_bare_skip_sets_true():
    """Bare @skip (no args) sets __punit_skip_condition to True."""

    @skip()
    def inner() -> None:
        pass

    assert hasattr(inner, '__punit_skip_condition'), 'Attribute missing'
    condition = getattr(inner, '__punit_skip_condition')
    assert condition is True, f'Expected True, got {condition}'


@fact
def check_skip_true_sets_true():
    """@skip(True) sets __punit_skip_condition to True."""

    @skip(True)
    def inner() -> None:
        pass

    condition = getattr(inner, '__punit_skip_condition')
    assert condition is True, f'Expected True, got {condition}'


@fact
def check_skip_false_sets_false():
    """@skip(False) sets __punit_skip_condition to False."""

    @skip(False)
    def inner() -> None:
        pass

    condition = getattr(inner, '__punit_skip_condition')
    assert condition is False, f'Expected False, got {condition}'


@fact
def check_skip_callable_sets_callable():
    """@skip(callable) sets __punit_skip_condition to the callable."""

    def my_callable() -> bool:
        return True

    @skip(my_callable)
    def inner() -> None:
        pass

    condition = getattr(inner, '__punit_skip_condition')
    assert condition is my_callable, f'Expected callable, got {condition}'


@fact
def check_skip_returns_original_function():
    """@skip(bool) returns the original target unchanged."""

    def my_func() -> int:
        return 42

    decorated = skip()(my_func)
    assert decorated is my_func, '@skip() should return the original function'

    decorated_with_true = skip()(my_func)
    assert decorated_with_true is my_func, '@skip(True) should return the original'


@fact
def check_skip_on_non_function_raises():
    """@skip on a non-function raises an exception."""
    try:
        @skip()
        class MyClass:
            pass
        assert False, 'Should have raised'
    except Exception as e:
        assert 'functions and methods' in str(e), f'Wrong error: {e}'


@fact
def check_skip_works_when_stacked_below():
    """Stacking @skip below a simulated decorator works without raising."""

    @skip()
    @_SimulatedDecorator()
    def inner() -> None:
        pass

    # Should be unconditionally skipped (condition = True)
    condition = getattr(inner, '__punit_skip_condition')
    assert condition is True, f'Expected True, got {condition}'
    assert hasattr(inner, '__punit_decorator')


@fact
def check_skip_works_when_stacked_above():
    """Stacking @skip above a simulated pUnit decorator works with condition callable."""

    def my_callable() -> bool:
        return True

    @skip(my_callable)
    @_SimulatedDecorator()
    def inner() -> None:
        pass

    condition = getattr(inner, '__punit_skip_condition')
    assert condition is my_callable, f'Expected callable, got {condition}'
    assert hasattr(inner, '__punit_decorator')


# --- Runner: _get_skip_condition ---


@fact
def check_get_skip_condition_returns_true_for_bare_skip():
    """_get_skip_condition returns True for bare @skip()."""

    @skip()
    def inner() -> None:
        pass

    result = _get_skip_condition(inner)
    assert result is True, f'Expected True, got {result}'


@fact
def check_get_skip_condition_returns_true_for_skip_true():
    """_get_skip_condition returns True for @skip(True)."""

    @skip(True)
    def inner() -> None:
        pass

    result = _get_skip_condition(inner)
    assert result is True, f'Expected True, got {result}'


@fact
def check_get_skip_condition_returns_none_for_normal():
    """_get_skip_condition returns None for functions without @skip."""

    def inner() -> None:
        pass

    result = _get_skip_condition(inner)
    assert result is None, f'Expected None, got {result}'


@fact
def check_get_skip_condition_unwraps():
    """_get_skip_condition unwraps through decorators."""

    def always_false() -> bool:
        return False

    @skip(always_false)
    @_SimulatedDecorator()
    def inner() -> None:
        pass

    result = _get_skip_condition(inner)
    assert result is always_false, f'Expected callable after unwrap, got {result}'


@fact
def check_get_skip_condition_callable_type():
    """_get_skip_condition returns the callable when @skip(callable)."""

    def my_condition() -> bool:
        return False

    @skip(my_condition)
    def inner() -> None:
        pass

    result = _get_skip_condition(inner)
    assert callable(result), f'Expected callable, got {type(result)}'


# --- TestResult.is_skip ---


@fact
def check_testresult_default_is_skip_false():
    """TestResult.is_skip defaults to False."""
    result = TestResult()
    assert result.is_skip is False


@fact
def check_testresult_can_set_is_skip():
    """TestResult.is_skip can be set to True."""
    result = TestResult()
    result.is_skip = True
    assert result.is_skip is True


# --- Report: HTML ---


@fact
def check_html_report_has_skipped_indicator():
    """HTML report includes a skipped indicator for skipped tests."""
    result = TestResult()
    result.is_skip = True
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_skipped'

    html = HtmlReportGenerator().generate([result])
    assert 'skipped' in html.lower(), f'HTML missing skipped indicator: {html}'


# --- Report: JUnit ---


@fact
def check_junit_has_skipped_element():
    """JUnit report emits <skipped /> for skipped tests."""
    result = TestResult()
    result.is_skip = True
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_skipped'
    result.start_time = 100.0
    result.stop_time = 101.0

    xml_str = JUnitReportGenerator().generate([result])
    root = et.fromstring(xml_str.encode())
    tc = root.find('.//testcase')
    assert tc is not None, 'JUnit test case element not found'
    skipped = tc.find('skipped')
    assert skipped is not None, f'JUnit missing <skipped /> element: {xml_str}'


@fact
def check_junit_no_skipped_for_normal():
    """JUnit does not emit <skipped /> for normal passing tests."""
    result = TestResult()
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_normal'
    result.start_time = 100.0
    result.stop_time = 101.0

    xml_str = JUnitReportGenerator().generate([result])
    root = et.fromstring(xml_str.encode())
    tc = root.find('.//testcase')
    assert tc is not None, 'JUnit test case element not found'
    skipped = tc.find('skipped')
    assert skipped is None, 'JUnit should not have <skipped /> for normal test'


# --- Report: JSON ---


@fact
def check_json_has_skip_status():
    """JSON report includes status='skip' for skipped tests."""
    result = TestResult()
    result.is_skip = True
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_skipped'

    data = json.loads(JsonReportGenerator().generate([result]))
    assert len(data) == 1
    assert data[0]['status'] == 'skip', f'Missing skip status: {data}'


@fact
def check_json_no_skip_status_on_normal():
    """JSON does not include status='skip' for normal tests."""
    result = TestResult()
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_normal'

    data = json.loads(JsonReportGenerator().generate([result]))
    assert data[0]['status'] == 'pass', f'Normal test should have pass status: {data}'
