# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import importlib
import inspect
import os
import socket
import time
import traceback
from types import ModuleType
from typing import Any, Optional

from .cli import CommandLineInterface
from .facts.FactManager import FactManager
from .setups.SetupManager import SetupManager
from .teardowns.TeardownManager import TeardownManager
from .theories.TheoryManager import TheoryManager
from .TestResult import TestResult


def _get_fails_reason(target: Any) -> str | None:
    """Return the ``__punit_fails_reason`` attribute, unwrapping decorators."""
    unwrapped = inspect.unwrap(target)
    if hasattr(unwrapped, '__punit_fails_reason'):
        return getattr(unwrapped, '__punit_fails_reason')
    return None


class TestRunner:

    __cli: CommandLineInterface
    __filenames: list[str]
    __test_package_name: str

    def __init__(self, test_package_name: str, filenames: list[str], cli: CommandLineInterface):
        self.__cli = cli
        self.__filenames = filenames
        self.__test_package_name = test_package_name

    async def __setup(self, module: object, module_name: str, class_name: Optional[str] = None, class_instance: Optional[Any] = None) -> bool:
        """Execute the setup for a test.

        Returns ``False`` if an error occurred during setup (the test should not run).
        A class-scoped ``@setup`` handles all tests in that specific class.
        A module-scoped ``@setup`` handles all bare-function tests in that module.
        The two scopes are independent -- there is no fallback between them; each scope fires only when it exists and the test belongs to it.
        """
        setup_manager = SetupManager.instance()

        if class_name is not None and len(class_name) > 0:
            # Class-scoped path -- this test lives inside a class
            sd = setup_manager.get('class', module_name, class_name)
            if sd is not None:
                try:
                    await sd.execute(module, class_instance)  # type: ignore[arg-type]
                except Exception as ex:
                    setup_manager.record_error()
                    if self.__cli.verbose:  # pragma: no cover
                        target_desc = (
                            f"{sd.metadata.class_name}.{sd.metadata.name}"
                            if sd.metadata.class_name
                            else sd.metadata.name
                        )
                        print(f'Setup Error ({target_desc}): {ex}')
                    return False
        else:
            # Module-scoped path -- this is a bare-function test
            sd = setup_manager.get('module', module_name, '')
            if sd is not None:
                try:
                    await sd.execute(module, class_instance)  # type: ignore[arg-type]
                except Exception as ex:
                    setup_manager.record_error()
                    if self.__cli.verbose:  # pragma: no cover
                        target_desc = (
                            f"{sd.metadata.class_name}.{sd.metadata.name}"
                            if sd.metadata.class_name
                            else sd.metadata.name
                        )
                        print(f'Setup Error ({target_desc}): {ex}')
                    return False
        return True

    async def __teardown(self, module: object, module_name: str, class_name: Optional[str] = None, class_instance: Optional[Any] = None) -> None:
        """Execute the teardown for a test.

        A class-scoped ``@teardown`` handles all tests in that specific class.
        A module-scoped ``@teardown`` handles all bare-function tests in that
        module.  The two scopes are independent -- there is no fallback between
        them; each scope fires only when it exists and the test belongs to it.
        """
        teardown_manager = TeardownManager.instance()

        if class_name is not None:
            # Class-scoped path -- this test lives inside a class
            td = teardown_manager.get('class', module_name, class_name)
            if td is not None:
                try:
                    await td.execute(module, class_instance)  # type: ignore[arg-type]
                except Exception as ex:
                    teardown_manager.record_error()
                    if self.__cli.verbose:  # pragma: no cover
                        target_desc = (
                            f"{td.metadata.class_name}.{td.metadata.name}"
                            if td.metadata.class_name
                            else td.metadata.name
                        )
                        print(f'Teardown Error ({target_desc}): {ex}')
        else:
            # Module-scoped path -- this is a bare-function test
            td = teardown_manager.get('module', module_name, '')
            if td is not None:
                try:
                    await td.execute(module, class_instance)  # type: ignore[arg-type]
                except Exception as ex:
                    teardown_manager.record_error()
                    if self.__cli.verbose:  # pragma: no cover
                        target_desc = (
                            f"{td.metadata.class_name}.{td.metadata.name}"
                            if td.metadata.class_name
                            else td.metadata.name
                        )
                        print(f'Teardown Error ({target_desc}): {ex}')

    def print_test_result(self, test_result: TestResult) -> None:
        """Print the test result using a coloured emoji and timing."""
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

    async def __run_facts(self, host_name: str, test_module: ModuleType, filename: str, module_report_name: str, results: list[TestResult]) -> None:
        """Run all facts for a test module and return their results."""
        facts = FactManager.instance().get(test_module.__name__)
        for fact in facts:
            result = TestResult()
            result.host_name = host_name
            result.package_name = self.__test_package_name
            result.file_name = filename
            result.module_name = module_report_name
            result.start_time = time.time()
            result.capture_output(False)
            # Run pre-test setup; if it fails, skip the fact.
            class_instance: Any = None
            if await self.__setup(test_module, test_module.__name__, fact.metadata.class_name, class_instance):
                try:
                    class_instance = await fact.execute(test_module)
                    result.is_success = True
                except Exception as ex:
                    result.is_success = False
                    result.exception = ex
            else:
                # Setup failed; record a failure result.
                result.is_success = False
            fails_reason = _get_fails_reason(fact.target)
            if fails_reason is not None:
                result.expected_failure_reason = fails_reason
                # Invert the result: a failing test with @fails counts as success,
                # and a passing test with @fails counts as failure (regression).
                result.is_success = not result.is_success
                # Set an exception so report generators can show the reason text.
                if not result.exception:
                    result.exception = RuntimeError(f'Unexpected pass ({fails_reason})')
            result.stop_time = time.time()
            result.class_name = fact.metadata.class_name
            result.test_name = fact.metadata.name
            results.append(result)
            await self.__teardown(test_module, test_module.__name__, result.class_name, class_instance)
            result.release_output()
            self.print_test_result(result)
            if self.__cli.failfast and not result.is_success:
                return

    async def __run_theories(self, host_name: str, test_module: ModuleType, filename: str, module_report_name: str, results: list[TestResult]) -> None:
        """Run all theory data-points for a test module and return their results."""
        theories = TheoryManager.instance().get(test_module.__name__)
        for theory in theories:
            for data in theory.datas:
                result = TestResult()
                result.host_name = host_name
                result.package_name = self.__test_package_name
                result.properties['data'] = data
                result.file_name = filename
                result.module_name = module_report_name
                result.start_time = time.time()
                result.capture_output(False)
                # Run pre-test setup; if it fails, skip the theory.
                class_instance: Any = None
                if await self.__setup(test_module, test_module.__name__, theory.metadata.class_name, class_instance):
                    try:
                        class_instance = await theory.execute(test_module, data)
                        result.is_success = True
                    except Exception as ex:
                        result.is_success = False
                        result.exception = ex
                else:
                    # Setup failed; record a failure result.
                    result.is_success = False
                fails_reason = _get_fails_reason(theory.target)
                if fails_reason is not None:
                    result.is_expected_failure = True
                    result.expected_failure_reason = fails_reason
                    # Invert the result: a failing test with @fails counts as success,
                    # and a passing test with @fails counts as failure (regression).
                    result.is_success = not result.is_success
                    # Set an exception so report generators can show the reason text.
                    if not result.exception:
                        result.exception = RuntimeError(f'Unexpected pass ({fails_reason})')
                result.stop_time = time.time()
                result.class_name = theory.metadata.class_name
                result.test_name = theory.metadata.name
                results.append(result)
                await self.__teardown(test_module, test_module.__name__, result.class_name, class_instance)
                result.release_output()
                self.print_test_result(result)
                if self.__cli.failfast and not result.is_success:
                    return

    async def run(self) -> list[TestResult]:
        results: list[TestResult] = []
        result: TestResult
        # TODO: aliasing
        test_package_path = os.path.join(os.path.abspath(os.curdir), self.__test_package_name).replace('\\', '/')
        for filename in self.__filenames:
            ts = time.time()
            module_import_name = filename.replace(test_package_path, '').replace('/', '.')
            if module_import_name.endswith('.py'):
                module_import_name = module_import_name[:-3]
            module_report_name = module_import_name.lstrip('.')
            try:
                host_name: str = socket.gethostname()
                test_module = importlib.import_module(module_import_name, self.__test_package_name)

                # execute all facts
                await self.__run_facts(host_name, test_module, filename, module_report_name, results)
                if self.__cli.failfast and any(e.is_success is False for e in results):
                    return results

                # execute all theories
                await self.__run_theories(host_name, test_module, filename, module_report_name, results)
                if self.__cli.failfast and any(e.is_success is False for e in results):
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
