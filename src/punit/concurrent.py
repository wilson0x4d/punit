# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Concurrent test execution infrastructure for pUnit.

Provides a pool of worker threads, each with its own asyncio event loop,
for executing tests in parallel.

Each test is wrapped in a coroutine that creates a ``TestResult``, runs
setup -> test -> teardown, and yields the populated result.  The main thread
dispatches these coroutines to worker threads and collects the results.
"""

from __future__ import annotations

import asyncio
import inspect
import os
import queue
import sys
import threading
import time
from types import ModuleType
from typing import Any

from .TestResult import TestResult


class _TaskInfo:
    """Internal holder for a dispatched coroutine and its completion state."""

    __slots__ = ("coro", "event", "result", "exception")

    def __init__(self, coro: Any) -> None:
        self.coro: Any = coro
        self.event: threading.Event = threading.Event()
        self.result: Any = None
        self.exception: BaseException | None = None


class ConcurrentPool:
    """
    Manages a pool of worker threads, each with its own asyncio event loop.

    The pool follows the context-manager protocol: ``__enter__`` starts the
    pool, ``__exit__`` waits for all in-flight work to finish and shuts down
    the workers.

    Parameters
    ----------
    concurrency : int
        Maximum number of tasks to run concurrently.  This also equals the
        number of worker threads.  Must be at least 1.
    """

    def __init__(self, concurrency: int) -> None:
        if concurrency < 1:
            raise ValueError("concurrency must be at least 1")
        self._concurrency: int = concurrency
        self._loops: list[asyncio.AbstractEventLoop] = []
        self._queues: list[queue.Queue[_TaskInfo | None]] = []
        self._counter: int = 0
        self._lock: threading.Lock = threading.Lock()
        self._workers: list[threading.Thread] = []

    def __enter__(self) -> ConcurrentPool:
        for _ in range(self._concurrency):
            loop = asyncio.new_event_loop()
            q: queue.Queue[_TaskInfo | None] = queue.Queue()
            self._loops.append(loop)
            self._queues.append(q)
            t = threading.Thread(
                target=self._worker_loop,
                args=(loop, q),
                daemon=True,
                name=f"punit-worker-{len(self._workers)}",
            )
            self._workers.append(t)
            t.start()
        return self

    def __exit__(self, *args: Any) -> None:
        for q in self._queues:
            q.put(None)
        for t in self._workers:
            t.join(timeout=60)
        for loop in self._loops:
            if loop.is_running():
                try:
                    loop.call_soon_threadsafe(loop.stop)
                except RuntimeError:
                    pass

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    def _worker_loop(
        self,
        loop: asyncio.AbstractEventLoop,
        q: queue.Queue[_TaskInfo | None],
    ) -> None:
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._drain_queue(loop, q))
        finally:
            try:
                loop.close()
            except Exception:
                pass

    async def _drain_queue(
        self,
        loop: asyncio.AbstractEventLoop,
        q: queue.Queue[_TaskInfo | None],
    ) -> None:
        while True:
            task = await loop.run_in_executor(None, q.get)
            if task is None:
                return
            try:
                await task.coro
            except BaseException as ex:
                task.exception = ex
            finally:
                task.event.set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dispatch(self, coro: Any) -> _TaskInfo:
        """
        Dispatch *coro* to be executed on a worker thread.

        Returns a ``_TaskInfo`` that can be checked with :py:meth:`wait`.
        """
        with self._lock:
            idx = self._counter % len(self._queues)
            self._counter += 1
        task = _TaskInfo(coro)
        self._queues[idx].put(task)
        return task

    def wait(self, task: _TaskInfo, timeout: float | None = None) -> None:
        """Block until *task*'s coroutine has completed."""
        task.event.wait(timeout=timeout)


