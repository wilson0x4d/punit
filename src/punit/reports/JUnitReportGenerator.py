# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Optional
import datetime
import xml.etree.ElementTree as et
from xml.sax.saxutils import escape
from ..TestResult import TestResult


class JUnitError:
    message: Optional[str] = None
    type: Optional[str] = None


class JUnitTestCase:
    # attrs
    classname: Optional[str] = None
    disabled: Optional[bool] = None
    name: Optional[str] = None
    time: Optional[float] = None
    # eles
    error: Optional[JUnitError] = None
    failure: Optional[JUnitError] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    skipped: Optional[bool] = None

    def __init__(self, test_result: TestResult) -> None:
        self.disabled = False
        self.classname = test_result.module_name if test_result.class_name is None else f'{test_result.module_name}.{test_result.class_name}'
        self.time = test_result.took
        data = test_result.properties.get('data')
        if data is not None and len(data) > 0:
            data = f'({",".join([str(e) for e in data])})'
        else:
            data = ''
        self.name = f'{test_result.test_name}{data}'
        if not test_result.is_success:
            exc_type = type(test_result.exception)
            error = JUnitError()
            error.message = f'{test_result.exception}'
            error.type = getattr(exc_type, '__name__') if not hasattr(exc_type, '__qualname__') else getattr(exc_type, '__qualname__')
            if issubclass(exc_type, AssertionError):
                self.failure = error
            else:
                self.error = error
        self.stdout = None if test_result.stdout is None else escape(test_result.stdout)
        self.stderr = None if test_result.stderr is None else escape(test_result.stderr)
        self.skipped = False


class JUnitTestSuite:
    # attrs
    name: Optional[str] = None
    hostname: Optional[str] = None
    id: Optional[int] = None
    package: Optional[str] = None
    timestamp: Optional[datetime.datetime] = None
    # eles
    testCases: Optional[list[JUnitTestCase]] = None

    @property
    def disabled(self) -> int:
        result: int = 0
        if self.testCases is not None:
            for testCase in self.testCases:
                if testCase.disabled is True:
                    result += 1
        return result

    @property
    def errors(self) -> int:
        result: int = 0
        if self.testCases is not None:
            for testCase in self.testCases:
                if testCase.error is not None:
                    result += 1
        return result

    @property
    def failures(self) -> int:
        result: int = 0
        if self.testCases is not None:
            for testCase in self.testCases:
                if testCase.failure is not None:
                    result += 1
        return result

    @property
    def skipped(self) -> int:
        result: int = 0
        if self.testCases is not None:
            for testCase in self.testCases:
                if testCase.skipped:
                    result += 1
        return result

    @property
    def tests(self) -> int:
        return 0 if self.testCases is None else len(self.testCases)

    @property
    def time(self) -> float:
        result: float = 0.0
        if self.testCases is not None:
            for testCase in self.testCases:
                result += testCase.time if testCase.time is not None else 0
        return result


class JUnitReportGenerator:

    def generate(self, test_results: list[TestResult]) -> str:
        # transform to intermediary model
        testSuites: dict[str, JUnitTestSuite] = {}
        testSuite: JUnitTestSuite | None
        ts: float = 0
        for test_result in test_results:
            if test_result.stop_time is not None and ts < test_result.stop_time:
                ts = test_result.stop_time
            testSuite = testSuites.get(test_result.module_name)
            if testSuite is None:
                testSuite = JUnitTestSuite()
                testSuite.name = test_result.module_name
                testSuite.id = len(testSuites)
                testSuite.hostname = test_result.host_name
                testSuite.package = test_result.package_name
                testSuite.testCases = []
                testSuites[test_result.module_name] = testSuite
            if testSuite.testCases is None:
                testSuite.testCases = []
            testSuite.testCases.append(JUnitTestCase(test_result))
            testSuite.timestamp = datetime.datetime.fromtimestamp(ts)
        # materialize as xml
        totalDisabledCount = 0
        totalErrorCount = 0
        totalFailureCount = 0
        totalTestCount = 0
        totalTime: float = 0
        testSuitesEle: et.Element = et.Element('testsuites')
        for testSuiteName in testSuites:
            testSuite = testSuites[testSuiteName]
            if testSuite is not None:
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
                if testSuite.testCases is not None:
                    for testCase in testSuite.testCases:
                        testCaseEle = et.SubElement(testSuiteEle, 'testcase')
                        testCaseEle.attrib['name'] = testCase.name if testCase.name is not None else 'UNKNOWN'
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
        testSuitesEle.attrib['failures'] = str(totalFailureCount)
        testSuitesEle.attrib['tests'] = str(totalTestCount)
        testSuitesEle.attrib['time'] = f'{totalTime:.6f}'.rstrip('0').rstrip('.')
        et.indent(testSuitesEle, space="    ")
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{et.tostring(testSuitesEle).decode()}\n'
