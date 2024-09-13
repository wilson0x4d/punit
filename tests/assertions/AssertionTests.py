# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from src.assertions import *
from src.facts import fact

class CustomError(Exception):
    pass

def raisesCustomError():
    raise CustomError()

@fact
def AssertRaises_MustCatchError():
    assert raises[Exception](raisesCustomError)

@fact
def AssertRaises_WithTypeVar():
    assert raises[Exception](raisesCustomError, exact=False)
    assert raises[CustomError](raisesCustomError, exact=True)
    assert not raises[Exception](raisesCustomError, exact=True)

@fact
def AssertRaises_WithKwarg():
    assert raises(raisesCustomError, exact=False, expect=Exception)
    assert raises(raisesCustomError, exact=True, expect=CustomError)
    assert not raises(raisesCustomError, exact=True, expect=Exception)
