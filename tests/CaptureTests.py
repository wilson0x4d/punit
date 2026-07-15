# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import sys
from punit import fact
from punit.TestResult import TextIOCapture


@fact
def captures_stdout() -> None:
    capture = TextIOCapture(sys.stdout, False)
    sys.stdout = capture
    print('stdout-test')
    assert capture.output == 'stdout-test\n'


@fact
def captures_stderr() -> None:
    capture = TextIOCapture(sys.stderr, False)
    sys.stderr = capture
    print('stderr-test', file=sys.stderr)
    assert capture.output == 'stderr-test\n'


@fact
def captures_stdout_and_stderr() -> None:
    capture1 = TextIOCapture(sys.stdout, False)
    sys.stdout = capture1
    capture2 = TextIOCapture(sys.stderr, False)
    sys.stderr = capture2
    print('stdout-test', file=sys.stdout)
    print('stderr-test', file=sys.stderr)
    assert capture1.output == 'stdout-test\n'
    assert capture2.output == 'stderr-test\n'


@fact
def isatty_delegates_to_target() -> None:
    capture = TextIOCapture(sys.stdout, False)
    assert capture.isatty() == sys.stdout.isatty()


@fact
def flush_is_noop_on_quiet() -> None:
    capture = TextIOCapture(sys.stdout, True)
    # Should not raise even though quiet mode
    capture.flush()
    assert capture.output is None
