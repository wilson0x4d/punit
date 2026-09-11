# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

from __future__ import annotations

from typing import Any, Callable, Optional

from ..filters import FilterManager
from ..traits import TraitDescriptor, TraitManager
from .theory_descriptor import TheoryDescriptor


class TheoryManager:
    """
    Singleton that stores and manages TheoryDescriptor instances per module.

    Usage
    -----

    .. code-block:: python

        from punit.theories import TheoryManager, TheoryDescriptor

        manager = TheoryManager.instance()
        manager.put(TheoryDescriptor(my_theory_function))
        theories = manager.get('tests.my_module')

    """

    __excluded_traits: list[TraitDescriptor]
    __included_traits: list[TraitDescriptor]
    __instance: Optional['TheoryManager'] = None
    __modules: dict[str, list[TheoryDescriptor]]
    __datas: dict[Callable[..., Any], list[tuple[Any, ...]]]

    def __init__(self) -> None:
        if TheoryManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TheoryManager')  # pragma: no cover
        self.__modules = {}
        self.__datas = {}

    @staticmethod
    def instance() -> TheoryManager:
        """Return the singleton TheoryManager instance."""
        if TheoryManager.__instance is None:
            TheoryManager.__instance = TheoryManager()
        return TheoryManager.__instance

    @property
    def excluded_traits(self) -> list[TraitDescriptor]:
        """Traits to exclude when filtering theory descriptors."""
        return [] if self.__excluded_traits is None else self.__excluded_traits

    @excluded_traits.setter
    def excluded_traits(self, value: list[TraitDescriptor]) -> None:
        self.__excluded_traits = value

    @property
    def included_traits(self) -> list[TraitDescriptor]:
        """Traits to include when filtering theory descriptors."""
        return [] if self.__included_traits is None else self.__included_traits

    @included_traits.setter
    def included_traits(self, value: list[TraitDescriptor]) -> None:
        self.__included_traits = value

    def __exclude_by_traits(self, theory_descriptor: TheoryDescriptor) -> bool:
        """Return True if the theory should be excluded based on applied trait filters."""
        traits = TraitManager.instance().get(theory_descriptor.target)
        if self.excluded_traits is not None and len(self.__excluded_traits) > 0:
            for trait in self.excluded_traits:
                for L_trait in traits:
                    if trait.name == L_trait.name and (trait.value is None or (trait.value == L_trait.value)):
                        return True
        if self.included_traits is not None and len(self.included_traits) > 0:
            for trait in self.included_traits:
                for L_trait in traits:
                    if trait.name == L_trait.name and (trait.value is None or (trait.value == L_trait.value)):
                        return False
            return True
        return False

    def get(self, module_name: str) -> list[TheoryDescriptor]:
        """Return theory descriptors for *module_name*, creating an empty list if none exist."""
        l = self.__modules.get(module_name)
        if l is None:
            l = []
            self.__modules[module_name] = l
        return l

    def put(self, theory_descriptor: TheoryDescriptor) -> None:
        """Add a theory descriptor if it passes filter and trait checks."""
        filters = FilterManager.instance().filters
        matches_filter: bool = False
        for filt in filters:
            if filt.re.fullmatch(theory_descriptor.metadata.filter_name) is not None:
                matches_filter = not filt.isExclude
                break
        if matches_filter:
            l = self.get(theory_descriptor.target.__module__)
            d = self.__datas.get(theory_descriptor.target)
            if d is not None:
                d.reverse()
                for data in d:
                    theory_descriptor.datas.append(data)
            if not self.__exclude_by_traits(theory_descriptor):
                l.append(theory_descriptor)

    def withData(self, target: Callable[..., Any], data: tuple[Any, ...]) -> None:
        """Associate a data point with *target* for later resolution in ``put()``."""
        d = self.__datas.get(target)
        if d is None:
            d = []
            self.__datas[target] = d
        d.append(data)
