# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import sys
from typing import Any, TextIO, Optional, cast


class TextIOCapture:

    __quiet:bool
    output:str|None = None
    target:TextIO

    def __init__(self, target:TextIO, quiet:bool = False) -> None:
        self.__quiet = quiet
        self.output = None
        self.target = target

    def write(self, text:str) -> int:
        if self.output is None:
            self.output = text
        else:
            self.output += text
        if not self.__quiet:
            self.target.write(text)
        return len(text)



class TestResult:

    __className:Optional[str]
    __exception:Exception|None
    __fileName:str|None
    __hostName:str|None
    __isSuccess:bool|None
    __moduleName:str|None
    __packageName:str|None
    __properties:dict[str, Any]
    __startTime:float|None
    __stderrCapture:TextIOCapture|None
    __stdoutCapture:TextIOCapture|None
    __stopTime:float|None
    __testName:str|None

    def __init__(self) -> None:
        self.__className = None
        self.__exception = None
        self.__fileName = None
        self.__hostName = None
        self.__isSuccess = None
        self.__moduleName = None
        self.__packageName = None
        self.__properties = dict[str,Any]()
        self.__startTime = None
        self.__stderrCapture = None
        self.__stdoutCapture = None
        self.__stopTime = None
        self.__testName = None

    @property
    def className(self) -> Optional[str]:
        return self.__className
    
    @className.setter
    def className(self, value:Optional[str]) -> None:
        self.__className = value

    @property
    def exception(self) -> Exception|None:
        return self.__exception
    
    @exception.setter
    def exception(self, value:Exception) -> None:
        self.__exception = value

    @property
    def fileName(self) -> str|None:
        return self.__fileName
    
    @fileName.setter
    def fileName(self, value:str) -> None:
        self.__fileName = value

    @property
    def hostName(self) -> str|None:
        return self.__hostName
    
    @hostName.setter
    def hostName(self, value:str) -> None:
        self.__hostName = value

    @property
    def isSuccess(self) -> bool:
        return False if self.__isSuccess is None else self.__isSuccess
    
    @isSuccess.setter
    def isSuccess(self, value:bool) -> None:
        self.__isSuccess = value

    @property
    def moduleName(self) -> str:
        return cast(str,self.__moduleName)
    
    @moduleName.setter
    def moduleName(self, value:str) -> None:
        self.__moduleName = value

    @property
    def packageName(self) -> str|None:
        return self.__packageName
    
    @packageName.setter
    def packageName(self, value:str) -> None:
        self.__packageName = value

    @property
    def properties(self) -> dict[str, Any]:
        return self.__properties
    
    @properties.setter
    def properties(self, value:dict[str, str]) -> None:
        self.__properties = value

    @property
    def startTime(self) -> float|None:
        return self.__startTime
    
    @startTime.setter
    def startTime(self, value:float) -> None:
        self.__startTime = value

    @property
    def stderr(self) -> str|None:
        return None if self.__stderrCapture is None else self.__stderrCapture.output

    @property
    def stdout(self) -> str|None:
        return None if self.__stdoutCapture is None else self.__stdoutCapture.output

    @property
    def stopTime(self) -> float|None:
        return self.__stopTime
    
    @stopTime.setter
    def stopTime(self, value:float) -> None:
        self.__stopTime = value

    @property
    def testName(self) -> str|None:
        return self.__testName
    
    @testName.setter
    def testName(self, value:str) -> None:
        self.__testName = value

    @property
    def took(self) -> float|None:
        return None if self.__stopTime is None or self.__startTime is None else self.__stopTime - self.__startTime

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


    def captureOutput(self, quiet:bool = False) -> None:
        self.__stdoutCapture = TextIOCapture(sys.stdout, quiet)
        self.__stderrCapture = TextIOCapture(sys.stderr, quiet)
        sys.stdout = self.__stdoutCapture
        sys.stderr = self.__stderrCapture

    def releaseOutput(self) -> None:
        if self.__stdoutCapture is not None and self.__stdoutCapture.target is not None:
            sys.stdout = self.__stdoutCapture.target
        if self.__stderrCapture is not None and self.__stderrCapture.target is not None:
            sys.stderr = self.__stderrCapture.target
