# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from .assertions import collections, exceptions, strings
from .facts import fact
from .theories import theory, inlinedata
from .traits import trait

from .assertions.exceptions import raises


__version__ = '0.0.0'
__commit__ = '0abc123'
__all__ = [
    '__version__', '__commit__',
    'assertions',
    'collections', 'exceptions', 'strings',
    'fact',
    'metadata',
    'raises',
    'theory', 'inlinedata',
    'trait'
]
