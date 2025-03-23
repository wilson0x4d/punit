# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import importlib
import os
import socket
import time
import traceback
from .cli import CommandLineInterface
from .facts.FactManager import FactManager
from .theories.TheoryManager import TheoryManager
from .TestResult import TestResult

class TestRunner:

    __cli:CommandLineInterface
    __filenames:list[str]
    __testPackageName:str
    
    def __init__(self, testPackageName:str, filenames:list[str], cli:CommandLineInterface):
        self.__cli = cli
        self.__filenames = filenames
        self.__testPackageName = testPackageName

    def printTestResult(self, testResult:TestResult):
        if self.__cli.quiet:
            return
        glyph = '🟩' if testResult.isSuccess else '🟥'
        data = testResult.properties.get('data')
        if data is None:
            data = ''
        else:
            try:
                data = f'({",".join([str(e) for e in data])})'
            except:
                data = '(???)'
        print(f'{glyph} {testResult.moduleName}/{"" if testResult.className is None or len(testResult.className) == 0 else f"{testResult.className}/"}{testResult.testName}{data} [{testResult.tookPretty}]')
        if self.__cli.verbose and (not testResult.isSuccess) and testResult.exception is not None:
            print(f'Test File:\n    {testResult.fileName}\nError:\n    {testResult.exception}\n    Traceback:\n{"".join(traceback.format_tb(testResult.exception.__traceback__))}')

    async def run(self) -> list[TestResult]:
        results:list[TestResult] = []
        # TODO: aliasing
        hostName:str = socket.gethostname()
        testPackagePath = os.path.join(os.path.abspath(os.curdir), self.__testPackageName).replace('\\', '/')
        for filename in self.__filenames:
            ts = time.time()
            moduleImportName = filename.replace(testPackagePath, '').replace('/', '.').replace('.py', '')
            moduleReportName = moduleImportName.lstrip('.')
            try:
                testModule = importlib.import_module(moduleImportName, self.__testPackageName)
                # execute all facts
                facts = FactManager.instance().get(testModule.__name__)
                for fact in facts:
                    result:TestResult = TestResult()
                    result.hostName = hostName
                    result.packageName = self.__testPackageName
                    result.fileName = filename
                    result.moduleName = moduleReportName
                    result.startTime = time.time()
                    result.captureOutput(not self.__cli.verbose)
                    try:
                        await fact.execute(testModule)
                        result.isSuccess = True
                    except Exception as ex:
                        result.isSuccess = False
                        result.exception = ex
                    result.releaseOutput()
                    result.stopTime = time.time()
                    result.className = fact.className
                    result.testName = fact.testName
                    results.append(result)
                    self.printTestResult(result)
                    if self.__cli.failfast and not result.isSuccess:
                        return results
                # execute all theories
                theories = TheoryManager.instance().get(testModule.__name__)
                for theory in theories:
                    for data in theory.datas:
                        result:TestResult = TestResult()
                        result.hostName = hostName
                        result.packageName = self.__testPackageName
                        result.properties['data'] = data
                        result.fileName = filename
                        result.moduleName = moduleReportName
                        result.startTime = time.time()
                        result.captureOutput(not self.__cli.verbose)
                        try:
                            await theory.execute(testModule, data)
                            result.isSuccess = True
                        except Exception as ex:
                            result.isSuccess = False
                            result.exception = ex
                        result.releaseOutput()
                        result.stopTime = time.time()
                        result.className = theory.className
                        result.testName = theory.testName
                        results.append(result)
                        self.printTestResult(result)
                        if self.__cli.failfast and not result.isSuccess:
                            return results
            except Exception as ex:
                # module-level failure, report test failure against the module
                # this is a best-attempt to create output that report readers
                # can consume to show there was a broad failure in a module.
                result = TestResult()
                result.className = '*'
                result.moduleName = moduleReportName
                result.testName = '*'
                result.startTime = ts
                result.stopTime = time.time()
                result.isSuccess = False
                result.exception = ex
                results.append(result)
                self.printTestResult(result)
                if self.__cli.failfast:
                    return results
        return results
