# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import sys
from typing import Any, Optional, Tuple

from .TextIOCapture import (
    TextIOReceiver,
    _TextIOCapture,
    _clear_receivers,
    _PERSISTENT_STDOUT,
    _PERSISTENT_STDERR,
    _set_receivers,
)


class TestResult:
    """
    Accumulates the outcome of a single test execution.

    Example
    -------

    Create and populate a result manually:

    .. code-block:: python

        result = TestResult()
        result.module_name = 'tests.example'
        result.test_name = 'test_something'
        result.is_success = True

    """

    __class_name: Optional[str]
    __exception: Exception | None
    __file_name: str | None
    __host_name: str | None
    __expected_failure_reason: str | None
    __is_success: bool | None
    __is_skip: bool
    __module_name: str | None
    __package_name: str | None
    __properties: dict[str, Any]
    __start_time: float | None
    __stdout_receiver: TextIOReceiver | None
    __stderr_receiver: TextIOReceiver | None
    __stop_time: float | None
    __test_name: str | None

    def __init__(self) -> None:
        self.__class_name = None
        self.__exception = None
        self.__file_name = None
        self.__host_name = None
        self.__expected_failure_reason = None
        self.__is_success = None
        self.__is_skip = False
        self.__module_name = None
        self.__package_name = None
        self.__properties = dict[str, Any]()
        self.__start_time = None
        self.__stdout_receiver = None
        self.__stderr_receiver = None
        self.__stop_time = None
        self.__test_name = None

    @property
    def class_name(self) -> Optional[str]:
        return (
            self.__class_name
            if self.__class_name is not None and len(self.__class_name) > 0
            else None
        )

    @class_name.setter
    def class_name(self, value: Optional[str]) -> None:
        self.__class_name = value

    @property
    def expected_failure_reason(self) -> str | None:
        return self.__expected_failure_reason

    @expected_failure_reason.setter
    def expected_failure_reason(self, value: str | None) -> None:
        self.__expected_failure_reason = value

    @property
    def exception(self) -> Exception | None:
        return self.__exception

    @exception.setter
    def exception(self, value: Exception) -> None:
        self.__exception = value

    @property
    def file_name(self) -> str | None:
        return self.__file_name

    @file_name.setter
    def file_name(self, value: str) -> None:
        self.__file_name = value

    @property
    def host_name(self) -> str | None:
        return self.__host_name

    @host_name.setter
    def host_name(self, value: str) -> None:
        self.__host_name = value

    @property
    def is_expected_failure(self) -> bool:
        """Deprecated: use ``expected_failure_reason is not None`` instead."""
        return self.expected_failure_reason is not None

    @is_expected_failure.setter
    def is_expected_failure(self, value: bool) -> None:
        # Deprecated no-op; consumers should set expected_failure_reason directly.
        pass

    @property
    def is_success(self) -> bool:
        return False if self.__is_success is None else self.__is_success

    @is_success.setter
    def is_success(self, value: bool) -> None:
        self.__is_success = value

    @property
    def is_skip(self) -> bool:
        return self.__is_skip

    @is_skip.setter
    def is_skip(self, value: bool) -> None:
        self.__is_skip = value

    @property
    def module_name(self) -> str | None:
        return self.__module_name

    @module_name.setter
    def module_name(self, value: str) -> None:
        self.__module_name = value

    @property
    def package_name(self) -> str | None:
        return self.__package_name

    @package_name.setter
    def package_name(self, value: str) -> None:
        self.__package_name = value

    @property
    def properties(self) -> dict[str, Any]:
        return self.__properties

    @properties.setter
    def properties(self, value: dict[str, str]) -> None:
        self.__properties = value

    @property
    def start_time(self) -> float | None:
        return self.__start_time

    @start_time.setter
    def start_time(self, value: float) -> None:
        self.__start_time = value

    @property
    def stderr(self) -> str | None:
        return None if self.__stderr_receiver is None else self.__stderr_receiver.output

    @property
    def stdout(self) -> str | None:
        return None if self.__stdout_receiver is None else self.__stdout_receiver.output

    @property
    def stop_time(self) -> float | None:
        return self.__stop_time

    @stop_time.setter
    def stop_time(self, value: float) -> None:
        self.__stop_time = value

    @property
    def test_name(self) -> str | None:
        return self.__test_name

    @test_name.setter
    def test_name(self, value: str) -> None:
        self.__test_name = value

    @property
    def took(self) -> float | None:
        return None if self.__stop_time is None or self.__start_time is None else self.__stop_time - self.__start_time

    @property
    def tookPretty(self) -> str:
        took = self.took
        if took is None:
            return 'N/A'
        elif took >= 1:
            return f'{took:.1f}'.rstrip('0').rstrip('.') + 's'
        elif took >= 0.001:
            return f'{(took*1000):.0f}ms'
        elif took >= 0.000001:
            return f'{(took*1000):.3f}'.rstrip('0').rstrip('.') + 'ms'
        elif took >= 0.000000001:
            return f'{(took*1000000):.3f}'.rstrip('0').rstrip('.') + 'μs'
        else:
            return f'{(took*1000000):.3f}'.rstrip('0').rstrip('.') + 'ns'

    def capture_output(self) -> None:
        """Prepare output capture for this test result.

        Creates receiver pair and sets them on the contextvars.ContextVar
        so that the persistent ``_TextIOCapture`` routes all ``write()``
        calls to the correct receivers.  The persistent captures control
        ``quiet`` passthrough based on the process-wide ``--quiet`` flag.
        """
        stdout_recv = TextIOReceiver()
        stderr_recv = TextIOReceiver()
        stdout_recv.init()
        stderr_recv.init()
        self.__stdout_receiver = stdout_recv
        self.__stderr_receiver = stderr_recv
        _set_receivers(stdout_recv, stderr_recv)

    def release_output(self) -> None:
        """Release the receiver pair from the contextvars.ContextVar.

        This clears the contextvars.ContextVar so that further writes
        (e.g. from teardown or unexpected post-test output) are not
        captured.  The receiver's ``output`` attribute remains available
        for inspection via the ``stdout`` / ``stderr`` properties.
        """
        self.__stdout_receiver = None
        self.__stderr_receiver = None
        _clear_receivers()
