# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""pUnit -- a modernized unit-testing framework for Python."""

from .assertions import collections, exceptions, numeric, strings
from .assertions.exceptions import raises
from .assertions.numeric import approx
from .facts import fact
from .lifecycle import Lifecycle, lifecycle
from .mocks.mock import Mock
from .results import fails
from .setups import setup
from .conditions import skip
from .teardowns import teardown
from .theories import theory, inlinedata
from .traits import trait
from .parallelism import parallel, sequential

from . import mocks

__version__ = '0.0.0'
__commit__ = '0abc123'
__all__ = [
    '__version__', '__commit__',
    'assertions',
    'collections',
    'exceptions', 'raises',
    'lifecycle', 'Lifecycle',
    'mocks', 'Mock',
    'numeric', 'approx',
    'strings',
    'fact',
    'setup',
    'teardown',
    'theory', 'inlinedata',
    'trait',
    'fails',
    'skip',
    'sequential',
    'parallel',
]
