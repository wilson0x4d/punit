Teardowns
=========

A **Teardown** provides a mechanism for performing cleanup after test execution. A ``@teardown``-decorated function is executed immediately after each test runs, allowing you to release resources or reset state without cluttering your test bodies with try/finally blocks.

In **pUnit**, teardowns come in two scopes:

* **Module-scoped** -- a bare function decorated with ``@teardown``; fires once per test across the entire module.
* **Class-scoped** -- a method inside a test class decorated with ``@teardown``; fires once per test within that specific class only.

The two scopes are independent: a module-scoped ``@teardown`` applies only to bare-function tests in its module, and a class-scoped ``@teardown`` applies only to the methods defined on its class.

.. tip:: A teardown may be synchronous or asynchronous, just like Facts and Theories.

.. py:currentmodule:: punit.teardowns

.. py:decorator:: teardown
    :canonical: punit.teardowns.teardown

    Decorates a function or method as a "Teardown" that runs after each test.

.. rubric:: Module-scoped example:

.. code-block:: python

    from punit import fact, teardown

    @teardown
    def my_teardown():
        """Runs once after each module-scoped test defined in the same module."""
        cleanup_database()

    @fact
    def test_something():
        assert True


.. rubric:: Class-scoped example:

.. code-block:: python

    from punit import fact, teardown

    class MyTestClass:

        @fact
        def test_a(self):
            assert True

        @teardown
        def tearDownClass(self):
            """Runs once after each class-scoped test method defined in the same class."""
            reset_temp_files()
