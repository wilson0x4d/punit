String Helpers
==============

.. py:currentmodule:: punit.strings

.. py:function:: are_same(a:str|None, b:str|None) -> bool

    Use :py:func:`~punit.strings.are_same` to assert that two strings contain the same characters in the same order.

.. rubric:: Example

.. code:: python

    from punit import strings

    a = 'hello'
    b = 'hello'
    c = 'world'
    d = None

    assert strings.are_same(a, b)
    assert not strings.are_same(b, c)
    assert strings.are_same(a, a)
    assert strings.are_same(None, None)
    assert not strings.are_same(a, None)
    assert not strings.are_same(None, b)

.. py:function:: has_length(actual: str | None, min: Optional[int] = None, max: Optional[int] = None) -> bool

    Check if ``actual``'s length falls within the inclusive range ``[min, max]``.
    At least one of ``min`` or ``max`` must be provided; passing both as ``None`` returns ``False``.

    :param str|None actual: The string to check
    :param int|None min: Inclusive lower bound on length (``len(actual) >= min``)
    :param int|None max: Inclusive upper bound on length (``len(actual) <= max``)
    :returns bool: True if the length satisfies the bounds, False otherwise

.. rubric:: Example

.. code:: python

    from punit import strings

    a = 'hello'

    assert strings.has_length(a, min=5)
    assert strings.has_length(a, max=5)
    assert strings.has_length(a, min=3, max=7)
    assert not strings.has_length(a, min=6)
    assert not strings.has_length(a, max=4)

.. py:function:: is_none_or_empty(string:str|None) -> bool

    Use :py:func:`~punit.strings.is_none_or_empty` to assert that a string is ``None`` or empty.

.. rubric:: Example

.. code:: python

    from punit import strings

    a = 'hello'
    b = ''
    c = None    

    assert not strings.is_none_or_empty(a)
    assert strings.is_none_or_empty(b)
    assert strings.is_none_or_empty(c)

.. py:function:: is_none_or_whitespace(string:str|None) -> bool

    Use :py:func:`~punit.strings.is_none_or_whitespace` to assert that a string is ``None`` or whitespace.

.. rubric:: Example

.. code:: python

    from punit import strings

    a = 'hello'
    b = ' \t'
    c = None

    assert not strings.is_none_or_whitespace(a)
    assert strings.is_none_or_whitespace(b)
    assert strings.is_none_or_whitespace(c)
