# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit.assertions.exceptions import raises
from punit.facts import fact


class CustomException(Exception):
    pass

def raisesCustomException() -> None:
    raise CustomException()

@fact
def AssertRaises_MustCatchException() -> None:
    assert raises[Exception](raisesCustomException)

@fact
def AssertRaises_WithTypeVar() -> None:
    # preferred syntax
    assert raises[Exception](raisesCustomException, exact=False)
    assert raises[CustomException](raisesCustomException, exact=True)
    assert not raises[Exception](raisesCustomException, exact=True)

@fact
def AssertRaises_WithKwarg() -> None:
    # compatibility syntax
    assert raises(raisesCustomException, exact=False, expect=Exception)
    assert raises(raisesCustomException, exact=True, expect=CustomException)
    assert not raises(raisesCustomException, exact=True, expect=Exception)

@fact
def AssertRaises_WhenNoException_MustReturnFalse() -> None:
    assert not raises[ValueError](lambda: None)
