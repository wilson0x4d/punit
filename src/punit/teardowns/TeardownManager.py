# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, Tuple

from .Teardown import Teardown


class TeardownManager:

    __instance: Optional['TeardownManager'] = None
    # NOTE: dict key is (scope_type, module_name, class_or_empty)
    __teardowns: dict[Tuple[str, str, str], Teardown]
    __teardown_error_count: int

    def __init__(self) -> None:
        if TeardownManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TeardownManager')  # pragma: no cover
        self.__teardowns = {}
        self.__teardown_error_count = 0

    @staticmethod
    def instance() -> TeardownManager:
        if TeardownManager.__instance is None:
            TeardownManager.__instance = TeardownManager()
        return TeardownManager.__instance

    @property
    def teardown_error_count(self) -> int:
        return self.__teardown_error_count

    def get(self, scope_type: str, module_name: str, class_name: Optional[str] = None) -> Optional[Teardown]:
        """Look up a teardown by (scope_type, module_name, class_name).

        For class-scoped lookups ``class_name`` must match the first segment of
        the decorated method's ``__qualname__``.  For module-scoped teardowns
        pass ``class_name = None`` or empty string; the manager normalises this
        to ``""``.
        """
        key: Tuple[str, str, str]
        if class_name is None or class_name == '':
            key = (scope_type, module_name, '')
        else:
            key = (scope_type, module_name, class_name)

        return self.__teardowns.get(key)

    def put(self, td: Teardown) -> None:
        """Store a teardown keyed by (scope_type, module_name, class_or_empty)."""
        cn = td.metadata.class_name
        if cn is not None and len(cn) > 0:
            key: Tuple[str, str, str] = (td.scope_type, td.metadata.module_name, cn)
        else:
            key = (td.scope_type, td.metadata.module_name, '')

        # Only one teardown per scope; last decorator wins if accidentally
        # applied twice.
        self.__teardowns[key] = td

    def record_error(self) -> None:
        """Called when a teardown function raises an exception."""
        self.__teardown_error_count += 1

    @staticmethod
    def reset() -> None:
        """Reset the singleton (used between test modules / suites)."""
        TeardownManager.__instance = None
