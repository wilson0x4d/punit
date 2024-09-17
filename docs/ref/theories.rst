Theories
========

A **Theory** is a `test` that makes `assertions` for a variant arrangement` of `state`. For a **Theory**, state is usually acquired from an external source, separated from the test definition. In **pUnit**, **Theories** are tests that have been decorated with :py:func:`theory` and at lease one data decorator such as :py:func:`inlinedata`.

Decorators
----------

.. py:currentmodule:: punit.theories

.. py:decorator:: theory
    :canonical: punit.theories.theory

    Decorates a function or method as a "Theory-based" test.

.. tip:: The ``@theory`` decorator on its own is not enough for a test to run, you must also provide data for the test using a decorator such as ``@inlinedata``.

.. py:decorator:: inlinedata(*args)
    :canonical: punit.theories.inlinedata

    Decorates a "Theory-based" test with inline data to be used by the test.

.. rubric:: Example (functions):

.. code:: python

    from punit import *

    @theory
    @inlinedata(0, 1, 1)
    @inlinedata(1, 1, 2)
    @inlinedata(1, 2, 3)
    @inlinedata(2, 3, 5)
    def myFunction(a, b, c):
        assert a + b == c

.. rubric:: Example (methods):

.. code:: python

    from punit import *

    class MyClass:
        @theory
        @inlinedata(0, 1, 1)
        @inlinedata(1, 1, 2)
        @inlinedata(1, 2, 3)
        @inlinedata(2, 3, 5)
        def myMethod(a, b, c):
            assert a + b == c
