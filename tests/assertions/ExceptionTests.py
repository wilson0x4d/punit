# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from punit.assertions.exceptions import *
from punit.facts import fact

class CustomException(Exception):
    pass

def raisesCustomException():
    raise CustomException()

@fact
def AssertRaises_MustCatchException():
    assert raises[Exception](raisesCustomException)

@fact
def AssertRaises_WithTypeVar():
    assert raises[Exception](raisesCustomException, exact=False)
    assert raises[CustomException](raisesCustomException, exact=True)
    assert not raises[Exception](raisesCustomException, exact=True)

@fact
def AssertRaises_WithKwarg():
    assert raises(raisesCustomException, exact=False, expect=Exception)
    assert raises(raisesCustomException, exact=True, expect=CustomException)
    assert not raises(raisesCustomException, exact=True, expect=Exception)

@fact
def AssertRaises_WhenNoException_MustReturnFalse():
    assert not raises[ValueError](lambda: None)
