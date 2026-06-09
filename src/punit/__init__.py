# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from .assertions import collections, exceptions, numeric, strings
from .facts import fact
from .setups import Setup, setup
from .teardowns import Teardown, teardown
from .theories import theory, inlinedata
from .traits import trait

from .assertions.exceptions import raises
from .assertions.numeric import approx


__version__ = '0.0.0'
__commit__ = '0abc123'
__all__ = [
    '__version__', '__commit__',
    'assertions',
    'collections',
    'exceptions', 'raises',
    'numeric', 'approx',
    'strings',
    'fact',
    'metadata',
    'setup', 'Setup',
    'teardown', 'Teardown',
    'theory', 'inlinedata',
    'trait'
]
