# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for the @fails decorator and its runner/report integration."""

import inspect
import json
import xml.etree.ElementTree as et  # type: ignore[import-untyped]
from typing import Any, Callable

from punit import fact, fails
from punit.runner import _get_fails_reason
from punit.TestResult import TestResult


@fact
def check_basic_attribute():
    """@fails(reason='...') sets __punit_fails_reason on the unwrapped target."""

    @fails(reason='bug #42')
    def inner() -> None:  # type: ignore[func-returns-value]
        pass

    assert hasattr(inner, '__punit_fails_reason'), 'Attribute missing'
    reason = getattr(inner, '__punit_fails_reason', None)
    assert reason == 'bug #42', f'Wrong reason: {reason}'


@fact
def check_unwraps_through_fact():
    """Stacking @fails below @fact sets __punit_fails_reason on the unwrapped target."""

    result = inspect.unwrap(_test_func_stacked_under_fact)
    assert hasattr(result, '__punit_fails_reason'), 'Attribute not set through @fact'
    assert getattr(result, '__punit_fails_reason') == 'order reversed'


@fact
def check_unwraps_through_theory_inlinedata():
    """Stacking @fails below @theory + @inlinedata sets __punit_fails_reason on the unwrapped target."""

    result = inspect.unwrap(_test_func_stacked_under_theory)
    assert hasattr(result, '__punit_fails_reason'), 'Attribute lost through stacking'
    assert getattr(result, '__punit_fails_reason') == 'edge case'


@fact
def check_returns_original_callable():
    """@fails returns the original target unchanged."""

    def my_func() -> int:  # type: ignore[func-returns-value]
        return 42

    decorated = fails(reason='x')(my_func)
    assert decorated is my_func, '@fails should return the original function'


@fact
def check_non_function_raises():
    """@fails on a non-function raises an exception."""
    try:
        @fails(reason='not a function')
        class MyClass:  # type: ignore[misc, no-redef]
            pass
        assert False, 'Should have raised'
    except Exception as e:
        assert 'functions and methods' in str(e), f'Wrong error: {e}'


@fact
def check_double_fails_raises():
    """Stacking two @fails decorators raises."""
    try:
        @fails(reason='first')
        @fails(reason='second')
        def inner() -> None:  # type: ignore[func-returns-value]
            pass
        assert False, 'Should have raised'
    except Exception as e:
        assert 'already marked' in str(e), f'Wrong error: {e}'


@fact
def check_fails_below_fact_raises():
    """Stacking @fails below another pUnit decorator raises."""

    class DummyDecorator:  # type: ignore[no-redef]
        """Simulates a decorator that also sets __punit_decorator."""

        def __call__(self, func: Callable) -> Callable:  # type: ignore[misc]
            if not hasattr(func, '__punit_decorator'):
                setattr(func, '__punit_decorator', '@dummy')
            return func

    try:
        @fails(reason='alone')
        @DummyDecorator()
        def inner() -> None:  # type: ignore[func-returns-value]
            pass
        assert False, 'Should have raised'
    except Exception as e:
        assert '@dummy' in str(e), f'Wrong error (missing decorator name): {e}'


@fact
def check_runner_get_fails_reason():
    """Verify _get_fails_reason works against targets."""

    @fails(reason='runner test reason')
    def inner() -> None:  # type: ignore[func-returns-value]
        pass

    result = _get_fails_reason(inner)
    assert result == 'runner test reason', f'Got {result}'


@fact
def check_inversion_of_failing_test():
    """A failing test with @fails should report is_success=True (inverted)."""

    # Simulate what the runner does for a test that failed:
    # 1. Test body raised → result.is_success = False
    # 2. @fails detected → result.is_expected_failure = True
    # 3. Inversion → result.is_success = not False = True
    class FakeResult:
        is_success: bool
        expected_failure_reason: str | None = None

    result = FakeResult()
    result.is_success = False  # simulated: test body raised an exception

    # Simulate @fails being present on the target
    @fails(reason='simulated bug')
    def failing_target() -> None:  # type: ignore[func-returns-value]
        raise AssertionError('intentional failure')

    fails_reason = _get_fails_reason(failing_target)
    if fails_reason is not None:
        result.expected_failure_reason = fails_reason
        result.is_success = not result.is_success  # Inversion

    assert result.is_success is True, f'Expected inversion to pass, got is_success={result.is_success}'
    assert result.expected_failure_reason == 'simulated bug'


