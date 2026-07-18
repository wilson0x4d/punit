# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
Parallelism for pUnit.

pUnit provides three mechanisms for controlling test execution parallelism:
the **``--parallel [THREADS]``** CLI flag, the **``@parallel``** decorator,
and the **``@sequential``** decorator.

CLI flag
--------
The ``--parallel [THREADS]`` option enables multi-threaded parallel execution.
Each worker thread runs its own asyncio event loop for isolation.

* ``--parallel`` (bare flag, no number) runs tests using
  ``cpu_count // 2`` workers.
* ``--parallel N`` runs tests using *N* workers.
* No flag means tests run sequentially, one after another.

When parallel mode is active the runner processes each test file in four
batches: parallel facts, parallel theories, sequential facts, then
sequential theories.

@parallel decorator
-------------------
Marking a fact or theory with ``@parallel`` triggers **auto-enable** mode.
When pUnit scans the test package and finds at least one ``@parallel``
decorated test (and no ``--parallel`` flag was given on the CLI):

* Parallel execution is enabled automatically with
  ``cpu_count // 2`` workers.
* **Only** ``@parallel``-marked tests run in the concurrent batch.
* All other tests are treated as sequential (as if they carried ``@sequential``).

Applying ``@parallel`` to a **class** marks every method of that class.

``@parallel`` is a no-op when ``--parallel`` is specified on the CLI; the
CLI flag takes full priority.

@sequential decorator
---------------------
Marking a fact or theory with ``@sequential`` forces it to run as a
sequential test **after** all parralel tests for that file have
completed.  This lets you co-run certain tests one-at-a-time inside
an otherwise parallel test suite (for example, tests that share mutable
state).

When no ``@parallel`` decorator is present and ``--parallel`` is not used
on the CLI, all tests run sequentially (the default).

Examples
--------

Enable parallel mode for the entire test package via CLI::

    punit tests/ --parallel 4

Run only selected tests in parallel -- no CLI flag needed::

    from punit import fact, parallel

    @fact
    @parallel
    def test_network_io():
        ...

    @fact
    def test_database_setup():
        # Runs sequentially alongside the parallel tests
        ...

Mix parallel and sequential tests inside a parallel suite::

    from punit import fact, parallel, sequential

    @parallel
    class SlowTests:
        @fact
        def test_heavy_computation(self):
            ...

        @fact
        @sequential
        def test_shared_file_handle(self):
            # Runs one-at-a-time after all other SlowTests finish
            ...

"""

from __future__ import annotations

import asyncio
import inspect
import queue
import threading
import time
from types import ModuleType
from typing import Any, Callable

from .TestResult import TestResult


class _TaskInfo:
    """Internal holder for a dispatched coroutine and its completion state."""

    __slots__ = ("coro", "event", "result", "exception")

    def __init__(self, coro: Any) -> None:
        self.coro: Any = coro
        self.event: threading.Event = threading.Event()
        self.result: Any = None
        self.exception: BaseException | None = None


class ThreadPool:
    """
    Manages a pool of worker threads, each with its own asyncio event loop.

    The pool follows the context-manager protocol: ``__enter__`` starts the
    pool, ``__exit__`` waits for all in-flight work to finish and shuts down
    the workers.

    Parameters
    ----------
    parallelism : int
        Maximum number of tasks to run in parallel.  This also equals the
        number of worker threads.  Must be at least 1.
    """

    def __init__(self, parallelism: int) -> None:
        if parallelism < 1:
            raise ValueError("parallelism must be at least 1")
        self._parallelism: int = parallelism
        self._loops: list[asyncio.AbstractEventLoop] = []
        self._queues: list[queue.Queue[_TaskInfo | None]] = []
        self._counter: int = 0
        self._lock: threading.Lock = threading.Lock()
        self._workers: list[threading.Thread] = []

    def __enter__(self) -> ThreadPool:
        for _ in range(self._parallelism):
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
    data: tuple[Any, ...],
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


def sequential(target: Callable[..., Any] | type) -> Callable[..., Any]:
    """Mark a test function, method, or class for **sequential** execution.

    When pUnit is started with ``--parallel THREADS`` (where *THREADS* > 1),
    tests decorated without ``@sequential`` run in parallel up to *N* at
    any given point.  ``@sequential`` tests are **not** added to the
    concurrent dispatch queue -- after all peers at the same scope finish
    concurrently, the sequential tests run one after another in their
    definition order.

    When applied to a **class**, all methods of the class are automatically
    marked as sequential.

    The decorator returns the original ``target`` unchanged; it installs the
    ``__punit_sequential`` marker attribute on the unwrapped function (or the
    class object itself for class targets).

    Parameters
    ----------
    target : Callable | type
        The test function, method, or class to mark.

    Returns
    -------
    Callable
        The original, undecorated target.

    Example
    -------

    .. code-block:: python

        from punit import fact, sequential

        @fact
        @sequential
        def my_test():
            assert True

        class MyTestCase:
            @fact
            @sequential
            def test_one(self):
                assert True

        # Apply @sequential to an entire class -- all methods run sequentially
        @sequential
        class SequentialTestCase:
            @fact
            def test_one(self):
                assert True

            @fact
            def test_two(self):
                assert True

    """
    import inspect

    if isinstance(target, type):
        setattr(target, "__punit_sequential", True)
        for name, method in inspect.getmembers(target, predicate=inspect.isfunction):
            setattr(method, "__punit_sequential", True)
        return target

    unwrapped = inspect.unwrap(target)
    setattr(unwrapped, "__punit_sequential", True)
    return target


def parallel(target: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a test function, method, or class for **parallel** execution.

    When pUnit detects any ``@parallel``-decorated tests in a test package at
    runtime, it automatically triggers (multi-threaded) parallel execution for
    the entire test run -- no ``--parallel`` CLI flag is required.

    When ``@parallel`` triggers auto-enable:

    * Only tests marked with ``@parallel`` run in the parallel batch
    * Tests not marked with ``@parallel`` are treated as sequential
      (as if decorated with ``@sequential``)
    * The thread pool is initialized with ``cpu_count // 2`` workers
    * This auto-enable is superseded by ``--parallel`` on the CLI

    When ``--parallel`` is specified on the CLI, this decorator has no effect;
    the existing ``--parallel`` behavior takes priority and all
    non-``@sequential`` tests run in parallel as before.

    When applied to a class, all methods of the class are automatically marked
    as parallel.

    The decorator returns the original ``target`` unchanged; it installs the
    ``__punit_parallel`` marker attribute on the unwrapped function (or the
    class object itself for class targets).

    Parameters
    ----------
    target : Callable | type
        The test function, method, or class to mark.

    Returns
    -------
    Callable
        The original, undecorated target.

    Example
    -------

    .. code-block:: python

        from punit import fact, parallel

        @fact
        @parallel
        def my_parallel_test():
            assert True

        class ParallelTestCase:
            @fact
            @parallel
            def test_one(self):
                assert True

            @fact
            def test_sequential(self):
                # Runs sequentially (not in parallel batch)
                assert True

    """
    import inspect

    if isinstance(target, type):
        setattr(target, "__punit_parallel", True)
        for name, method in inspect.getmembers(target, predicate=inspect.isfunction):
            setattr(method, "__punit_parallel", True)
        return target

    unwrapped = inspect.unwrap(target)
    setattr(unwrapped, "__punit_parallel", True)
    return target


__all__ = [
    'ThreadPool',
    'parallel',
    'sequential'
]
