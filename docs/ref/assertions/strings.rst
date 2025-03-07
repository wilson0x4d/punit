String Helpers
==============

.. py:currentmodule:: punit.strings

.. py:function:: areSame(a:str|None, b:str|None) -> bool

    Use :py:func:`~punit.strings.areSame` to assert that two strings contain the same characters in the same order.

.. rubric:: Example

.. code:: python

    from punit import *

    a = 'hello'
    b = 'hello'
    c = 'world'
    d = None

    assert strings.areSame(a, b)
    assert not strings.areSame(b, c)
    assert strings.areSame(a, a)
    assert strings.areSame(None, None)
    assert not strings.areSame(a, None)
    assert not strings.areSame(None, b)

.. py:function:: isNoneOrEmpty(string:str|None) -> bool

    Use :py:func:`~punit.strings.isNoneOrEmpty` to assert that a string is ``None`` or empty.

.. rubric:: Example

.. code:: python

    from punit import *

    a = 'hello'
    b = ''
    c = None    

    assert strings.isNoneOrEmpty(a)
    assert strings.isNoneOrEmpty(b)
    assert strings.isNoneOrEmpty(c)
    assert not strings.isNoneOrEmpty(a)
    assert not strings.isNoneOrEmpty(b)

.. py:function:: isNoneOrWhitespace(string:str|None) -> bool

    Use :py:func:`~punit.strings.isNoneOrWhitespace` to assert that a string is ``None`` or whitespace.

.. rubric:: Example

.. code:: python

    from punit import *

    a = 'hello'
    b = ' \t'
    c = None

    assert strings.isNoneOrWhitespace(a)
    assert strings.isNoneOrWhitespace(b)
    assert strings.isNoneOrWhitespace(c)
    assert not strings.isNoneOrWhitespace(a)
    assert not strings.isNoneOrWhitespace(b)
