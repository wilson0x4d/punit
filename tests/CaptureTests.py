# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import sys
from punit.facts import fact
from punit.TestResult import TextIOCapture

@fact
def TextIOCapture_CapturesStdOut() -> None:
    capture:TextIOCapture = TextIOCapture(sys.stdout, False)
    sys.stdout = capture
    print('stdout-test')
    assert capture.output == 'stdout-test\n'

@fact
def TextIOCapture_CapturesStdErr() -> None:
    capture:TextIOCapture = TextIOCapture(sys.stderr, False)
    sys.stderr = capture
    print('stderr-test', file=sys.stderr)
    assert capture.output == 'stderr-test\n'

@fact
def TextIOCapture_CapturesStdOutAndStdErr() -> None:
    capture1:TextIOCapture = TextIOCapture(sys.stdout, False)
    sys.stdout = capture1
    capture2:TextIOCapture = TextIOCapture(sys.stderr, False)
    sys.stderr = capture2
    print('stdout-test', file=sys.stdout)
    print('stderr-test', file=sys.stderr)
    assert capture1.output == 'stdout-test\n'
    assert capture2.output == 'stderr-test\n'
