Quick Start
============
.. _quickstart:

.. contents::

Installation
------------

For the moment, installation is only possible from the public Github repository:

.. rubric:: Using ``pip``:

.. code:: bash

    pip install git+https://github.com/wilson0x4d/punit.git

.. rubric:: Using ``poetry``:

.. code:: bash

    poetry add git+https://github.com/wilson0x4d/punit.git

We are `working on getting published to PyPI <https://github.com/pypi/support/issues/4760>`_, but due to a huge backlog of requests this may take a long time.

Command-Line Interface
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

**pUnit** looks for tests within a "Test Package", this is a directory sitting within the working directory that contains all of your test files.

.. admonition:: Why?

    The motivation for this was to ensure "relative imports" work correctly within test files, without sacrificing the ability to run tests out of multiple directories. For this reason the use of a "Test Package" is reinforced and a CLI argument to control it has been provided.

By default the Test Package **pUnit** expects to find is named "tests", and therefore all tests in the ``tests/`` directory will be executed.

You can change the Test Package by passing a ``--test-package`` argument indicating the target package name.

.. code:: bash

    python3 -m punit --test-package foo

In this example only the tests in  ``foo/`` will be run, and all relative imports will be resolved from the context of the ``foo`` module.

There is no requirement that you implement an `__init__.py` for your Test Package and whether or not you do every Python source file ``*.py`` will be included as a test file (unless it would be excluded via ``--exclude``.)

Test Discovery
--------------

**pUnit** scans all subdirectories of the Test Package looking for Python files (``*.py``) to be used for testing.

You can modify this behavior through a combination of ``--exclude`` and ``--include`` arguments.

The ``--exclude`` and ``--include`` arguments accept simple wildcard patterns to determine if a file or directory should be excluded or included, respectively. Do not confuse these with "globs" as they are not globs. The only valid wildcard expressions are `*` (match 1 or more of any character) and `?` (match any single character.)

Order does not matter, and ``--exclude`` will override a target even if an ``--include`` pattern would normally have included it.

Default Behavior
----------------

The default behavior is equivalent to the following:

.. code:: bash

    python3 -m punit --working-directory . --test-package tests --include '/tests/*.py' --exclude '/.*' --exclude '/__*__'

This ensures all Python files under the ``tests/`` directory in the current directory are executed as tests, except those in "dot-directories" or having "dunder-names".

Diagnosing Problems
-------------------

If you're trying to understand why Python files are/are-not running as tests you can use the ``--verbose`` argument. This will exhaustively output Include/Exclude information during the discovery process (among other things) and can be a useful debugging aid if things are not working as expected.
