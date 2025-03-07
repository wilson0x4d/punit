# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Optional
from src.assertions import *
from src.facts import *
from src.theories import *

@theory
@inlinedata('Values Match', 'hello', 'hello', True)
@inlinedata('Case Differs', 'Hello', 'hello', False)
@inlinedata('Values Do Not Match', 'hello', 'world', False)
@inlinedata('Left Is None', None, 'hello', False)
@inlinedata('Right Is None', 'hello', None, False)
@inlinedata('Both Are None', None, None, True)
def areSame(when: str, a: Optional[str], b: Optional[str], then: bool):
    assert then == strings.areSame(a, b)

@theory
@inlinedata('String Is None', None, True)
@inlinedata('String Is Empty', '', True)
@inlinedata('String Is Not Empty', ' \t', False)
def isNoneOrEmpty(when: str, value: Optional[str], then: bool):
    assert then == strings.isNoneOrEmpty(value)

@theory
@inlinedata('String Is None', None, True)
@inlinedata('String Is Empty', '', True)
@inlinedata('String Is Whitespace', ' \t', True)
@inlinedata('String Is Not Whitespace', 'hello', False)
def isNoneOrWhitespace(when: str, value: Optional[str], then: bool):
    assert then == strings.isNoneOrWhitespace(value)
