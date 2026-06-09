# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import sys
from typing import Any, TextIO, Optional, cast


class TextIOCapture:

    __quiet: bool
    output: str | None = None
    target: TextIO

    def __init__(self, target: TextIO, quiet: bool = False) -> None:
        self.__quiet = quiet
        self.output = None
        self.target = target

    def write(self, text: str) -> int:
        if self.output is None:
            self.output = text
        else:
            self.output += text
        if not self.__quiet:
            self.target.write(text)
        return len(text)


class TestResult:

    __class_name: Optional[str]
    __exception: Exception | None
    __file_name: str | None
    __host_name: str | None
    __is_success: bool | None
    __module_name: str | None
    __package_name: str | None
    __properties: dict[str, Any]
    __start_time: float | None
    __stderr_capture: TextIOCapture | None
    __stdout_capture: TextIOCapture | None
    __stop_time: float | None
    __test_name: str | None

    def __init__(self) -> None:
        self.__class_name = None
        self.__exception = None
        self.__file_name = None
        self.__host_name = None
        self.__is_success = None
        self.__module_name = None
        self.__package_name = None
        self.__properties = dict[str, Any]()
        self.__start_time = None
        self.__stderr_capture = None
        self.__stdout_capture = None
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
    def is_success(self) -> bool:
        return False if self.__is_success is None else self.__is_success

    @is_success.setter
    def is_success(self, value: bool) -> None:
        self.__is_success = value

    @property
    def module_name(self) -> str:
        return cast(str, self.__module_name)

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
        return None if self.__stderr_capture is None else self.__stderr_capture.output

    @property
    def stdout(self) -> str | None:
        return None if self.__stdout_capture is None else self.__stdout_capture.output

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
            return f'{(took*1000):.3f}'.rstrip('0').rstrip('.') + 'ms'

    def capture_output(self, quiet: bool = False) -> None:
        self.__stdout_capture = TextIOCapture(sys.stdout, quiet)
        self.__stderr_capture = TextIOCapture(sys.stderr, quiet)
        sys.stdout = self.__stdout_capture
        sys.stderr = self.__stderr_capture

    def release_output(self) -> None:
        if self.__stdout_capture is not None and self.__stdout_capture.target is not None:
            sys.stdout = self.__stdout_capture.target
        if self.__stderr_capture is not None and self.__stderr_capture.target is not None:
            sys.stderr = self.__stderr_capture.target
