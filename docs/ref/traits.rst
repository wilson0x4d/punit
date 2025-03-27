Traits
======

A **Trait** is a categorical name/value pair that can be associated with a test. **Traits** can be used to group tests together for inclusion or exclusion, allowing for more flexible testing strategies.

Some use-cases for traits include:

- Grouping tests by their area of functionality (e.g. UI, business logic, etc.)
- Grouping tests by their dependencies/requirements (e.g. integration, mock, etc.)
- Flagging tests as "slow" or "flaky" for controlling the order of execution or skipping them during certain types of testing.

Once a trait has been applied to a test it can be referenced during test execution to exclude or include the test for execution. Consider the following examples.

.. code:: bash

    # by prefixing the trait name with a '!', tests with this trait will be excluded.
    python3 -m punit --trait '!integration'
    # (this will exclude all `!integration` tests)

    # by specifying the trait name and value, only tests having both will be matched:
    python3 -m punit --trait integration=redis
    # (this will only run `integration` tests having a `redis` value)

    # `--trait` can be specified multiple times, tests having either trait will be matched:
    python3 -m punit --trait category=api --trait integration
    # (this will run category=api OR category=ui tests)

    # exclusions take priority over inclusions:
    python3 -m punit --trait integration --trait '!integration=postgres'
    # (runs all `integration` tests, except those having a `postgres` value)

Other test selection criteria such as ``--include``, ``--exclude``, and ``--filter`` can be used in conjunction with traits to provide more fine-grained control over test execution.

Decorators
----------
.. py:currentmodule:: punit.traits

.. py:decorator:: trait(name, value=None)
    :canonical: punit.traits.trait

    Decorates a **Fact** or **Theory** as having a specific **Trait**.

.. tip:: The ``@trait`` decorator can be applied more than once on a test.

.. rubric:: Example (functions):

.. code:: python

    from punit import *

    @theory
    @inlinedata(0, 1, 1)
    @trait('integration', 'redis')
    @trait('category', 'api')
    def myFunction(a, b, c):
        assert a + b == c

.. rubric:: Example (methods):

.. code:: python

    from punit import *

    class MyClass:
        @fact
        @trait('category', 'ui')
        def myMethod(self):
            assert True
