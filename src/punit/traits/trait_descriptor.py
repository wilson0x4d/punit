# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Optional


class TraitDescriptor:
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
