Setups
======

A **Setup** provides a mechanism for performing initialization before test execution. A ``@setup``-decorated function is executed immediately before each test runs, allowing you to prepare resources or reset state without cluttering your test bodies with try/finally blocks.

In **pUnit**, setups come in two scopes:

* **Module-scoped** -- a bare function decorated with ``@setup``; fires once per test across the entire module.
* **Class-scoped** -- a method inside a test class decorated with ``@setup``; fires once per test within that specific class only.

The two scopes are independent: a module-scoped ``@setup`` applies only to bare-function tests in its module, and a class-scoped ``@setup`` applies only to the methods defined on its class.

.. tip:: A setup may be synchronous or asynchronous, just like Facts and Theories. If a setup raises an exception, the corresponding test is marked as failed but no further processing occurs for that test.

.. py:currentmodule:: punit.setups

.. py:decorator:: setup
    :canonical: punit.setups.setup

    Decorates a function or method as a "Setup" that runs before each test.

.. rubric:: Module-scoped example:

.. code:: python

    from punit import fact, setup

    @setup
    def my_setup():
        """Runs once before each module-scoped test defined in the same module."""
        prepare_database()

    @fact
    def test_something():
        assert True


.. rubric:: Class-scoped example:

.. code:: python

    from punit import fact, setup

    class MyTestClass:

        @setup
        def setUpClass(self):
            """Runs once before each class-scoped test method defined in the same class."""
            reset_temp_files()

        @fact
        def test_a(self):
            assert True


.. rubric:: Combining setups and teardowns:

.. code:: python

    from punit import fact, setup, teardown

    _connection = None

    @setup
    def db_setup():
        """Initialize database connection before each test."""
        global _connection
        _connection = connect_to_database()

    @teardown
    def db_teardown():
        """Close database connection after each test."""
        global _connection
        if _connection:
            _connection.close()
            _connection = None

    @fact
    def test_query():
        assert query(_connection) is not None
