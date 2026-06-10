# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact, fails, theory, inlinedata


@fact
@fails(reason='this test only exists for verifying `--filters-file.txt` functionality.')
def donotrun_one() -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@fact
@fails(reason='this test only exists for verifying `--filters-file.txt` functionality.')
def donotrun() -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@fact
@fails(reason='this test only exists for verifying `--filters-file.txt` functionality.')
def three_donotrun_three() -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@theory
@inlinedata('aaa')
@fails(reason='this test only exists for verifying `--filters-file.txt` functionality.')
def donotrun_four(bar:str) -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@theory
@inlinedata('bbb')
@fails(reason='this test only exists for verifying `--filters-file.txt` functionality.')
def five_donotrun(bar:str) -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@theory
@inlinedata('ccc')
@fails(reason='this test only exists for verifying `--filters-file.txt` functionality.')
def donotrun_six(bar:str) -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover
