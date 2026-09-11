# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations


class MockError(Exception):
    """
    Exception raised when mock configuration is violated.

    Usage
    -----

    .. code-block:: python

        from punit.mocks import Mock, MockError

        mock = Mock()
        mock.foo.returns(42)
        try:
            mock.foo = 99  # raises MockError
        except MockError:
            pass

    """
