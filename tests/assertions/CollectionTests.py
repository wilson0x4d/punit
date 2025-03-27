# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Sequence
from punit.assertions import *
from punit.facts import *
from punit.theories import *

@theory
@inlinedata('Values Match', [1,2,3], [1,2,3], True)
@inlinedata('Values Do Not Match', [1,1,1], [2,2,2], False)
@inlinedata('Sizes Differ', [1], [2,3], False)
@inlinedata('Left Is None', None, [1], False)
@inlinedata('Right Is None', [1], None, False)
@inlinedata('Both Is None', None, None, True)
def areSameWhenLists(when:str, a:Sequence, b:Sequence, then:bool):
    assert then == collections.areSame(a, b), f'when:{when}'

@theory
@inlinedata('Values Match', (1,2,3), (1,2,3), True)
@inlinedata('Values Do Not Match', (1,1,1), (2,2,2), False)
@inlinedata('Sizes Differ', (1,), (2,3), False)
@inlinedata('Left Is None', None, (1,), False)
@inlinedata('Right Is None', (1,), None, False)
@inlinedata('Both Is None', None, None, True)
def areSameWhenTuples(when:str, a:Sequence, b:Sequence, then:bool):
    assert then == collections.areSame(a, b), f'when:{when}'

@theory
@inlinedata('Values Match', {'a':1,'b':2,'c':3}, {'a':1,'b':2,'c':3}, True)
@inlinedata('Nested Values Match', {'a':{'b':2,'c':3}}, {'a':{'b':2,'c':3}}, True)
@inlinedata('Values Do Not Match', {'a':1,'b':1,'c':1}, {'a':2,'b':2,'c':2}, False)
@inlinedata('Nested Values Do Not Match', {'a':{'b':2,'c':3}}, {'a':{'b':4,'c':5}}, False)
@inlinedata('Sizes Differ', {'a':1}, {'a':2,'b':3}, False)
@inlinedata('Left Is None', None, {'a':1}, False)
@inlinedata('Right Is None', {'a':1}, None, False)
@inlinedata('Both Is None', None, None, True)
def areSameWhenDictionaries(when:str, a:Sequence, b:Sequence, then:bool):
    assert then == collections.areSame(a, b), f'when:{when}'

@theory
@inlinedata('For Dictionaries', {'b':2,'a':1,'c':3}, {'a':1,'b':2,'c':3}, True)
@inlinedata('For Tuples', (1,3,2), (1,2,3), True)
@inlinedata('For Lists', [2,3,1], [1,2,3], True)
def areSameWithSort(when:str, a:Sequence, b:Sequence, then:bool):
    assert then == collections.areSame(a, b, sort=True), f'when:{when}'

@theory
@inlinedata('Sequence Is None', None, 0, True)
@inlinedata('Sequence Is Empty', [], 0, True)
@inlinedata('Sequence Is Not None And Has Length', [1], 1, True)
@inlinedata('Sequence Is Not Empty And Has Length', [1], 1, True)
@inlinedata('Sequence Is Not None And Has No Length', [1], None, False)
@inlinedata('Sequence Is Not Empty And Has No Length', [1], None, False)
def hasLength(when:str, sequence:Sequence, expected:int, then:bool):
    assert then == collections.hasLength(sequence, expected), f'when:{when}'

@theory
@inlinedata('Sequence Is None', None, True)
@inlinedata('Sequence Is Not None And Is Empty', [], True)
@inlinedata('Sequence Is Not None And Is Not Empty', [1], False)
def isNoneOrEmpty(when:str, sequence:Sequence, then:bool):
    assert then == collections.isNoneOrEmpty(sequence), f'when:{when}'