async def _execute_fact(
    fact: Any,
    module: ModuleType,
    module_report_name: str,
    filename: str,
    host_name: str,
    package_name: str | None,
) -> TestResult:
    """Execute a single Fact and return a populated TestResult."""
    result = TestResult()
    result.host_name = host_name
    result.package_name = package_name or ''
    result.file_name = filename
    result.module_name = module_report_name
    result.start_time = time.time()
    result.capture_output()

    class_instance: Any = None
    try:
        md = fact.metadata
        unwrapped = inspect.unwrap(fact.target)

        # -- skip check --
        skip_cond = getattr(unwrapped, '__punit_skip_condition', None)
        skipped = False
        if skip_cond is not None:
            if callable(skip_cond):
                try:
                    if skip_cond():
                        skipped = True
                except Exception:
                    pass
            elif skip_cond is True:
                skipped = True
        if skipped:
            result.is_skip = True
            result.is_success = True
            return result

        # -- setup --
        scope = 'class' if (md.class_name and len(md.class_name) > 0) else 'module'
        from .setups.SetupManager import SetupManager
        sd = SetupManager.instance().get(scope, module.__name__, md.class_name or '')
        if sd is not None:
            try:
                coro = sd.execute(module, class_instance)
                if inspect.iscoroutine(coro):
                    await coro
            except Exception:
                result.is_success = False
                result.stop_time = time.time()
                return result

        # -- test --
        try:
            class_instance = await fact.execute(module)
            result.is_success = True
        except Exception as ex:
            result.is_success = False
            result.exception = ex

        # -- fails inversion --
        fails_reason = getattr(unwrapped, '__punit_fails_reason', None)
        if fails_reason is not None:
            result.is_success = not result.is_success
            if not result.exception:
                result.exception = RuntimeError(f'Unexpected pass ({fails_reason})')

        result.stop_time = time.time()
        result.class_name = md.class_name
        result.test_name = md.name

    finally:
        # -- teardown --
        if result.is_success is not None:
            md = fact.metadata
            scope = 'class' if (md.class_name and len(md.class_name) > 0) else 'module'
            from .teardowns.TeardownManager import TeardownManager
            td = TeardownManager.instance().get(scope, module.__name__, md.class_name or '')
            if td is not None:
                try:
                    coro = td.execute(module, class_instance)
                    if inspect.iscoroutine(coro):
                        await coro
                except Exception:
                    pass
        result.release_output()

    return result


async def _execute_theory(
    theory: Any,
    data: tuple,
    module: ModuleType,
    module_report_name: str,
    filename: str,
    host_name: str,
    package_name: str | None,
) -> TestResult:
    """Execute a single theory data-point and return a populated TestResult."""
    result = TestResult()
    result.host_name = host_name
    result.package_name = package_name or ''
    result.file_name = filename
    result.module_name = module_report_name
    result.properties['data'] = data
    result.start_time = time.time()
    result.capture_output()

    class_instance: Any = None
    try:
        md = theory.metadata
        unwrapped = inspect.unwrap(theory.target)

        # -- skip check --
        skip_cond = getattr(unwrapped, '__punit_skip_condition', None)
        skipped = False
        if skip_cond is not None:
            if callable(skip_cond):
                try:
                    if skip_cond():
                        skipped = True
                except Exception:
                    pass
            elif skip_cond is True:
                skipped = True
        if skipped:
            result.is_skip = True
            result.is_success = True
            return result

        # -- setup --
        scope = 'class' if (md.class_name and len(md.class_name) > 0) else 'module'
        from .setups.SetupManager import SetupManager
        sd = SetupManager.instance().get(scope, module.__name__, md.class_name or '')
        if sd is not None:
            try:
                coro = sd.execute(module, class_instance)
                if inspect.iscoroutine(coro):
                    await coro
            except Exception:
                result.is_success = False
                result.stop_time = time.time()
                return result

        # -- test --
        try:
            class_instance = await theory.execute(module, data)
            result.is_success = True
        except Exception as ex:
            result.is_success = False
            result.exception = ex

        # -- fails inversion --
        fails_reason = getattr(unwrapped, '__punit_fails_reason', None)
        if fails_reason is not None:
            result.is_success = not result.is_success
            if not result.exception:
                result.exception = RuntimeError(f'Unexpected pass ({fails_reason})')

        result.stop_time = time.time()
        result.class_name = md.class_name
        result.test_name = md.name

    finally:
        # -- teardown --
        if result.is_success is not None:
            md = theory.metadata
            scope = 'class' if (md.class_name and len(md.class_name) > 0) else 'module'
            from .teardowns.TeardownManager import TeardownManager
            td = TeardownManager.instance().get(scope, module.__name__, md.class_name or '')
            if td is not None:
                try:
                    coro = td.execute(module, class_instance)
                    if inspect.iscoroutine(coro):
                        await coro
                except Exception:
                    pass
        result.release_output()

    return result
