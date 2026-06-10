# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import re


class Filter:
    """
    Wraps a glob-style filter pattern and compiles it to a case-insensitive regex.

    Patterns use ``*`` for multi-character wildcards and ``?`` for single characters.
    Prefix with ``!`` to mark the filter as an exclusion rule.
    """

    __isExclude: bool
    __pattern: str
    __re: re.Pattern[str]

    def __init__(self, pattern: str) -> None:
        self.__isExclude = pattern.startswith('!')
        self.__pattern = pattern
        self.__re = self.__toRegex(pattern)

    def __toRegex(self, pattern: str) -> re.Pattern[str]:
        """Convert a glob-style pattern to a compiled regex.

        Supports ``*`` (multi-char wildcard), ``?`` (single-char wildcard),
        and ``!`` prefix (exclusion).  Matching is case-insensitive.
        """
        if self.__isExclude:
            pattern = pattern[1:]
        pattern = re.escape(pattern)\
            .replace('\\\\', '/')\
            .replace('\\*', r'.*')\
            .replace('?', '.')
        return re.compile(pattern, re.IGNORECASE)

    @property
    def isExclude(self) -> bool:
        return self.__isExclude

    @property
    def pattern(self) -> str:
        return self.__pattern

    @property
    def re(self) -> re.Pattern:
        return self.__re
