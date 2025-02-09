Quick Start
============
.. _quickstart:

.. contents::

Installation
------------

You can install the library from `PyPI <https://pypi.org/project/punit/>`_ using typical methods, such as ``pip``:

.. code:: bash

   python3 -m pip install punit

Usage
----------------------

For the simplest usage you can run **pUnit** from the root of a repository, it will discover and run all tests.

.. code:: bash
    
    python3 -m punit

You can provide an explicit working directory by passing ``--working-directory``:

.. code:: bash

    python3 -m punit --working-directory /home/user/my-project/

You can view a complete listing of arguments by passing ``--help``:

.. code:: bash

    python3 -m punit --help

The Test Package
----------------

**pUnit** looks for tests within a "Test Package", this is a subdirectory of the working directory, it is expected to contain all of your test files.

.. admonition:: Why?

    The motivation for this was to ensure "relative imports" work correctly within test files, without sacrificing the ability to run tests out of multiple directories. For this reason the use of a "Test Package" is reinforced and a CLI argument to control it has been provided.

By default the Test Package **pUnit** expects to find is named "tests", and therefore all tests in the ``tests/`` directory will be executed.

.. rubric:: How to override the default

You can change the Test Package by passing a ``--test-package`` argument indicating the target package name. For example:

.. code:: bash

    python3 -m punit --test-package foo

In this example only the tests in  ``foo/`` will be run, and all relative imports will be resolved from the context of ``foo``.

.. rubric:: Is is necessary to create ``__init__.py`` or ``__main__.py``?

No. There is no requirement that ``__init__`` or ``__main__`` exist. If they exist they will be ignored (by default.)

Test Discovery
--------------

**pUnit** scans the Test Package directory, and all subdirectories, looking for Python files (``*.py``) to be used for testing.

You can modify this behavior through a combination of ``--exclude`` and ``--include`` arguments.

The ``--exclude`` and ``--include`` arguments accept simple wildcard patterns to determine if a file or directory should be excluded or included, respectively. Do not confuse these with "globs" as they are not globs. The only valid wildcard expressions are ``*`` (match 1 or more of any character) and ``?`` (match any single character.)

Order does not matter, and ``--exclude`` will override a target even if an ``--include`` pattern would normally have included it.

Test Filtering
--------------

Separate from the **Test Discovery** process, **pUnit** can be instructed to execute only a subset of discovered tests by providing a ``--filter`` argument. This argument can be used to restrict test execution to a specific test, test class, test module, or (if tests are named well) a range of tests spanning the test hierarchy -- such as testing a feature.

.. code:: bash

    # the default behavior is equivalent to..
    python3 -m punit --filter '*'
    # but imagine you had a series of tests targeting "Widgets"..
    python3 -m punit --filter 'Widget'

The same filter rules that apply to ``--include`` and ``--exclude`` arguments also apply to ``--filter``, but take note that unlike ``--include`` and ``--exclude`` multiple ``--filter`` arguments will not be honored (last-in wins.)

The ``--filter`` argument is intended as a human QOL feature. Build workflows should use ``--include`` and ``--exclude`` for maximum flexibility and control.

Default Behavior
----------------

The default behavior is equivalent to the following:

.. code:: bash

    python3 -m punit --working-directory . --test-package tests --include '/tests/*.py' --exclude '/.*' --exclude '/__*__'

This ensures all Python files under the ``tests/`` subdirectory are executed as tests, except for Python files within "dot-directories" or having "dunder-names".

Diagnosing Problems
-------------------

If you're trying to understand why Python files are/are-not running as tests you can use the ``--verbose`` argument. This will exhaustively output Include/Exclude information during the discovery process (among other things) and can be a useful debugging aid if things are not working as expected.
