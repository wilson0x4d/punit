# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import datetime
import xml.etree.ElementTree as et
from xml.sax.saxutils import escape
from ..TestResult import TestResult

class JUnitError:
    message:str = None
    type:str = None


class JUnitTestCase:
    # attrs
    classname:str = None
    disabled:bool = None
    name:str = None
    time:float = None
    # eles
    error:JUnitError = None
    failure:JUnitError = None
    stdout:str = None
    stderr:str = None
    skipped:bool = None
    def __init__(self, testResult:TestResult) -> None:
        self.disabled = False
        self.classname = testResult.moduleName if testResult.className is None else f'{testResult.moduleName}.{testResult.className}'
        self.time = testResult.took
        data = testResult.properties.get('data')
        if data is not None and len(data) > 0:
            data = f'({",".join([str(e) for e in data])})'
        else:
            data = ''
        self.name = f'{testResult.testName}{data}'
        if not testResult.isSuccess:
            exc_type = type(testResult.exception)
            error = JUnitError()
            error.message = f'{testResult.exception}'
            error.type = getattr(exc_type, '__name__') if not hasattr(exc_type, '__qualname__') else getattr(exc_type, '__qualname__')
            if issubclass(exc_type, AssertionError):
                self.failure = error
            else:
                self.error = error
        self.stdout = None if testResult.stdout is None else escape(testResult.stdout)
        self.stderr = None if testResult.stderr is None else escape(testResult.stderr)
        self.skipped = False


class JUnitTestSuite:
    # attrs
    name:str = None
    hostname:str = None
    id:int = None
    name:str = None
    package:str = None
    timestamp:datetime.datetime = None
    # eles
    testCases:list[JUnitTestCase] = None

    @property
    def disabled(self) -> int:
        result:int = 0
        for testCase in self.testCases:
            if testCase.disabled == True:
                result += 1
        return result

    @property
    def errors(self) -> int:
        result:int = 0
        for testCase in self.testCases:
            if testCase.error is not None:
                result += 1
        return result

    @property
    def failures(self) -> int:
        result:int = 0
        for testCase in self.testCases:
            if testCase.failure is not None:
                result += 1
        return result

    @property
    def skipped(self) -> int:
        result:int = 0
        for testCase in self.testCases:
            if testCase.skipped:
                result += 1
        return result

    @property
    def tests(self) -> float:
        return len(self.testCases)

    @property
    def time(self) -> float:
        result:float = 0.0
        for testCase in self.testCases:
            result += testCase.time
        return result


class JUnitReportGenerator:

    def __init__(self):
        pass

    def generate(self, testResults:list[TestResult]) -> str:
        # transform to intermediary model
        testSuites:dict[str, JUnitTestSuite] = {}
        ts = 0
        for testResult in testResults:
            if ts < testResult.stopTime:
                ts = testResult.stopTime
            testSuite = testSuites.get(testResult.moduleName)
            if testSuite is None:
                testSuite = JUnitTestSuite()
                testSuite.name = testResult.moduleName
                testSuite.id = len(testSuites)
                testSuite.hostname = testResult.hostName
                testSuite.package = testResult.packageName
                testSuite.testCases = []
                testSuites[testResult.moduleName] = testSuite
            testSuite.testCases.append(JUnitTestCase(testResult))
            testSuite.timestamp = datetime.datetime.fromtimestamp(ts)
        # materialize as xml
        totalDisabledCount = 0
        totalErrorCount = 0
        totalFailureCount = 0
        totalTestCount = 0
        totalTime = 0
        testSuitesEle:et.Element = et.Element('testsuites')
        for testSuiteName in testSuites:
            testSuite:JUnitTestSuite = testSuites[testSuiteName]
            totalTime += testSuite.time
            totalDisabledCount += testSuite.disabled
            totalErrorCount += testSuite.errors
            totalFailureCount += testSuite.failures
            totalTestCount += testSuite.tests
            testSuiteEle = et.SubElement(testSuitesEle, 'testsuite')
            testSuiteEle.attrib['disabled'] = str(testSuite.disabled)
            testSuiteEle.attrib['errors'] = str(testSuite.errors)
            testSuiteEle.attrib['failures'] = str(testSuite.failures)
            testSuiteEle.attrib['id'] = str(testSuite.id)
            testSuiteEle.attrib['name'] = str(testSuite.name)
            testSuiteEle.attrib['package'] = str(testSuite.package)
            testSuiteEle.attrib['timestamp'] = str(testSuite.timestamp)
            testSuiteEle.attrib['hostname'] = str(testSuite.hostname)
            testSuiteEle.attrib['tests'] = str(testSuite.tests)
            testSuiteEle.attrib['time'] = f'{testSuite.time:.6f}'.rstrip('0').rstrip('.')
            for testCase in testSuite.testCases:
                testCaseEle = et.SubElement(testSuiteEle, 'testcase')
                testCaseEle.attrib['name'] = testCase.name
                if testCase.classname is not None:
                    testCaseEle.attrib['classname'] = testCase.classname
                testCaseEle.attrib['time'] = f'{testCase.time:.6f}'.rstrip('0').rstrip('.')
                if testCase.skipped:
                    et.SubElement(testCaseEle, 'skipped')
                if testCase.error is not None:
                    ele = et.SubElement(testCaseEle, 'error')
                    if testCase.error.type is not None:
                        ele.attrib['type'] = testCase.error.type
                    if testCase.error.message is not None:
                        ele.attrib['message'] = testCase.error.message
                if testCase.failure is not None:
                    ele = et.SubElement(testCaseEle, 'failure')
                    if testCase.failure.type is not None:
                        ele.attrib['type'] = testCase.failure.type
                    if testCase.failure.message is not None:
                        ele.attrib['message'] = testCase.failure.message
                if testCase.stdout is not None:
                    ele = et.SubElement(testCaseEle, 'system-out')
                    ele.text = testCase.stdout
                if testCase.stderr is not None:
                    ele = et.SubElement(testCaseEle, 'system-err')
                    ele.text = testCase.stderr
        testSuitesEle.attrib['disabled'] = str(totalDisabledCount)
        testSuitesEle.attrib['errors'] = str(totalErrorCount)
        testSuitesEle.attrib['failures'] = str(totalErrorCount)
        testSuitesEle.attrib['tests'] = str(totalTestCount)
        testSuitesEle.attrib['time'] = f'{totalTime:.6f}'.rstrip('0').rstrip('.')
        et.indent(testSuitesEle, space="    ")
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{et.tostring(testSuitesEle).decode()}\n'
