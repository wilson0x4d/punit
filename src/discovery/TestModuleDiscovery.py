# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import re

from ..facts import FactManager
from ..theories import TheoryManager
from ..cli import CommandLineInterface

class TestModuleDiscovery:

    __cli:CommandLineInterface
    __excludePatterns:list[re.Pattern]
    __filenames:list[str]
    __filterPattern:re.Pattern
    __includePatterns:list[re.Pattern]
    __workdir:str

    def __init__(self, workdir:str, includePatterns:list[str], excludePatterns:list[str], cli:CommandLineInterface):
        self.__cli = cli
        self.__excludePatterns = []
        if excludePatterns is not None:
            for pattern in excludePatterns:
                self.__excludePatterns.append(
                    re.compile(
                        self.__convertPatternToRegex(pattern),
                        re.IGNORECASE))
        self.__filenames = []
        self.__filterPattern = re.compile(self.__convertPatternToRegex(cli.filterPattern))
        self.__includePatterns = []
        if includePatterns is not None:
            for pattern in includePatterns:
                self.__includePatterns.append(
                    re.compile(
                        self.__convertPatternToRegex(pattern),
                        re.IGNORECASE))
        self.__workdir = workdir

    def __convertPatternToRegex(self, pattern:str):
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
        FactManager.instance().filterPattern = self.__filterPattern
        TheoryManager.instance().filterPattern = self.__filterPattern
        if self.__cli.verbose:
            print(f'.. starting test discovery')
        self.__filenames = self.__walkDirectory(self.__workdir)
        if self.__cli.verbose:
            print('.. finished test discovery.')
        return self.__filenames
