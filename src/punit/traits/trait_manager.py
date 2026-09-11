# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

from types import FunctionType, MethodType
from typing import Any, Callable, Optional

from .trait_descriptor import TraitDescriptor


class TraitManager:
    """
    Singleton that maps callables to their associated TraitDescriptors.

    Usage
    -----

    .. code-block:: python

        from punit.traits import TraitManager, TraitDescriptor

        manager = TraitManager.instance()
        manager.put(my_function, TraitDescriptor('category', 'api'))
        traits = manager.get(my_function)

    """

    __instance: Optional['TraitManager'] = None
    __traits: dict[Callable[..., Any] | FunctionType | MethodType, dict[str, TraitDescriptor]]

    def __init__(self) -> None:
        if TraitManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TraitManager')  # pragma: no cover
        self.__traits = dict[Callable[..., Any] | FunctionType | MethodType, dict[str, TraitDescriptor]]()

    @staticmethod
    def instance() -> TraitManager:
        """Return the singleton TraitManager instance."""
        if TraitManager.__instance is None:
            TraitManager.__instance = TraitManager()
        return TraitManager.__instance

    def get(self, callable: Callable[..., Any] | FunctionType | MethodType) -> list[TraitDescriptor]:
        """Return all traits associated with *callable*."""
        d = self.__traits.get(callable)
        if d is None:
            d = dict[str, TraitDescriptor]()
            self.__traits[callable] = d
        return [e for e in d.values()]

    def put(self, callable: Callable[..., Any], trait: TraitDescriptor) -> None:
        """Associate *trait* with *callable*, keyed by the trait's name."""
        d = self.__traits.get(callable)
        if d is None:
            d = dict[str, TraitDescriptor]()
            self.__traits[callable] = d
        d[trait.name] = trait
