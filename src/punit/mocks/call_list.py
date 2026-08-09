# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Union,
)

from .call import Call


class CallList(tuple):  # type: ignore[type-arg]
    """Tuple of :class:`Call` supporting partial-sublist matching via ``__contains__``."""

    def __contains__(self, item: object) -> bool:  # type: ignore[override]
        if isinstance(item, CallList):
            target = list(item)
            if not target:
                return True
            for i in range(len(self) - len(target) + 1):
                if all(CallList.__matches(self[i + j], target[j]) for j in range(len(target))):
                    return True
            return False
        return super().__contains__(item)

    @staticmethod
    def __matches(call: Call, other: Call) -> bool:
        return call.path == other.path and call.args == other.args and call.kwargs == other.kwargs