@fact
def check_inversion_of_passing_test():
    """A passing test with @fails should report is_success=False (inverted as regression)."""

    class FakeResult:
        is_success: bool
        expected_failure_reason: str | None = None

    result = FakeResult()
    result.is_success = True  # simulated: test body passed

    @fails(reason='unexpected fix')
    def passing_target() -> None:  # type: ignore[func-returns-value]
        pass  # This passes!

    fails_reason = _get_fails_reason(passing_target)
    if fails_reason is not None:
        result.expected_failure_reason = fails_reason
        result.is_success = not result.is_success  # Inversion

    assert result.is_success is not True, f'Expected inversion to fail (regression), got is_success={result.is_success}'
    assert result.expected_failure_reason == 'unexpected fix'


@fact
def check_no_inversion_without_fails():
    """A normal test without @fails should keep its original is_success value."""

    class FakeResult:
        is_success: bool
        expected_failure_reason: str | None = None

    result = FakeResult()
    result.is_success = False  # simulated failure

    def normal_target() -> None:  # type: ignore[func-returns-value]
        raise AssertionError('normal failure')

    fails_reason = _get_fails_reason(normal_target)
    if fails_reason is not None:
        result.expected_failure_reason = fails_reason
        result.is_success = not result.is_success

    assert result.is_success is False, 'Result should NOT be inverted without @fails'


@fact
def check_report_html_shows_expected_failure_reason():
    """HTML report includes the expected-failure reason text."""
    from punit.reports.HtmlReportGenerator import HtmlReportGenerator

    result = TestResult()
    result.is_success = False
    result.expected_failure_reason = 'expected bug #7'
    result.module_name = 'mod'
    result.test_name = 'test_foo'

    html = HtmlReportGenerator().generate([result])

    assert 'expected bug #7' in html, f'HTML missing reason text: {html}'


@fact
def check_report_junit_has_expected_failure_element():
    """JUnit report includes <expected-failure> element."""
    from punit.reports.JUnitReportGenerator import JUnitReportGenerator

    result = TestResult()
    result.is_success = False
    result.expected_failure_reason = 'junit test reason'
    result.module_name = 'mod'
    result.test_name = 'test_junit'
    result.start_time = 100.0
    result.stop_time = 101.0

    xml_str = JUnitReportGenerator().generate([result])
    root = et.fromstring(xml_str.encode())
    tc = root.find('.//testcase')
    assert tc is not None, 'JUnit test case element not found'
    ef = tc.find('expected-failure')
    assert ef is not None, 'JUnit missing expected-failure element'
    assert ef.get('reason') == 'junit test reason'


@fact
def check_report_json_includes_flag():
    """JSON report includes expected_failure boolean and reason string."""
    from punit.reports.JsonReportGenerator import JsonReportGenerator

    result = TestResult()
    result.is_success = False
    result.expected_failure_reason = 'json test reason'
    result.module_name = 'mod'
    result.test_name = 'test_json'
    result.start_time = 100.0
    result.stop_time = 101.0

    data = json.loads(JsonReportGenerator().generate([result]))
    assert len(data) == 1
    assert data[0]['status'] == 'fail'
    assert data[0].get('expected_failure') is True, f'Missing expected_failure: {data}'
    assert data[0].get('expected_failure_reason') == 'json test reason'


@fact
def check_report_no_flag_on_normal_test():
    """Report does not add expected-failure fields for normal passing tests."""
    from punit.reports.JsonReportGenerator import JsonReportGenerator

    result = TestResult()
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_normal'
    result.start_time = 100.0
    result.stop_time = 101.0

    data = json.loads(JsonReportGenerator().generate([result]))
    assert data[0]['status'] == 'pass'
    assert data[0].get('expected_failure') is None, f'Should not have expected_failure: {data}'


@fact
def check_html_no_expected_failure_for_passed():
    """HTML does not show expected-failure annotation when test passes without @fails."""
    from punit.reports.HtmlReportGenerator import HtmlReportGenerator

    result = TestResult()
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_pass'

    html = HtmlReportGenerator().generate([result])
    assert 'expected failure' not in html.lower(), f'Should not show expected-failure for passed test: {html}'


