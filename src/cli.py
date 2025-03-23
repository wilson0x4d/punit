# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import sys
import typing
from . import __version__

CommandLineInterface = typing.ForwardRef('CommandLineInterface')

class CommandLineInterface:

    __excludePatterns:list[str]
    __failfast:bool
    __filterPattern:str
    __help:bool
    __includePatterns:list[str]
    __no_default_patterns:bool
    __outputFilename:str
    __quiet:bool
    __reportFormat:str
    __testPackageName:str
    __verbose:bool
    __workdir:str

    def __init__(self):
        self.__aliases = {}
        self.__excludePatterns = []
        self.__failfast = False
        self.__filterPattern = '*'
        self.__help = False
        self.__includePatterns = []
        self.__no_default_patterns = False
        self.__outputFilename = None
        self.__quiet = False
        self.__reportFormat = None
        self.__testPackageName = 'tests'
        self.__workdir = os.path.curdir
        self.__verbose = False

    def __parse(self, argv:list[str]) -> CommandLineInterface:
        aliasName:str = None
        extractFilterPattern:bool = False
        extractExcludePattern:bool = False
        extractIncludePattern:bool = False
        extractAliasName:bool = False
        extractAliasPath:bool = False
        extractReportFormat:bool = False
        extractOutputFilename:bool = False
        for arg in argv:
            if extractFilterPattern:
                self.__filterPattern = arg
                extractFilterPattern = False
                continue
            if extractIncludePattern:
                self.__includePatterns.append(arg)
                extractIncludePattern = False
                continue
            elif extractExcludePattern:
                self.__excludePatterns.append(arg)
                extractExcludePattern = False
                continue
            elif extractAliasName:
                aliasName = arg
                extractAliasName = False
                extractAliasPath = True
                continue
            elif extractAliasPath:
                extractAliasPath = False
                self.__aliases[aliasName] = arg
                continue
            elif self.__workdir is None:
                self.__workdir = arg
                continue
            elif self.__testPackageName is None:
                self.__testPackageName = arg
                continue
            elif extractReportFormat:
                extractReportFormat = False
                self.__reportFormat = arg.lower()
                match self.__reportFormat:
                    case 'html' | 'junit':
                        pass
                    case _:
                        print(f'Unsupported value "{arg}" for --report argument, aborting.')
                        print(f'(valid values are "json" and "junit")')
                        exit(4)
                continue
            elif extractOutputFilename:
                extractOutputFilename = False
                self.__outputFilename = arg
                continue
            match arg:
                case '-h' | '--help':
                    self.__help = True
                case '-a':
                    extractAliasName = True
                case '-t' | '--filter':
                    extractFilterPattern = True
                case '-e' | '--exclude':
                    extractExcludePattern = True
                case '-f' | '--failfast':
                    self.__failfast = True
                case '-p' | '--test-package':
                    self.__testPackageName = None
                case '-i' | '--include':
                    extractIncludePattern = True
                case '-q' | '--quiet':
                    self.__quiet = True
                case '-w' | '--working-directory':
                    self.__workdir = None
                case '-v' | '--verbose':
                    self.__verbose = True
                case '-n' | '--no-default-patterns':
                    self.__no_default_patterns = True
                case '-r' | '--report':
                    extractReportFormat = True
                case '-o' | '--output':
                    extractOutputFilename = True
                case _:
                    continue
        return self

    @property
    def aliases(self) -> bool:
        return self.__aliases

    @property
    def failfast(self) -> bool:
        return self.__failfast

    @property
    def filterPattern(self) -> str:
        return self.__filterPattern

    @property
    def excludePatterns(self) -> list[str]:
        return self.__excludePatterns

    @property
    def help(self) -> bool:
        return self.__help

    @property
    def includePatterns(self) -> list[str]:
        return self.__includePatterns

    @property
    def outputFilename(self) -> str|None:
        return self.__outputFilename

    @property
    def quiet(self) -> bool:
        return self.__quiet or (self.__reportFormat is not None and self.__outputFilename is None)

    @property
    def reportFormat(self) -> str|None:
        return self.__reportFormat

    @property
    def testPackageName(self) -> str:
        return self.__testPackageName

    @property
    def verbose(self) -> bool:
        return self.__verbose and self.__reportFormat is None 

    @property
    def workdir(self) -> str:
        return self.__workdir

    def printHelp(self) -> None:
        self.printVersion()
        print(
"""
Usage: python3 -m punit [-h|--help]
                        [-q|--quiet] [-v|--verbose]
                        [-f|--failfast]
                        [-p|--test-package NAME]
                        [-i|--include PATTERN]
                        [-e|--exclude PATTERN]
                        [-t|--filter PATTERN]
                        [-w|--workdir DIRECTORY]
                        [-n|--no-default-patterns]
                        [-r|--report {junit|json}]
                        [-o|--output FILENAME]

Options:
    -h, --help           Show this help text and exit
    -q, --quiet          Quiet output
    -v, --verbose        Verbose output
    -f, --failfast       Stop on first failure or error
    -p, --test-package NAME
        Use NAME as the test package, all tests should
        be locatable as modules in the named package.
        Default: 'tests'
    -i, --include PATTERN
        Include any tests matching PATTERN
        Default: '*.py'
    -e, --exclude PATTERN
        Exclude any tests matching PATTERN, overriding --include
        Default: '__*__' (dunder files), '/.*/' (dot-directories)
    -t, --filter
        Only execute tests matching PATTERN
        Default: '*'
    -w, --working-directory DIRECTORY
        Working directory (defaults to start directory)
    -n, --no-default-patterns
        Do not apply any default include/exclude patterns.
    -r, --report {html|junit}
        Generate a report to stdout using either an "html"
        or "junit" format. When generating a report to stdout
        all other output is suppressed, unless `--output`
        is also specified.
    -o, --output FILENAME
        If `--report` is used, instead of writing to stdout
        write to FILENAME. In this case `--report` does not
        suppress any program output.
"""
        )
        exit(0)

    def printSummary(self) -> None:
        self.printVersion()
        print(f'Working Directory:\n\t{self.__workdir}')
        print(f'Fail Fast: \n\t{"Yes" if self.__failfast else "No"}')
        if len(self.__includePatterns) > 0:
            print('Include Patterns:')
            for pattern in self.__includePatterns:
                print(f'\t{pattern}')
        if len(self.__excludePatterns) > 0:
            print('Exclude Patterns:')
            for pattern in self.__excludePatterns:
                print(f'\t{pattern}')
        print('Filter Pattern:')
        print(f'\t{self.__filterPattern}')
    def printVersion(self) -> None:
        print(f'pUnit {__version__}')

    def validate(self) -> None:
        if self.__workdir is None or len(self.__workdir.lstrip()) == 0 or self.__workdir.startswith('-'):
            print(f'Invalid working directory specified: {self.__workdir}')
            exit(1)
        elif not os.path.isdir(self.__workdir):
            print(f'Working directory does not exist: {self.__workdir}')
            exit(2)
        self.__workdir = os.path.abspath(self.__workdir)
        if not self.__no_default_patterns:
            # if no other patterns specified, default to including all files found in the directory matching `testPackageName`
            if len(self.__includePatterns) == 0:
                self.__includePatterns.append(f'/{self.testPackageName}/*.py')
            # always exclude dot-folders (.git, .venv, etc)
            self.__excludePatterns.append('/.*')
            # always exclude dunder files
            self.__excludePatterns.append('/__*__')

    @staticmethod
    def parse(argv:list[str] = sys.argv) -> CommandLineInterface:
        result = CommandLineInterface().__parse(argv)
        result.validate()
        return result
