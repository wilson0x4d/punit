# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Sequence
from punit import collections
from punit import theory, inlinedata


@theory
@inlinedata('Values Match', [1, 2, 3], [1, 2, 3], True)
@inlinedata('Values Do Not Match', [1, 1, 1], [2, 2, 2], False)
@inlinedata('Sizes Differ', [1], [2, 3], False)
@inlinedata('Left Is None', None, [1], False)
@inlinedata('Right Is None', [1], None, False)
@inlinedata('Both Is None', None, None, True)
def are_same_when_lists(when: str, a: list[Any] | None, b: list[Any] | None, then: bool):
    assert a is None or isinstance(a, list)
    assert b is None or isinstance(b, list)
    assert then == collections.are_same(a, b), when


@theory
@inlinedata('Values Match', {1, 2, 3}, {1, 2, 3}, True)
@inlinedata('Values Do Not Match', {1, 1, 1}, {2, 2, 2}, False)
@inlinedata('Sizes Differ', {1}, {2, 3}, False)
@inlinedata('Left Is None', None, {1}, False)
@inlinedata('Right Is None', {1}, None, False)
@inlinedata('Both Is None', None, None, True)
def are_same_when_sets(when: str, a: set[Any] | None, b: set[Any] | None, then: bool):
    assert a is None or isinstance(a, set)
    assert b is None or isinstance(b, set)
    assert then == collections.are_same(a, b), when


@theory
@inlinedata('Values Match', (1, 2, 3), (1, 2, 3), True)
@inlinedata('Values Do Not Match', (1, 1, 1), (2, 2, 2), False)
@inlinedata('Sizes Differ', (1,), (2, 3), False)
@inlinedata('Left Is None', None, (1,), False)
@inlinedata('Right Is None', (1,), None, False)
@inlinedata('Both Is None', None, None, True)
def are_same_when_tuples(when: str, a: tuple[Any] | None, b: tuple[Any] | None, then: bool):
    assert a is None or isinstance(a, tuple)
    assert b is None or isinstance(b, tuple)
    assert then == collections.are_same(a, b), when


@theory
@inlinedata('Values Match', {'a': 1, 'b': 2, 'c': 3}, {'a': 1, 'b': 2, 'c': 3}, True)
@inlinedata('Nested Values Match', {'a': {'b': 2, 'c': 3}}, {'a': {'b': 2, 'c': 3}}, True)
@inlinedata('Values Do Not Match', {'a': 1, 'b': 1, 'c': 1}, {'a': 2, 'b': 2, 'c': 2}, False)
@inlinedata('Nested Values Do Not Match', {'a': {'b': 2, 'c': 3}}, {'a': {'b': 4, 'c': 5}}, False)
@inlinedata('Sizes Differ', {'a': 1}, {'a': 2, 'b': 3}, False)
@inlinedata('Left Is None', None, {'a': 1}, False)
@inlinedata('Right Is None', {'a': 1}, None, False)
@inlinedata('Both Is None', None, None, True)
def are_same_when_dictionaries(when: str, a: dict[Any, Any], b: dict[Any, Any], then: bool):
    assert a is None or isinstance(a, dict)
    assert b is None or isinstance(b, dict)
    assert then == collections.are_same(a, b), when


@theory
@inlinedata('For Dictionaries', {'b': 2, 'a': 1, 'c': 3}, {'a': 1, 'b': 2, 'c': 3}, True)
@inlinedata('For Tuples', (1, 3, 2), (1, 2, 3), True)
@inlinedata('For Lists', [2, 3, 1], [1, 2, 3], True)
def are_same_with_sort(when: str, a: Sequence[Any], b: Sequence[Any], then: bool):
    assert then == collections.are_same(a, b, sort=True), when


@theory
@inlinedata('None with no constraints', None, 0, True)
@inlinedata('None + non-zero constraint', None, 1, False)
def has_length_none_value(when: str, sequence: Sequence[Any], expected: int, then: bool):
    assert then == collections.has_length(sequence, expected), when


@theory
@inlinedata('Empty with no constraints (exact)', [], 0, True)
@inlinedata('Empty + non-zero constraint', [], 1, False)
def has_length_empty_value(when: str, sequence: Sequence[Any], expected: int, then: bool):
    assert then == collections.has_length(sequence, expected), when


@theory
@inlinedata('Single-element list matches', [1], 1, True)
@inlinedata('Single-element list below expected', [1], 2, False)
@inlinedata('Multi-element list matches', [1, 2, 3], 3, True)
@inlinedata('Multi-element list below expected (4)', [1, 2, 3], 4, False)
@inlinedata('Multi-element list above expected (2 as min)', [1, 2, 3], 2, True)
@inlinedata('Empty tuple matches zero', (), 0, True)
@inlinedata('Tuple matches expected', (1, 2), 2, True)
@inlinedata('Range matches expected', range(5), 5, True)
def has_length_value(when: str, sequence: Sequence[Any], expected: int, then: bool):
    assert then == collections.has_length(sequence, min=expected), when


@theory
@inlinedata('Sequence Is None', None, True)
@inlinedata('Sequence Is Not None And Is Empty', [], True)
@inlinedata('Sequence Is Not None And Is Not Empty', [1], False)
def is_none_or_empty(when: str, sequence: Sequence[Any], then: bool):
    assert then == collections.is_none_or_empty(sequence), f'when:{when}'
