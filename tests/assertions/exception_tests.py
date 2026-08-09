# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact, raises


class CustomError(Exception):
    pass


def raises_custom_exception() -> None:
    raise CustomError()


@fact
def raises_must_capture_errors() -> None:
    assert raises[Exception](raises_custom_exception)


@fact
def raises_supports_typearg_syntax() -> None:
    # preferred syntax
    assert raises[Exception](raises_custom_exception, exact=False)
    assert raises[CustomError](raises_custom_exception, exact=True)
    assert not raises[Exception](raises_custom_exception, exact=True)


@fact
def raises_supports_kwargs_syntax() -> None:
    # compatibility syntax
    assert raises(raises_custom_exception, exact=False, expect=Exception), 'do not expect an exact type match.'
    assert raises(raises_custom_exception, exact=True, expect=CustomError), 'must expect an exact type match'
    assert not raises(raises_custom_exception, exact=True, expect=Exception)


@fact
def when_no_error_must_return_false() -> None:
    assert not raises[ValueError](lambda: None), 'do not assert when no error raised.'
