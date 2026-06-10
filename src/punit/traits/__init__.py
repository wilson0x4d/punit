# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Traits are categorical name/value pairs associated with a test.

Traits can be used to group tests together for inclusion or exclusion during
execution, enabling more flexible testing strategies. Common use-cases include:

* Grouping by area of functionality (e.g., UI, business logic)
* Grouping by dependencies (e.g., integration, mock)
* Flagging tests as slow or flaky to control execution order

Trait filtering with ``--trait`` supports several forms:

* ``!trait_name`` -- exclude tests with this trait
* ``trait_name=value`` -- run only tests matching both name and value
* Multiple ``--trait`` flags match any (OR logic)
* Exclusions take priority over inclusions

Example
-------

.. code-block:: python

    from punit import theory, inlinedata, trait

    @theory
    @inlinedata(0, 1, 1)
    @trait('integration', 'redis')
    @trait('category', 'api')
    def test_api_query(a, b, c):
        assert a + b == c

.. code-block:: bash

    # exclude integration tests
    python3 -m punit --trait '!integration'

    # run only integration=redis tests
    python3 -m punit --trait integration=redis

"""

from .TraitManager import TraitManager
from .Trait import Trait, trait


__all__ = [
    'TraitManager',
    'Trait', 'trait'
]
