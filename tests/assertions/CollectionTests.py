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
def areSame(when:str, a:Sequence, b:Sequence, then:bool):
    assert then == collections.areSame(a, b)

@theory
@inlinedata('Sequence Is None', None, 0, True)
@inlinedata('Sequence Is Empty', [], 0, True)
@inlinedata('Sequence Is Not None And Has Length', [1], 1, True)
@inlinedata('Sequence Is Not Empty And Has Length', [1], 1, True)
@inlinedata('Sequence Is Not None And Has No Length', [1], None, False)
@inlinedata('Sequence Is Not Empty And Has No Length', [1], None, False)
def hasLength(when:str, sequence:Sequence, expected:int, then:bool):
    assert then == collections.hasLength(sequence, expected)

@theory
@inlinedata('Sequence Is None', None, True)
@inlinedata('Sequence Is Not None And Is Empty', [], True)
@inlinedata('Sequence Is Not None And Is Not Empty', [1], False)
def isNoneOrEmpty(when:str, sequence:Sequence, then:bool):
    assert then == collections.isNoneOrEmpty(sequence)
