# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import sys
from typing import TextIO

class TextIOCapture:

    __quiet:bool
    output:str = None
    target:TextIO

    def __init__(self, target:TextIO, quiet:bool = False) -> None:
        self.__quiet = quiet
        self.output = None
        self.target = target

    def write(self, text:str):
        if self.output is None:
            self.output = text
        else:
            self.output += text
        if not self.__quiet:
            self.target.write(text)

class TestResult:

    __className:str
    __exception:Exception
    __fileName:str
    __hostName:str
    __isSuccess:bool
    __moduleName:str
    __packageName:str
    __properties:dict[str, str]
    __startTime:float
    __stderrCapture:TextIOCapture
    __stdoutCapture:TextIOCapture
    __stopTime:float
    __testName:str

    def __init__(self):
        self.__className = None
        self.__exception = None
        self.__fileName = None
        self.__hostName = None
        self.__isSuccess = None
        self.__moduleName = None
        self.__packageName = None
        self.__properties = {}
        self.__startTime = None
        self.__stderrCapture = None
        self.__stdoutCapture = None
        self.__stopTime = None
        self.__testName = None

    @property
    def className(self) -> str:
        return self.__className
    
    @className.setter
    def className(self, value:str) -> None:
        self.__className = value

    @property
    def exception(self) -> Exception:
        return self.__exception
    
    @exception.setter
    def exception(self, value:Exception) -> None:
        self.__exception = value

    @property
    def fileName(self) -> str:
        return self.__fileName
    
    @fileName.setter
    def fileName(self, value:str) -> None:
        self.__fileName = value

    @property
    def hostName(self) -> str:
        return self.__hostName
    
    @hostName.setter
    def hostName(self, value:str) -> None:
        self.__hostName = value

    @property
    def isSuccess(self) -> bool:
        return self.__isSuccess
    
    @isSuccess.setter
    def isSuccess(self, value:bool) -> None:
        self.__isSuccess = value

    @property
    def moduleName(self) -> str:
        return self.__moduleName
    
    @moduleName.setter
    def moduleName(self, value:str) -> None:
        self.__moduleName = value

    @property
    def packageName(self) -> str:
        return self.__packageName
    
    @packageName.setter
    def packageName(self, value:str) -> None:
        self.__packageName = value

    @property
    def properties(self) -> dict[str, str]:
        return self.__properties
    
    @properties.setter
    def properties(self, value:dict[str, str]) -> None:
        self.__properties = value

    @property
    def startTime(self) -> float:
        return self.__startTime
    
    @startTime.setter
    def startTime(self, value:float) -> None:
        self.__startTime = value

    @property
    def stderr(self) -> str:
        return None if self.__stderrCapture is None else self.__stderrCapture.output

    @property
    def stdout(self) -> str:
        return None if self.__stdoutCapture is None else self.__stdoutCapture.output

    @property
    def stopTime(self) -> float:
        return self.__stopTime
    
    @stopTime.setter
    def stopTime(self, value:float) -> None:
        self.__stopTime = value

    @property
    def testName(self) -> str:
        return self.__testName
    
    @testName.setter
    def testName(self, value:str) -> None:
        self.__testName = value

    @property
    def took(self) -> float:
        return self.__stopTime - self.__startTime

    @property
    def tookPretty(self) -> str:
        took = self.took
        if took >= 1:
            return f'{took:.1f}'.rstrip('0').rstrip('.') + 's'
        elif took >= 0.001:
            return f'{(took*1000):.0f}ms'
        elif took >= 0.000001:
            return f'{(took*1000):.3f}'.rstrip('0').rstrip('.') + 'ms'
        elif took >= 0.000000001:
            return f'{(took*1000000):.3f}'.rstrip('0').rstrip('.') + 'μs'
        else:
            return f'{(took*1000):.3f}'.rstrip('0').rstrip('.') + 'ms'


    def captureOutput(self, quiet:bool = False) -> tuple[TextIO, TextIO]:
        self.__stdoutCapture = TextIOCapture(sys.stdout, quiet)
        self.__stderrCapture = TextIOCapture(sys.stderr, quiet)
        sys.stdout = self.__stdoutCapture
        sys.stderr = self.__stderrCapture

    def releaseOutput(self) -> None:
        sys.stdout = self.__stdoutCapture.target
        sys.stderr = self.__stderrCapture.target
