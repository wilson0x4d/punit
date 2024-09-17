Facts
=====

A **Fact** is a `test` that makes `assertions` for an invariant arrangement of `state`. For a **Fact**, state is usually codified or hardcoded as part of test definition. In **pUnit**, **Facts** are tests that have been decorated with :py:func:`fact`.

Decorators
----------

.. py:currentmodule:: punit.facts

.. py:decorator:: fact
    :canonical: punit.facts.fact

    Decorates a function or method as a "Fact-based" test.

.. rubric:: Example (functions):

.. code:: python

    from punit import *

    @fact
    def myFunction():
        assert 1 == 1

.. rubric:: Example (methods):

.. code:: python

    from punit import *

    class MyClass:
        @fact
        def myMethod():
            assert 1 == 1
