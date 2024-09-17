Writing Tests
=============

.. note:: For information about Test Discovery, Test Packages, and Diagnosing problems please see the :doc:`quickstart`.

What is a Test?
---------------

In **pUnit** a `test` is a `function` or `method` that arranges `state` and performs `assertions` to verify expectations.

What is Test Failure?
---------------------

A test is said to `fail` if an ``AssertionError`` is raised by the test.

A test is said to `error` if any other ``Exception`` type is raised.

A test is said to `pass` if it does not raise any ``Exception`` during execution.

What is an Assertion?
---------------------

An `assertion` is a verification of `state`, typically performed using Python's ``assert`` keyword.

There is no requirement that assertions be performed using ``assert`` this is merely a conventional approach to testing that reads well.

.. code:: python

    assert 1 == 1 # this assertion will pass
    assert 1 == 2 # this assertion will fail

Facts and Theories
------------------

**pUnit** is based upon two fundamental concepts: **Facts** and **Theories**.

.. _what-are-facts:

A **Fact** is a `test` that makes `assertions` for an invariant arrangement of `state`. For a **Fact**, state is usually codified or hardcoded as part of test definition. In **pUnit**, **Facts** are tests that have been decorated with :py:func:`fact`.

.. _what-are-theories:

A **Theory** is a `test` that makes `assertions` for a variant arrangement` of `state`. For a **Theory**, state is usually acquired from an external source, separated from the test definition. In **pUnit**, **Theories** are tests that have been decorated with :py:func:`theory` and at lease one data decorator such as :py:func:`inlinedata`.

.. note:: In the current version of **pUnit** there is only a single source of variant state, the :py:func:`inlinedata` decorator.

Examples
--------

The section provides a series of referential examples which attempt to illustrate how tests can be written using `pUnit`. For the purpose of thesse examples assume they all reside in the same Python source file.

.. rubric:: A test function using ``@fact``:

.. code:: python

    from punit import *

    @fact
    def factFunc():
        assert 2 + 2 == 4, "It's a fact!"

.. rubric:: A test method using ``@fact``:

.. code:: python

    class MyTestClass:
        @fact
        def factMethod(self):
            assert 2 + 2 == 4, "It's a fact!"

.. rubric:: A test function using ``@theory``:

.. code:: python

    @theory
    @inlinedata(2, 2, 4, "It's a fact!")
    @inlinedata(1, 1, 2, "It's a fact!")
    def theoryFunc(x, y, z, message):
        assert x + y == z, message

.. rubric:: A test method using ``@theory``:

.. code:: python

    class MyTestClass:
        @theory
        @inlinedata(2, 2, 4, "It's a fact!")
        @inlinedata(1, 1, 2, "It's a fact!")
        def theoryMethod(self, x, y, z, message):
            assert x + y == z, message

As you can see from these examples, writing tests with `pUnit` is easy.

**Theories** offer a convenient way to write tests that verify expectations over a series of `states`, without having to write the same test over and over.