@fact
def check_html_no_expected_failure_for_failed_without_fails():
    """HTML does not show expected-failure annotation when test fails but has no @fails."""
    from punit.reports.HtmlReportGenerator import HtmlReportGenerator

    result = TestResult()
    result.is_success = False
    result.module_name = 'mod'
    result.test_name = 'test_fail'

    html = HtmlReportGenerator().generate([result])
    assert 'expected failure' not in html.lower(), f'Should not show expected-failure for failed test: {html}'


@fact
def check_junit_no_expected_failure_for_passed():
    """JUnit does not add expected-failure element for passed test without @fails."""
    from punit.reports.JUnitReportGenerator import JUnitReportGenerator

    result = TestResult()
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_pass'
    result.start_time = 100.0
    result.stop_time = 101.0

    xml_str = JUnitReportGenerator().generate([result])
    root = et.fromstring(xml_str.encode())
    tc = root.find('.//testcase')
    assert tc is not None, 'JUnit test case element not found'
    ef = tc.find('expected-failure')
    assert ef is None, 'JUnit should not have expected-failure for passed test'


@fact
def check_json_no_expected_failure_for_passed():
    """JSON does not include expected_failure key for normal passing tests."""
    from punit.reports.JsonReportGenerator import JsonReportGenerator

    result = TestResult()
    result.is_success = True
    result.module_name = 'mod'
    result.test_name = 'test_pass'
    result.start_time = 100.0
    result.stop_time = 101.0

    data = json.loads(JsonReportGenerator().generate([result]))
    assert data[0]['status'] == 'pass'
    assert 'expected_failure' not in data[0], f'Should not have expected_failure key: {data}'


@fact
def check_json_no_expected_failure_for_failed_without_fails():
    """JSON does not include expected_failure for normal failure."""
    from punit.reports.JsonReportGenerator import JsonReportGenerator

    result = TestResult()
    result.is_success = False
    result.module_name = 'mod'
    result.test_name = 'test_fail'
    result.start_time = 100.0
    result.stop_time = 101.0

    data = json.loads(JsonReportGenerator().generate([result]))
    assert data[0]['status'] == 'fail'
    assert 'expected_failure' not in data[0], f'Should not have expected_failure: {data}'


@fact
def check_report_html_shows_expected_failure_text_when_passed():
    """HTML shows '(expected failure)' when a test passes but has @fails."""
    from punit.reports.HtmlReportGenerator import HtmlReportGenerator

    result = TestResult()
    result.is_success = True
    result.expected_failure_reason = 'bug #42'
    result.module_name = 'mod'
    result.test_name = 'test_pass_with_fails'

    html = HtmlReportGenerator().generate([result])
    
    assert 'expected failure: bug #42' in html, f'Missing reason text in HTML: {html}'


@fact
def check_runner_get_fails_reason_returns_none_when_missing():
    """_get_fails_reason returns None when target has no attribute."""

    def inner() -> Any:  # type: ignore[func-returns-value]
        return True

    result = _get_fails_reason(inner)
    assert result is None, f'Expected None, got {result}'


# --- Module-level decorated functions for stacking tests ---
# These use simulators of @fact/@theory that set __punit_decorator but do NOT
# register with FactManager/TheoryManager; avoiding pUnit's discovery loop.


class _FactCapturer:  # type: ignore[no-redef]
    """Simulates @fact; sets __punit_decorator, no singleton registration."""

    def __call__(self, func: Callable) -> Callable:  # type: ignore[misc]
        if not hasattr(func, '__punit_decorator'):
            setattr(func, '__punit_decorator', '@fact')
        return func


class _TheoryCapturer:  # type: ignore[no-redef]
    """Simulates @theory; sets __punit_decorator, no singleton registration."""

    def __call__(self, func: Callable) -> Callable:  # type: ignore[misc]
        if not hasattr(func, '__punit_decorator'):
            setattr(func, '__punit_decorator', '@theory')
        return func


# Decorated at import time; attributes set for testing in aba/abb tests.
_test_func_stacked_under_fact: Callable[[], None] = (
    _FactCapturer()(fails(reason='order reversed')(lambda: None))  # type: ignore[arg-type, assignment]
)


@_TheoryCapturer()
@fails(reason='edge case')
def _test_func_stacked_under_theory(x: int = 0) -> None:  # type: ignore[func-returns-value]
    """Stacked under @theory; attribute set on this function by the decorators."""
    pass
