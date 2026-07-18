# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Verify output capture works in both serial and concurrent execution paths.

The new design uses a persistent global ``_TextIOCapture`` for stdout/stderr
that dispatches writes to a ``TextIOReceiver`` via a contextvars.ContextVar.
When ``TestResult.capture_output()`` is called, receivers are set on the
contextvar.  Writes to ``sys.stdout`` (which points to the persistent
capture) are routed to the receiver for the current task.
"""

import sys

from punit import fact
from punit.TestResult import TestResult


# --------------------------------------------------------------
# Serial (non-concurrent path)
# --------------------------------------------------------------

@fact
def serial_captures_stdout() -> None:
    result = TestResult()
    result.capture_output()
    print('serial-stdout-test')
    assert result.stdout == 'serial-stdout-test\n'
    result.release_output()


@fact
def serial_captures_stderr() -> None:
    result = TestResult()
    result.capture_output()
    print('serial-stderr-test', file=sys.stderr)
    assert result.stderr == 'serial-stderr-test\n'
    result.release_output()


@fact
def serial_captures_both_stdout_and_stderr() -> None:
    result = TestResult()
    result.capture_output()
    print('serial-both-stdout')
    print('serial-both-stderr', file=sys.stderr)
    assert result.stdout == 'serial-both-stdout\n'
    assert result.stderr == 'serial-both-stderr\n'
    result.release_output()


@fact
def serial_release_output_stops_receiving() -> None:
    """Verify that after release_output, text is no longer captured."""
    result = TestResult()
    result.capture_output()
    print('before-release')
    assert result.stdout == 'before-release\n'
    result.release_output()
    # After release_output, the receiver is None so stdout is None too
    assert result.stdout is None


@fact
def serial_captures_multiple_print_calls() -> None:
    result = TestResult()
    result.capture_output()
    print('line1')
    print('line2')
    print('line3')
    assert result.stdout == 'line1\nline2\nline3\n'
    result.release_output()


@fact
def stdout_is_none_without_capture() -> None:
    result = TestResult()
    assert result.stdout is None
    assert result.stderr is None


@fact
def release_output_clears_internal_references() -> None:
    """Verify release_output resets internal state after capture completes."""
    result = TestResult()
    result.capture_output()
    print('test')
    captured = result.stdout  # save before release
    assert captured == 'test\n'
    result.release_output()
    assert result.stdout is None
    assert result.stderr is None
