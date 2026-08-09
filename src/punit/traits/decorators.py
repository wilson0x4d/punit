# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Callable, Optional


def trait(name: str, value: Optional[str] = None) -> Callable[..., Any]:
    """Decorates a Fact or Theory as having a specific Trait.

    Once applied, the trait can be referenced during test execution to include or
    exclude the test. The ``--trait`` flag accepts several forms:

    * ``!trait_name`` -- exclude tests with this trait
    * ``trait_name=value`` -- run only tests matching both name and value
    * Multiple ``--trait`` flags match any (OR logic)
    * Exclusions take priority over inclusions

    Args:
        name: The categorical trait name (e.g., 'integration', 'category')
        value: Optional trait value for more specific matching (e.g., 'redis')

    Returns:
        A wrapper that attaches the trait to the target via TraitManager

    Example
    -------

    .. code-block:: python

        from punit import theory, inlinedata, trait

        @theory
        @inlinedata(0, 1, 1)
        @trait('integration', 'redis')
        @trait('category', 'api')
        def myFunction(a, b, c):
            assert a + b == c

    Note: The ``@trait`` decorator can be applied more than once to a single test.

    """
    def wrapper(target: Callable[..., Any]) -> Callable[..., Any]:
        from .trait_descriptor import TraitDescriptor
        from .trait_manager import TraitManager
        trait = TraitDescriptor(name, value)
        TraitManager.instance().put(target, trait)
        return target
    return wrapper
