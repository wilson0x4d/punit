Fails
=====

A **Fail** marks a Fact or Theory as expected to fail for a given reason. When the decorated test is run, pUnit records the failure alongside its ``reason`` so that CI systems and report generators can distinguish an *expected* failure from a regression.

Place this decorator *below* ``@fact`` or ``@theory``, closest to the function definition. It unwraps any intermediate decorators and attaches ``reason`` directly onto the original callable so that runners and reporters can detect expected failures.

.. py:currentmodule:: punit.fails

.. py:decorator:: fails(*, reason: str)
    :canonical: punit.fails.fails

    Marks a Fact or Theory as expected to fail for the given *reason*.

.. rubric:: Example (functions):

.. code-block:: python

    from punit import fact, fails

    @fact
    @fails(reason='bug #123: assert order is reversed')
    def test_reversed_order():
        assert get_items() == ['b', 'a']


.. rubric:: Example (methods):

.. code-block:: python

    from punit import fact, fails

    class MyTestClass:

        @fact
        @fails(reason='bug #456: timeout under load')
        def test_slow_query(self):
            assert query(duration=30) == expected


.. tip:: The ``@fails`` decorator may only be applied once per function and must appear after any ``@fact`` or ``@theory`` decorator.
