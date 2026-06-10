# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

from typing import Callable, Optional


class Trait:
    """A categorical name/value pair associated with a test.

    Traits can be used to group tests together for inclusion or exclusion during
    execution, allowing more flexible testing strategies. Common use-cases include:

    * Grouping by area of functionality (e.g., UI, business logic)
    * Grouping by dependencies (e.g., integration, mock)
    * Flagging tests as slow or flaky to control execution order

    Example
    -------

    .. code-block:: python

        from punit import fact, trait

        @fact
        @trait('category', 'ui')
        def test_ui_feature():
            assert True

    """

    __name: str
    __value: str | None

    def __init__(self, name: str, value: Optional[str] = None):
        self.__name = name
        self.__value = value

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> str | None:
        return self.__value


def trait(name: str, value: Optional[str] = None) -> Callable:
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
    def wrapper(target: Callable) -> Callable:
        from .TraitManager import TraitManager
        trait = Trait(name, value)
        TraitManager.instance().put(target, trait)
        return target
    return wrapper
