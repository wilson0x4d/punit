# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import importlib
import os
import socket
import time
import traceback

from .cli import CommandLineInterface
from .facts.FactManager import FactManager
from .metadata.CallableMetadata import CallableMetadata
from .theories.TheoryManager import TheoryManager
from .TestResult import TestResult


class TestRunner:

    __cli: CommandLineInterface
    __filenames: list[str]
    __test_package_name: str

    def __init__(self, test_package_name: str, filenames: list[str], cli: CommandLineInterface):
        self.__cli = cli
        self.__filenames = filenames
        self.__test_package_name = test_package_name

    def print_test_result(self, test_result: TestResult):
        if self.__cli.quiet:
            return
        glyph = '🟩' if test_result.is_success else '🟥'
        data = test_result.properties.get('data')
        if data is None:
            data = ''
        else:
            try:
                data = f'({",".join([str(e) for e in data])})'
            except Exception:
                data = '(???)'
        print(f'{glyph} {test_result.module_name}/{"" if test_result.class_name is None or len(test_result.class_name) == 0 else f"{test_result.class_name}/"}{test_result.test_name}{data} [{test_result.tookPretty}]')
        if self.__cli.verbose and (not test_result.is_success) and test_result.exception is not None:
            print(f'Test File:\n    {test_result.file_name}\nError:\n    {test_result.exception}\n    Traceback:\n{"".join(traceback.format_tb(test_result.exception.__traceback__))}')

    async def run(self) -> list[TestResult]:
        results: list[TestResult] = []
        result: TestResult
        # TODO: aliasing
        host_name: str = socket.gethostname()
        test_package_path = os.path.join(os.path.abspath(os.curdir), self.__test_package_name).replace('\\', '/')
        for filename in self.__filenames:
            ts = time.time()
            moduleImportName = filename.replace(test_package_path, '').replace('/', '.')
            if moduleImportName.endswith('.py'):
                moduleImportName = moduleImportName[:-3]
            module_report_name = moduleImportName.lstrip('.')
            try:
                testModule = importlib.import_module(moduleImportName, self.__test_package_name)
                # execute all facts
                facts = FactManager.instance().get(testModule.__name__)
                for fact in facts:
                    result = TestResult()
                    result.host_name = host_name
                    result.package_name = self.__test_package_name
                    result.file_name = filename
                    result.module_name = module_report_name
                    result.start_time = time.time()
                    result.captureOutput(not self.__cli.verbose)
                    try:
                        await fact.execute(testModule)
                        result.is_success = True
                    except Exception as ex:
                        result.is_success = False
                        result.exception = ex
                    result.releaseOutput()
                    result.stop_time = time.time()
                    result.class_name = fact.metadata.class_name
                    result.test_name = fact.metadata.name
                    results.append(result)
                    self.print_test_result(result)
                    if self.__cli.failfast and not result.is_success:
                        return results
                # execute all theories
                theories = TheoryManager.instance().get(testModule.__name__)
                for theory in theories:
                    for data in theory.datas:
                        result = TestResult()
                        result.host_name = host_name
                        result.package_name = self.__test_package_name
                        result.properties['data'] = data
                        result.file_name = filename
                        result.module_name = module_report_name
                        result.start_time = time.time()
                        result.captureOutput(not self.__cli.verbose)
                        try:
                            await theory.execute(testModule, data)
                            result.is_success = True
                        except Exception as ex:
                            result.is_success = False
                            result.exception = ex
                        result.releaseOutput()
                        result.stop_time = time.time()
                        result.class_name = theory.metadata.class_name
                        result.test_name = theory.metadata.name
                        results.append(result)
                        self.print_test_result(result)
                        if self.__cli.failfast and not result.is_success:
                            return results
            except Exception as ex:
                # module-level failure, report test failure against the module
                # this is a best-attempt to create output that report readers
                # can consume to show there was a broad failure in a module.
                result = TestResult()
                result.class_name = '*'
                result.module_name = module_report_name
                result.test_name = '*'
                result.start_time = ts
                result.stop_time = time.time()
                result.is_success = False
                result.exception = ex
                results.append(result)
                self.print_test_result(result)
                if self.__cli.failfast:
                    return results
        return results
