# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from .assertions import *
from .facts import *
from .theories import *
from .traits import *


__version__ = '0.0.0'
__commit__ = '0abc123'
__all__ = [
    '__version__', '__commit__',
    'assertions',
    'collections', 'exceptions', 'strings',
    'facts',
    'fact',
    'metadata',
    'theories',
    'theory', 'inlinedata',
    'traits',
    'trait'
]
