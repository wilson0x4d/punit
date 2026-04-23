# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import re


class Filter:

    __isExclude:bool
    __pattern:str
    __re:re.Pattern

    def __init__(self, pattern:str) -> None:
        self.__isExclude = pattern.startswith('!')
        self.__pattern = pattern
        self.__re = self.__toRegex(pattern)

    def __toRegex(self, pattern:str) -> re.Pattern:
        if self.__isExclude:
            pattern = pattern[1:]
        pattern = re.escape(pattern)\
            .replace('\\\\', '/')\
            .replace('\\*', r'.*')\
            .replace('?', '.')
        return re.compile(pattern)

    @property
    def isExclude(self) -> bool:
        return self.__isExclude
    
    @property
    def pattern(self) -> str:
        return self.__pattern
    
    @property
    def re(self) -> re.Pattern:
        return self.__re
