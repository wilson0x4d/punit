# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Optional
from punit import strings
from punit import theory, inlinedata


@theory
@inlinedata('Values Match', 'hello', 'hello', True)
@inlinedata('Case Differs', 'Hello', 'hello', False)
@inlinedata('Values Do Not Match', 'hello', 'world', False)
@inlinedata('Left Is None', None, 'hello', False)
@inlinedata('Right Is None', 'hello', None, False)
@inlinedata('Both Are None', None, None, True)
@inlinedata('Lengths Differ', 'two', 'three', False)
def are_same(when: str, a: Optional[str], b: Optional[str], then: bool):
    assert then == strings.areSame(a, b)


@theory
@inlinedata('String Is None', None, True)
@inlinedata('String Is Empty', '', True)
@inlinedata('String Is Not Empty', ' \t', False)
def is_none_or_empty(when: str, value: Optional[str], then: bool):
    assert then == strings.isNoneOrEmpty(value)


@theory
@inlinedata('String Is None', None, True)
@inlinedata('String Is Empty', '', True)
@inlinedata('String Is Whitespace', ' \t', True)
@inlinedata('String Is Not Whitespace', 'hello', False)
def is_none_or_whitespace(when: str, value: Optional[str], then: bool):
    assert then == strings.isNoneOrWhitespace(value)


@theory
@inlinedata('None with no constraints', None, True, None, None)
@inlinedata('None + min set to 1', None, False, 1, None)
@inlinedata('None + max set to 3', None, False, None, 3)
@inlinedata('None + min=max set to 3', None, False, 3, 3)
@inlinedata('None + min=0,max=0 (falsy)', None, True, 0, 0)
def has_length_none_value(when: str, value: Optional[str], expected: bool, min: Optional[int] = None, max: Optional[int] = None):
    assert expected == strings.has_length(value, min=min, max=max), when


@theory
@inlinedata('Empty with no constraints (no check made)', '', False, None, None)
@inlinedata('Empty + only min=0', '', True, 0, None)
@inlinedata('Empty + only max=0', '', True, None, 0)
@inlinedata('Empty + min=0,max=0', '', True, 0, 0)
@inlinedata('Empty + min>0 (1)', '', False, 1, None)
def has_length_empty_value(when: str, value: str, expected: bool, min: Optional[int] = None, max: Optional[int] = None):
    assert expected == strings.has_length(value, min=min, max=max), when


@theory
@inlinedata('Len=2 + no constraints', 'ab', False, None, None)
@inlinedata('Len=2 + only min=1', 'ab', True, 1, None)
@inlinedata('Len=2 + only max=3', 'ab', True, None, 3)
@inlinedata('Len=2 + min=max=2 (exact)', 'ab', True, 2, 2)
@inlinedata('Len=2 + in range [1,3]', 'ab', True, 1, 3)
@inlinedata('Len=2 + below min (3)', 'ab', False, 3, None)
@inlinedata('Len=2 + above max (1)', 'ab', False, None, 1)
@inlinedata('Len=3 + exactly at min (3)', 'abc', True, 3, None)
@inlinedata('Len=3 + exactly at max (3)', 'abc', True, None, 3)
@inlinedata('Len=3 + one above min (2)', 'abc', True, 2, None)
@inlinedata('Len=3 + one below max (4)', 'abc', True, None, 4)
@inlinedata('Len=3 + min>len (4)', 'abc', False, 4, None)
@inlinedata('Len=3 + max<len (2)', 'abc', False, None, 2)
@inlinedata('Len=3 + in range [1,5]', 'abc', True, 1, 5)
@inlinedata('Len=3 + at range [2,4]', 'abc', True, 2, 4)
def has_length_value(when: str, value: str, expected: bool, min: Optional[int] = None, max: Optional[int] = None):
    assert expected == strings.has_length(value, min=min, max=max), when
