Exception Helpers
=================

.. py:currentmodule:: punit.exceptions

.. py:function:: raises[TError:Exception](action:Callable, *, exact:bool = False, expect:TError = None) -> bool

    Use :py:func:`raises` to assert that a function, method, or lambda expression raises an expected ``Exception``.

    :param action: The ``Callable`` being tested, usually a function or method reference.

    :param exact: A ``boolean`` indicating that the raised Exception must be an exact type match (and not a subclass of the specified type.) Use this when you need to test for a specific exception type.

    :param expect: A ``type`` parameter that can be used in lieu of ``TError``.
    
.. rubric:: Exact Match Example

.. code:: python

    class MyException(Exception):
        pass

    class NotMyException(Exception):
        pass

    def myFunctionOne:
        raise NotMyException()

    def myFunctionTwo:
        raise MyException()

    # assert we can inexact-match Exception superclass
    assert raises[Exception](myFunctionOne)
    assert raises[Exception](myFunctionTwo)
    # assert we can exact-match Exception subclass
    assert raises[NotMyException](myFunctionOne, exact=True)
    assert raises[MyException](myFunctionTwo, exact=True)

.. rubric:: Syntax Example

.. admonition:: LTS
    
    This helper offers two syntaxes, one which relies on Python 3.12 "Type Parameters" and the other which relies on an explicit ``expect:type`` argument; the latter syntax exists solely for LTS purposes to preempt Python Core Developers breaking a dunder the Python 3.12 syntax is relying on.

.. code:: python

    def myFunction:
        raise MyException()

    # using Python 3.12 Type Parameter Syntax
    assert raises[MyException](myFunction)
    # using LTS/failsafe `expect` syntax
    assert raises(myFunction, expect=MyException)

