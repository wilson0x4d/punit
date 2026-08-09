# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

from __future__ import annotations

from typing import Optional

from ..filters import FilterManager
from ..traits import TraitDescriptor, TraitManager
from .fact_descriptor import FactDescriptor


class FactManager:

    __excluded_traits: list[TraitDescriptor]
    __instance: Optional['FactManager'] = None
    __included_traits: list[TraitDescriptor]
    __modules: dict[str, list[FactDescriptor]]

    def __init__(self) -> None:
        if FactManager.__instance is not None:
            raise Exception('Cannot create more than one instance of FactManager')  # pragma: no cover
        self.__modules = {}

    @staticmethod
    def instance() -> FactManager:
        if FactManager.__instance is None:
            FactManager.__instance = FactManager()
        return FactManager.__instance

    @property
    def excluded_traits(self) -> list[TraitDescriptor]:
        return [] if self.__excluded_traits is None else self.__excluded_traits

    @excluded_traits.setter
    def excluded_traits(self, value: list[TraitDescriptor]) -> None:
        self.__excluded_traits = value

    @property
    def included_traits(self) -> list[TraitDescriptor]:
        return [] if self.__included_traits is None else self.__included_traits

    @included_traits.setter
    def included_traits(self, value: list[TraitDescriptor]) -> None:
        self.__included_traits = value

    def __exclude_by_traits(self, fact_descriptor: FactDescriptor) -> bool:
        traits = TraitManager.instance().get(fact_descriptor.target)
        if self.excluded_traits is not None and len(self.excluded_traits) > 0:
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

    def get(self, module_name: str) -> list[FactDescriptor]:
        fact_descriptors = self.__modules.get(module_name)
        if fact_descriptors is None:
            fact_descriptors = []
            self.__modules[module_name] = fact_descriptors
        return fact_descriptors

    def put(self, fact_descriptor: FactDescriptor) -> None:
        filters = FilterManager.instance().filters
        matches_filter: bool = False
        for filt in filters:
            if filt.re.fullmatch(fact_descriptor.metadata.filter_name) is not None:
                matches_filter = not filt.isExclude
                break
        if matches_filter:
            l = self.get(fact_descriptor.target.__module__)
            if not self.__exclude_by_traits(fact_descriptor):
                l.append(fact_descriptor)
