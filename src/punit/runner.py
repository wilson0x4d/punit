# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
import importlib
import inspect
import os
import socket
import time
import traceback
from types import ModuleType
from typing import Any, Callable, Optional

from .TextIOCapture import setup_global_text_io, _PERSISTENT_STDOUT, _PERSISTENT_STDERR
from .cli import CommandLineInterface
from .parallelism import ThreadPool, _execute_fact, _execute_theory
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


def _get_skip_condition(target: Any) -> bool | Callable[..., bool] | None:
    """Return the ``__punit_skip_condition`` attribute, unwrapping decorators."""
    unwrapped = inspect.unwrap(target)
    if hasattr(unwrapped, '__punit_skip_condition'):
        return getattr(unwrapped, '__punit_skip_condition')
    return None


def _is_sequential(target: Any) -> bool:
    """Return True if *target* is marked with ``@sequential``."""
    unwrapped = inspect.unwrap(target)
    return getattr(unwrapped, '__punit_sequential', None) is True


def _is_parallel(target: Any) -> bool:
    """Return True if *target* is marked with ``@parallel``."""
    unwrapped = inspect.unwrap(target)
    return getattr(unwrapped, '__punit_parallel', None) is True


def _get_parallelism(cli: 'CommandLineInterface') -> int:
    """Resolve the parallelism level from CLI.

    Returns ``-1`` when parallelism is disabled (use sequential flow).
    Returns the worker count when enabled; ``0`` maps to ``cpu_count // 2``.
    """
    parallelism = cli.parallelism
    if parallelism is None:
        return -1
    if parallelism <= 0:
        cores = os.cpu_count() or 1
        return max(1, cores // 2)
    return parallelism


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
        glyph = '🟨' if test_result.is_skip else '🟩' if test_result.is_success else '🟥'
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

    def __detect_parallel_tests(self) -> bool:
        """Return True if any registered fact or theory is marked with ``@parallel``."""
        fm = FactManager.instance()
        modules = getattr(fm, '_FactManager__modules', {})
        for facts in modules.values():
            for fact in facts:
                if _is_parallel(fact.target):
                    return True
        tm = TheoryManager.instance()
        modules = getattr(tm, '_TheoryManager__modules', {})
        for theories in modules.values():
            for theory in theories:
                if _is_parallel(theory.target):
                    return True
        return False

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
            result.capture_output()
            try:
                class_instance: Any = None
                skip_condition = _get_skip_condition(fact.target)
                skipped: bool = False
                if skip_condition is not None:
                    if callable(skip_condition):
                        if skip_condition():
                            skipped = True
                    else:
                        skipped = skip_condition is True

                if skipped:
                    result.is_skip = True
                    result.is_success = True
                elif await self.__setup(test_module, test_module.__name__, fact.metadata.class_name, class_instance):
                    try:
                        class_instance = await fact.execute(test_module)
                        result.is_success = True
                    except Exception as ex:
                        result.is_success = False
                        result.exception = ex
                else:
                    result.is_success = False
                fails_reason = _get_fails_reason(fact.target)
                if fails_reason is not None:
                    result.expected_failure_reason = fails_reason
                    result.is_success = not result.is_success
                    if not result.exception:
                        result.exception = RuntimeError(f'Unexpected pass ({fails_reason})')
                result.stop_time = time.time()
                result.class_name = fact.metadata.class_name
                result.test_name = fact.metadata.name
                results.append(result)
                await self.__teardown(test_module, test_module.__name__, result.class_name, class_instance)
            finally:
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
                result.capture_output()
                try:
                    class_instance: Any = None
                    skip_condition = _get_skip_condition(theory.target)
                    skipped: bool = False
                    if skip_condition is not None:
                        if callable(skip_condition):
                            if skip_condition():
                                skipped = True
                        else:
                            skipped = skip_condition is True

                    if skipped:
                        result.is_skip = True
                        result.is_success = True
                    elif await self.__setup(test_module, test_module.__name__, theory.metadata.class_name, class_instance):
                        try:
                            class_instance = await theory.execute(test_module, data)
                            result.is_success = True
                        except Exception as ex:
                            result.is_success = False
                            result.exception = ex
                    else:
                        result.is_success = False
                    fails_reason = _get_fails_reason(theory.target)
                    if fails_reason is not None:
                        result.is_expected_failure = True
                        result.expected_failure_reason = fails_reason
                        result.is_success = not result.is_success
                        if not result.exception:
                            result.exception = RuntimeError(f'Unexpected pass ({fails_reason})')
                    result.stop_time = time.time()
                    result.class_name = theory.metadata.class_name
                    result.test_name = theory.metadata.name
                    results.append(result)
                    await self.__teardown(test_module, test_module.__name__, result.class_name, class_instance)
                finally:
                    result.release_output()
                self.print_test_result(result)
                if self.__cli.failfast and not result.is_success:
                    return

    async def run(self) -> list[TestResult]:
        results: list[TestResult] = []
        result: TestResult
        # TODO: aliasing
        # Install persistent TextIO captures so both serial and parallel
        # paths dispatch writes to the correct task-local receivers.
        setup_global_text_io()
        # Set quiet passthrough on the global captures based on CLI
        _PERSISTENT_STDOUT.quiet = self.__cli.quiet
        _PERSISTENT_STDERR.quiet = self.__cli.quiet
        test_package_path = os.path.join(os.path.abspath(os.curdir), self.__test_package_name).replace('\\', '/')
        parallelism = _get_parallelism(self.__cli)

        if parallelism > 0:
            return await self._run_parallel(results, test_package_path)

        # Auto-enable parallel mode when @parallel-decorated tests are detected
        has_parallel_tests = self.__detect_parallel_tests()
        if has_parallel_tests:
            cores = os.cpu_count() or 1
            parallelism = max(1, cores // 2)
            await self._run_parallel_parallel_only(results, test_package_path, parallelism)
            return results

        for filename in self.__filenames:
            ts = time.time()
            if not self.__test_package_name:
                module_import_name = filename
            else:
                module_import_name = filename.replace(test_package_path, '').replace('/', '.')
                if module_import_name.endswith('.py'):
                    module_import_name = module_import_name[:-3]
            module_report_name = module_import_name.lstrip('.')
            try:
                host_name: str = socket.gethostname()
                if not self.__test_package_name:
                    test_module = importlib.import_module(module_import_name)
                else:
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

    # ------------------------------------------------------------------
    # Parallel execution
    # ------------------------------------------------------------------

    async def _run_parallel_parallel_only(
        self,
        results: list[TestResult],
        test_package_path: str,
        parallelism: int,
    ) -> None:
        """Execute ``@parallel``-decorated tests in a worker pool, rest sequentially.

        This is used when ``@parallel`` decorators are detected at runtime and
        no ``--parallel`` CLI flag was provided: only tests marked with
        ``@parallel`` go into the parallel batch, everything else runs one-by-one.
        """
        try:
            pool = ThreadPool(parallelism)
            with pool:
                module_report_name = ''
                for filename in self.__filenames:
                    try:
                        if not self.__test_package_name:
                            module_import_name = filename
                        else:
                            module_import_name = filename.replace(test_package_path, '').replace('/', '.')
                            if module_import_name.endswith('.py'):
                                module_import_name = module_import_name[:-3]
                        module_report_name = module_import_name.lstrip('.')
                        if not self.__test_package_name:
                            test_module = importlib.import_module(module_import_name)
                        else:
                            test_module = importlib.import_module(module_import_name, self.__test_package_name)
                        host_name = socket.gethostname()

                        await self._run_parallel_facts_parallel_only(host_name, test_module, filename, module_report_name, results, pool)
                        if self.__cli.failfast and any(e.is_success is False for e in results):
                            break

                        await self._run_parallel_theories_parallel_only(host_name, test_module, filename, module_report_name, results, pool)
                        if self.__cli.failfast and any(e.is_success is False for e in results):
                            break

                        facts = FactManager.instance().get(test_module.__name__)
                        for fact in facts:
                            if _is_parallel(fact.target):
                                continue
                            test_result = await _execute_fact(fact, test_module, module_report_name, filename, host_name, self.__test_package_name)
                            results.append(test_result)
                            self.print_test_result(test_result)
                            if self.__cli.failfast and not test_result.is_success:
                                return

                        theories = TheoryManager.instance().get(test_module.__name__)
                        for theory in theories:
                            if _is_parallel(theory.target):
                                continue
                            for data in theory.datas:
                                test_result = await _execute_theory(theory, data, test_module, module_report_name, filename, host_name, self.__test_package_name)
                                results.append(test_result)
                                self.print_test_result(test_result)
                                if self.__cli.failfast and not test_result.is_success:
                                    return

                    except Exception as ex:
                        result = TestResult()
                        result.class_name = '*'
                        result.module_name = module_report_name
                        result.test_name = '*'
                        result.start_time = time.time()
                        result.stop_time = time.time()
                        result.is_success = False
                        result.exception = ex
                        results.append(result)
                        self.print_test_result(result)
                        if self.__cli.failfast:
                            break
        except Exception:
            pass

    async def _run_parallel(self, results: list[TestResult], test_package_path: str) -> list[TestResult]:
        """Execute all tests with a worker pool (each worker has its own event loop)."""
        parallelism = _get_parallelism(self.__cli)
        pool: ThreadPool | None = None
        try:
            pool = ThreadPool(parallelism)
            with pool:
                module_report_name = ''
                for filename in self.__filenames:
                    try:
                        if not self.__test_package_name:
                            module_import_name = filename
                        else:
                            module_import_name = filename.replace(test_package_path, '').replace('/', '.')
                            if module_import_name.endswith('.py'):
                                module_import_name = module_import_name[:-3]
                        module_report_name = module_import_name.lstrip('.')
                        if not self.__test_package_name:
                            test_module = importlib.import_module(module_import_name)
                        else:
                            test_module = importlib.import_module(module_import_name, self.__test_package_name)
                        host_name = socket.gethostname()

                        await self._run_parallel_facts(host_name, test_module, filename, module_report_name, results, pool)
                        if self.__cli.failfast and any(e.is_success is False for e in results):
                            break

                        await self._run_parallel_theories(host_name, test_module, filename, module_report_name, results, pool)
                        if self.__cli.failfast and any(e.is_success is False for e in results):
                            break

                        await self._run_sequential_facts(host_name, test_module, filename, module_report_name, results, pool)
                        await self._run_sequential_theories(host_name, test_module, filename, module_report_name, results, pool)

                    except Exception as ex:
                        result = TestResult()
                        result.class_name = '*'
                        result.module_name = module_report_name
                        result.test_name = '*'
                        result.start_time = time.time()
                        result.stop_time = time.time()
                        result.is_success = False
                        result.exception = ex
                        results.append(result)
                        self.print_test_result(result)
                        if self.__cli.failfast:
                            break
        except Exception:
            pass
        return results

    async def _run_parallel_facts(
        self,
        host_name: str,
        test_module: ModuleType,
        filename: str,
        module_report_name: str,
        results: list[TestResult],
        pool: ThreadPool
    ) -> None:
        """Run non-sequential facts in parallel via thread pool."""
        facts = FactManager.instance().get(test_module.__name__)
        coros: list[Any] = []
        for fact in facts:
            if _is_sequential(fact.target):
                continue
            coro = _execute_fact(fact, test_module, module_report_name, filename, host_name, self.__test_package_name)
            coros.append(coro)
        if coros:
            test_results = await asyncio.gather(*coros)
            for test_result in test_results:
                results.append(test_result)
                self.print_test_result(test_result)
                if self.__cli.failfast and not test_result.is_success:
                    return

    async def _run_parallel_theories(
        self,
        host_name: str,
        test_module: ModuleType,
        filename: str,
        module_report_name: str, results: list[TestResult],
        pool: ThreadPool
    ) -> None:
        """Run non-sequential theory data-points concurrently."""
        theories = TheoryManager.instance().get(test_module.__name__)
        coros: list[Any] = []
        for theory in theories:
            for data in theory.datas:
                if _is_sequential(theory.target):
                    continue
                coro = _execute_theory(theory, data, test_module, module_report_name, filename, host_name, self.__test_package_name)
                coros.append(coro)
        if coros:
            test_results = await asyncio.gather(*coros)
            for test_result in test_results:
                results.append(test_result)
                self.print_test_result(test_result)
                if self.__cli.failfast and not test_result.is_success:
                    return

    async def _run_sequential_facts(
        self,
        host_name: str,
        test_module: ModuleType,
        filename: str,
        module_report_name: str,
        results: list[TestResult],
        pool: ThreadPool
    ) -> None:
        """Run @sequential facts sequentially."""
        facts = FactManager.instance().get(test_module.__name__)
        for fact in facts:
            if not _is_sequential(fact.target):
                continue
            test_result = await _execute_fact(fact, test_module, module_report_name, filename, host_name, self.__test_package_name)
            results.append(test_result)
            self.print_test_result(test_result)
            if self.__cli.failfast and not test_result.is_success:
                return

    async def _run_sequential_theories(
        self,
        host_name: str,
        test_module: ModuleType,
        filename: str,
        module_report_name: str,
        results: list[TestResult],
        pool: ThreadPool
    ) -> None:
        """Run @sequential theory data-points sequentially."""
        theories = TheoryManager.instance().get(test_module.__name__)
        for theory in theories:
            if not _is_sequential(theory.target):
                continue
            for data in theory.datas:
                test_result = await _execute_theory(theory, data, test_module, module_report_name, filename, host_name, self.__test_package_name)
                results.append(test_result)
                self.print_test_result(test_result)
                if self.__cli.failfast and not test_result.is_success:
                    return

    async def _run_parallel_facts_parallel_only(
        self,
        host_name: str,
        test_module: ModuleType,
        filename: str,
        module_report_name: str,
        results: list[TestResult],
        pool: ThreadPool
    ) -> None:
        """Run @parallel facts in parallel (auto-enable mode)."""
        facts = FactManager.instance().get(test_module.__name__)
        coros: list[Any] = []
        for fact in facts:
            if not _is_parallel(fact.target):
                continue
            coro = _execute_fact(fact, test_module, module_report_name, filename, host_name, self.__test_package_name)
            coros.append(coro)
        if coros:
            test_results = await asyncio.gather(*coros)
            for test_result in test_results:
                results.append(test_result)
                self.print_test_result(test_result)
                if self.__cli.failfast and not test_result.is_success:
                    return

    async def _run_parallel_theories_parallel_only(
        self,
        host_name: str,
        test_module: ModuleType,
        filename: str,
        module_report_name: str,
        results: list[TestResult],
        pool: ThreadPool
    ) -> None:
        """Run @parallel theory data-points in parallel (auto-enable mode)."""
        theories = TheoryManager.instance().get(test_module.__name__)
        coros: list[Any] = []
        for theory in theories:
            if not _is_parallel(theory.target):
                continue
            for data in theory.datas:
                coro = _execute_theory(theory, data, test_module, module_report_name, filename, host_name, self.__test_package_name)
                coros.append(coro)
        if coros:
            test_results = await asyncio.gather(*coros)
            for test_result in test_results:
                results.append(test_result)
                self.print_test_result(test_result)
                if self.__cli.failfast and not test_result.is_success:
                    return
