# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Sequence
from src.assertions import *
from src.facts import *
from src.theories import *

@theory
@inlinedata('Values Match', [1,2,3], [1,2,3], True)
@inlinedata('Values Do Not Match', [1,1,1], [2,2,2], False)
@inlinedata('Sizes Differ', [1], [2,3], False)
@inlinedata('Left Is None', None, [1], False)
@inlinedata('Right Is None', [1], None, False)
@inlinedata('Both Is None', None, None, True)
def areSame(when:str, a:Sequence, b:Sequence, then:bool):
    assert then == collections.areSame(a, b)
