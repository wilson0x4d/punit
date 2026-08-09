# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import select
import sys
from typing import Optional

from .filter_descriptor import FilterDescriptor


class FilterManager:

    __instance: Optional['FilterManager'] = None
    __filter_descriptors: list[FilterDescriptor]

    def __init__(self) -> None:
        self.__filter_descriptors = list[FilterDescriptor]()

    @property
    def filters(self) -> list[FilterDescriptor]:
        return self.__filter_descriptors

    @staticmethod
    def instance() -> FilterManager:
        instance = FilterManager.__instance
        if instance is None:
            instance = FilterManager()
            FilterManager.__instance = instance
        return instance

    def add(self, pattern: str) -> None:
        self.__filter_descriptors.append(FilterDescriptor(pattern))

    def remove(self, pattern: str) -> None:
        for filt in [e for e in self.__filter_descriptors]:
            if filt.pattern == pattern:
                self.__filter_descriptors.remove(filt)
                break

    def load(self, filepath: str) -> None:
        # treat as a filepath containing one or more filter patterns
        lines: list[str] = []
        if filepath == 'stdin':
            ready, _, _ = select.select([sys.stdin], [], [], 5)
            if not ready:
                print('No data from stdin, aborting.')
                os._exit(7)
            lines = sys.stdin.read().splitlines()
            if len(lines) == 0:
                print('No filters from stdin, aborting.')
                os._exit(6)
        else:
            if not os.path.exists(filepath):
                print(f'file missing or not accessible: {filepath}')
                os._exit(5)
            with open(filepath, 'rb') as f:
                lines = f.read().decode().splitlines()
        for line in lines:
            line = line.split('#')[0].strip()  # strip comments and prefix/postfix whitespace
            if len(line) == 0:
                # comments and empty lines
                continue
            self.__filter_descriptors.append(FilterDescriptor(line))

    def print(self) -> None:
        if len(FilterManager.instance().filters) > 0:
            print('Filters:')
            for filt in self.filters:
                print(f'\t{filt.pattern}')
