# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import re

from ..facts import FactManager
from ..theories import TheoryManager
from ..cli import CommandLineInterface
from ..traits import Trait

class TestModuleDiscovery:

    __cli:CommandLineInterface
    __excludePatterns:list[re.Pattern]
    __excludeTraits:list[Trait]
    __filenames:list[str]
    __filterPatterns:list[re.Pattern]
    __includePatterns:list[re.Pattern]
    __includeTraits:list[Trait]
    __workdir:str

    def __init__(self, workdir:str, includePatterns:list[str], excludePatterns:list[str], cli:CommandLineInterface) -> None:
        self.__cli = cli
        self.__excludePatterns = []
        if excludePatterns is not None:
            for pattern in excludePatterns:
                self.__excludePatterns.append(
                    re.compile(
                        self.__convertPatternToRegex(pattern),
                        re.IGNORECASE))
        self.__filenames = []
        self.__filterPatterns = self.__buildFilterPatterns(cli.filterPattern)
        self.__includePatterns = []
        self.__excludeTraits = cli.excludeTraits
        self.__includeTraits = cli.includeTraits
        if includePatterns is not None:
            for pattern in includePatterns:
                self.__includePatterns.append(
                    re.compile(
                        self.__convertPatternToRegex(pattern),
                        re.IGNORECASE))
        self.__workdir = workdir

    def __buildFilterPatterns(self, input:str) -> list[re.Pattern]:
        if input.startswith('@'):
            # treat as a filepath containing one or more filter patterns
            filepath = os.path.realpath(input[1:])
            with open(filepath, 'rb') as f:
                result = list[re.Pattern]()                
                for line in f.read().decode().splitlines():
                    if (self.__cli.verbose):
                        print(f'\t{line}')
                    result.append(re.compile(self.__convertPatternToRegex(line)))
                return result
        else:
            # treat as a single filter pattern
            return [re.compile(self.__convertPatternToRegex(input))]

    def __convertPatternToRegex(self, pattern:str) -> str:
        result = re.escape(pattern)\
            .replace('\\\\', '/')\
            .replace('\\*', r'.+')\
            .replace('?', '.')
        return result

    def __testAnyInclude(self, input:str) -> bool:
        for pat in self.__includePatterns:
            if len(pat.findall(input)) > 0:
                return True
        return False

    def __testAnyExclude(self, input:str) -> bool:
        for pat in self.__excludePatterns:
            if len(pat.findall(input)) > 0:
                return True
        return False

    def __walkDirectory(self, path:str) -> list[str]:
        filenames = []
        if os.path.isdir(path):
            for dname, dlist, flist in os.walk(path, topdown=True):
                if self.__cli.verbose:
                    print(f'.. discovery for: {dname}')
                dname2 = dname.replace('\\', '/')
                if self.__testAnyExclude(dname2):
                    # directory is excluded, prune all children
                    if self.__cli.verbose:
                        print(f'Excluded: {dname}')
                    while len(dlist) > 0:
                        del dlist[0]
                    while len(flist) > 0:
                        del flist[0]
                # determine if any individual subdirs should be pruned
                dlnames = dlist.copy()
                for dlname in dlnames:
                    dlname2 = dlname.replace('\\', '/')
                    if self.__testAnyExclude(dlname2):
                        if self.__cli.verbose:
                            print(f'Excluded: {dlname}')
                        dlist.remove(dlname)
                # determine if any individual files should be pruned
                for fname in flist:
                    fname2 = os.path.join(dname, fname).replace('\\', '/')
                    if self.__testAnyInclude(fname2) and not self.__testAnyExclude(fname2):
                        if fname.endswith('.py'):
                            if self.__cli.verbose:
                                print(f'Included: {fname}')
                            filenames.append(fname2)
        return filenames

    @property
    def filenames(self) -> list[str]:
        return self.__filenames
        
    def discover(self) -> list[str]:
        FactManager.instance().excludeTraits = self.__excludeTraits
        FactManager.instance().filterPatterns = self.__filterPatterns
        FactManager.instance().includeTraits = self.__includeTraits
        TheoryManager.instance().excludeTraits = self.__excludeTraits
        TheoryManager.instance().filterPatterns = self.__filterPatterns
        TheoryManager.instance().includeTraits = self.__includeTraits
        if self.__cli.verbose:
            print(f'.. starting test discovery')
        self.__filenames = self.__walkDirectory(self.__workdir)
        if self.__cli.verbose:
            print('.. finished test discovery.')
        return self.__filenames
