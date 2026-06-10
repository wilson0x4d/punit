Facts
=====

A **Fact** is a `test` that makes `assertions` for an invariant arrangement of `state`. For a **Fact**, state is usually codified or hardcoded as part of test definition. In **pUnit**, **Facts** are tests that have been decorated with ``@fact``.

.. py:currentmodule:: punit.facts

.. py:decorator:: fact
    :canonical: punit.facts.fact

    Decorates a function or method as a "Fact-based" test.

.. rubric:: Example (functions):

.. code-block:: python

    from punit import fact

    @fact
    def myFunction():
        assert 1 == 1

.. rubric:: Example (methods):

.. code-block:: python

    from punit import fact

    class MyClass:
        @fact
        def myMethod():
            assert 1 == 1
