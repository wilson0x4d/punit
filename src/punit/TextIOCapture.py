# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Module-level TextIO output capture for concurrent test execution.

When tests run concurrently on a single thread, multiple coroutines write to
``sys.stdout`` / ``sys.stderr`` simultaneously and interleave or clobber each
other's captures.  This module fixes that by:

1. Creating two persistent ``_TextIOCapture`` instances that replace
   ``sys.stdout`` / ``sys.stderr`` via ``setup_global_text_io()``.

2. Using a ``contextvars.ContextVar`` to track the active
   ``TextIOReceiver`` pair for the current task.

3. Dispatching every ``write()`` on the persistent capture to the correct
   receiver based on the contextvar so that each test's output is isolated
   to its own ``TestResult``.

The ``quiet`` passthrough to the original stream is a process-wide concern
controlled by the ``_TextIOCapture``.  The receiver only accumulates text.
"""

from __future__ import annotations

import contextvars
import io
import sys
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Context variable – stores the active receivers for the current task
# ---------------------------------------------------------------------------

_text_io_receivers_ctx: Any = contextvars.ContextVar(
    'text_io_receivers', default=None
)


class TextIOReceiver:
    """
    String buffer for a single test's stdout or stderr.

    The persistent ``_TextIOCapture`` dispatches all writes to whichever
    receiver is active in the current task's context (resolved via the
    contextvars.ContextVar).  Each test gets its own receiver so output
    is never mixed between concurrent tests.

    The receiver knows nothing about ``quiet`` – it simply accumulates text
    into its ``output`` attribute.  Passthrough to the original stream is
    the responsibility of the persistent ``_TextIOCapture``.
    """

    def __init__(self) -> None:
        self.output: Optional[str] = None

    def init(self) -> None:
        """Re-initialise the receiver for a new test."""
        self.output = ''


class _TextIOCapture(io.TextIOBase):
    """
    Persistent ``TextIOBase`` that dispatches writes to the correct
    ``TextIOReceiver`` via the contextvars.ContextVar.

    Two instances exist globally (one for stdout, one for stderr).  After
    ``setup_global_text_io()`` they replace ``sys.stdout`` / ``sys.stderr``.
    Every ``write()`` checks the contextvars.ContextVar, finds the active
    receiver for the current task, and dispatches the text to it.

    When ``quiet`` is ``True``, writes are only stored in the receiver.
    When ``quiet`` is ``False``, text is written to the original stream
    so the terminal still sees everything.  The receiver always gets
    collected regardless of quiet state.
    """

    __slots__ = ('__quiet', '__is_stdout')

    def __init__(self, quiet: bool = False, is_stdout: bool = True) -> None:
        self.__quiet = quiet
        self.__is_stdout = is_stdout

    @property
    def quiet(self) -> bool:
        return self.__quiet

    @quiet.setter
    def quiet(self, value: bool) -> None:
        self.__quiet = value

    def __enter__(self) -> '_TextIOCapture':
        return self

    def __exit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        pass

    @property
    def closed(self) -> bool:
        return False

    def close(self) -> None:
        pass

    def fileno(self) -> int:
        _sys_target: Any = sys.__stdout__ if self.__is_stdout else sys.__stderr__
        return _sys_target.fileno()  # type: ignore[union-attr]

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        return False

    def read(self, n: int | None = -1, /) -> str:
        return ''

    def reconfigure(
        self, *, encoding: str | None = None, errors: str | None = None, newline: str | None = None, **kwargs: Any
    ) -> io.TextIOBase:
        return self

    def writable(self) -> bool:
        return True

    def write(self, text: str) -> int:
        # Dispatch to the test-receiver (if one is set on the contextvar)
        receivers = _text_io_receivers_ctx.get()
        if receivers is not None and len(receivers) == 2:
            receiver = receivers[0] if self.__is_stdout else receivers[1]
            if receiver.output is None:
                receiver.output = text
            else:
                receiver.output += text
        # Passthrough to the original stream (unless quiet)
        if not self.__quiet:
            target: Any = sys.__stdout__ if self.__is_stdout else sys.__stderr__
            if hasattr(target, 'write') and target is not None:
                target.write(text)
        return len(text)

    def is_stdout_channel(self) -> bool:
        return self.__is_stdout


# ---------------------------------------------------------------------------
# Persistent instances – created once at module import time
# ---------------------------------------------------------------------------

_PERSISTENT_STDOUT = _TextIOCapture(quiet=False, is_stdout=True)
_PERSISTENT_STDERR = _TextIOCapture(quiet=False, is_stdout=False)


def setup_global_text_io() -> None:
    """Replace ``sys.stdout`` and ``sys.stderr`` with persistent captures.

    Called once by ``TestRunner.run()`` so both serial and concurrent paths
    dispatch through the persistent capture.  After this, all writes to
    stdout/stderr go through the capture which routes to the correct
    task-local ``TextIOReceiver`` via the contextvars.ContextVar.
    """
    sys.stdout = _PERSISTENT_STDOUT
    sys.stderr = _PERSISTENT_STDERR


def _set_receivers(
    receiver_stdout: 'TextIOReceiver', receiver_stderr: 'TextIOReceiver'
) -> None:
    """Place receiver pair on the contextvars.ContextVar.

    Called by ``TestResult.capture_output()`` so the persistent capture
    routes all ``write()`` calls to these receivers.
    """
    _text_io_receivers_ctx.set((receiver_stdout, receiver_stderr))


def _clear_receivers() -> None:
    """Clear the receivers from the contextvars.ContextVar.

    Called by ``TestResult.release_output()`` so the receivers cannot
    collect writes during teardown or unexpected post-test output.
    """
    _text_io_receivers_ctx.set(None)
