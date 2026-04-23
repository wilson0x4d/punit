# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import select
import sys
from typing import Optional

from .Filter import Filter


class FilterManager:

    __instance:Optional['FilterManager']|None = None
    __filters:list[Filter]

    def __init__(self) -> None:
        self.__filters = list[Filter]()

    @property
    def filters(self) -> list[Filter]:
        return self.__filters

    @staticmethod
    def instance() -> 'FilterManager':
        instance = FilterManager.__instance
        if instance is None:
            instance = FilterManager()
            FilterManager.__instance = instance
        return instance

    def add(self, pattern:str) -> None:
        self.__filters.append(Filter(pattern))

    def remove(self, pattern:str) -> None:
        for filter in [e for e in self.__filters]:
            if filter.pattern == pattern:
                self.__filters.remove(filter)
                break

    def load(self, filepath:str) -> None:
        # treat as a filepath containing one or more filter patterns
        lines:list[str] = []
        if filepath == 'stdin':
            ready, _, _ = select.select([sys.stdin], [], [], 5)
            if not ready:
                print('No data from stdin, aborting.')
                sys.exit(7)
            lines = sys.stdin.read().splitlines()
            if len(lines) == 0:
                print('No filters from stdin, aborting.')
                sys.exit(6)
        else:
            if not os.path.exists(filepath):
                print(f'file missing or not accessible: {filepath}')
                sys.exit(5)
            with open(filepath, 'rb') as f:
                lines = f.read().decode().splitlines()
        for line in lines:
            line = line.split('#')[0].strip() # strip comments and prefix/postfix whitespace
            if len(line) == 0:
                # comments and empty lines
                continue
            self.__filters.append(Filter(line))

    def print(self) -> None:
        if len(FilterManager.instance().filters) > 0:
            print('Filters:')
            for filter in self.filters:
                print(f'\t{filter.pattern}')
