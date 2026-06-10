# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, Tuple

from .Setup import Setup


class SetupManager:

    __instance: Optional['SetupManager'] = None
    # NOTE: dict key is (scope_type, module_name, class_or_empty)
    __setups: dict[Tuple[str, str, str], Setup]
    __setup_error_count: int

    def __init__(self) -> None:
        if SetupManager.__instance is not None:
            raise Exception('Cannot create more than one instance of SetupManager')  # pragma: no cover
        self.__setups = {}
        self.__setup_error_count = 0

    @staticmethod
    def instance() -> SetupManager:
        if SetupManager.__instance is None:
            SetupManager.__instance = SetupManager()
        return SetupManager.__instance

    @property
    def setup_error_count(self) -> int:
        return self.__setup_error_count

    def get(self, scope_type: str, module_name: str, class_name: Optional[str] = None) -> Optional[Setup]:
        """Look up a setup by (scope_type, module_name, class_name).

        For class-scoped lookups ``class_name`` must match the first segment of
        the decorated method's ``__qualname__``.  For module-scoped setups
        pass ``class_name = None`` or empty string;  the manager normalises this
        to ``""``.
        """
        key: Tuple[str, str, str]
        if class_name is None or class_name == '':
            key = (scope_type, module_name, '')
        else:
            key = (scope_type, module_name, class_name)

        return self.__setups.get(key)

    def put(self, sd: Setup) -> None:
        """Store a setup keyed by (scope_type, module_name, class_or_empty)."""
        cn = sd.metadata.class_name
        if cn is not None and len(cn) > 0:
            key: Tuple[str, str, str] = (sd.scope_type, sd.metadata.module_name, cn)
        else:
            key = (sd.scope_type, sd.metadata.module_name, '')

        # Only one setup per scope;  last decorator wins if accidentally
        # applied twice.
        self.__setups[key] = sd

    def record_error(self) -> None:
        """Called when a setup function raises an exception."""
        self.__setup_error_count += 1

    @staticmethod
    def reset() -> None:
        """Reset the singleton (used between test modules / suites)."""
        SetupManager.__instance = None
