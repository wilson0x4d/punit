# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import re


class FilterDescriptor:
    """
    Wraps a glob-style filter pattern and compiles it to a case-insensitive regex.

    Patterns use ``*`` for multi-character wildcards and ``?`` for single characters.
    Prefix with ``!`` to mark the filter as an exclusion rule.

    Usage
    -----

    .. code-block:: python

        from punit.filters import FilterDescriptor

        filt = FilterDescriptor('test_*.py')
        print(filt.isExclude)  # False
        print(filt.pattern)    # 'test_*.py'

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
        """True if this filter is an exclusion rule (pattern prefixed with ``!``)."""
        return self.__isExclude

    @property
    def pattern(self) -> str:
        """The original glob-style pattern string."""
        return self.__pattern

    @property
    def re(self) -> re.Pattern[str]:
        """The compiled regex derived from the glob-style pattern."""
        return self.__re
