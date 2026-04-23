# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact, theory, inlinedata


@fact
def donotrun_one() -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@fact
def two_donotrun() -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@fact
def three_donotrun_three() -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@theory
@inlinedata('foo')
def donotrun_four(bar:str) -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@theory
@inlinedata('foo')
def five_donotrun(bar:str) -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover

@theory
@inlinedata('foo')
def six_donotrun_six(bar:str) -> None:
    raise Exception('this test should have been excluded by `filters-file.txt`.') # pragma: no cover
