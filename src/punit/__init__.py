# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""pUnit -- a modernized unit-testing framework for Python."""

from .assertions import collections, exceptions, numeric, strings
from .assertions.exceptions import raises
from .assertions.numeric import approx
from .facts import fact
from .mocks.mock import Mock
from .results import fails
from .setups import Setup, setup
from .conditions import skip
from .teardowns import Teardown, teardown
from .theories import theory, inlinedata
from .traits import trait
from .sync import synchronous
from .concurrent import ConcurrentPool

from . import mocks

__version__ = '0.0.0'
__commit__ = '0abc123'
__all__ = [
    '__version__', '__commit__',
    'assertions',
    'collections',
    'exceptions', 'raises',
    'mocks', 'Mock',
    'numeric', 'approx',
    'strings',
    'fact',
    'setup', 'Setup',
    'teardown', 'Teardown',
    'theory', 'inlinedata',
    'trait',
    'fails',
    'skip',
    'synchronous',
    'ConcurrentPool',
]
