# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Sequence

def areSame(a:Sequence[Any], b:Sequence[Any]) -> bool:
    if a is b:
        return True
    elif a is None and b is not None:
        return False
    elif a is not None and b is None:
        return False
    elif len(a) != len(b):        
        return False
    for i in range(len(a)):
        if not a[i] == b[i]:
            return False
    return True
