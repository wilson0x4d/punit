Overview
========

**pUnit** is a modernized unit-testing framework for Python, inspired by **xUnit**.

Features
--------

* **IDE Support**; Run/Debug tests and review results with full error detail from within VSCode using the `x4d.punit-testadapter <https://marketplace.visualstudio.com/items?itemName=x4d.punit-testadapter>`__ extension (`also available for VSCodium via Open VSX <https://open-vsx.org/extension/x4d/punit-testadapter>`__).
* **Fact/Theory Based Testing**; Separate ``@fact`` and ``@theory`` decorators distinguish invariant tests from variant (parameterized) tests, allowing for more concise test permutation syntaxes.
* **Parallel Test Execution**; Optionally run tests concurrently with multiple worker threads, each with its own async event loop. Enable via ``--parallelism`` CLI flag or ``@parallel`` decorator. Mix parallel and ``@sequential``-marked tests in the same file.
* **Dual-Scope Setup/Teardown**; Module-scoped and class-scoped setup/teardown as bare decorated functions, no fixture plumbing or injection required. Configure with ``@setup`` and ``@teardown``.
* **Per-Test Output Capture**; Captures each test's stdout/stderr output in isolation, included in the test results and all report formats.
* **Traits**; Categorical name/value test metadata queryable at discovery time via CLI flags. Unlike traditional marks, traits are filterable during discovery, not at decoration, and can also be used to filter in the IDE.
* **Expected Failures with Inversion**; Invert test results for known bugs with human-readable reason tracking. Mark with ``@fails(reason)``, useful for TDD workflows.
* **Mock Objects**; Single-class mocking with fluent API (``.returns()``, ``.side_effect()``), origin conformance, delegate/spy support, nested child mocks, and iterator protocol. Located in ``punit.mocks``.
* **Module Patching**; Decorator and context-manager patching for arbitrary Python paths with automatic restoration, with support for complex dotted attribute paths.
* **Argument Matchers**; Lightweight and extensible matchers (``is_any``, ``contains``, ``is_gt``, ``is_lt``, ``in_range``, ``neg``) for flexible mock call assertions.
* **Conditionals**; Skip tests using boolean, callback, or unconditional logic via ``@skip()``. Evaluates at execution time, allowing for complex state mutation/evaluation in test suites.
* **Multi-Format Reports**; Built-in HTML, jUnit XML, and JSON reports which include captured output, precise timing, and full error detail. Enable with ``--report`` and combine with ``--output`` to write to a file, great for CI/CD integrations.
* **Multi-Level Test Filtering**; Unified test pipeline that combines filename globbing, case-insensitive regex on test names, trait queries, and ``--filter @FILEPATH`` filters (loaded from ``FILEPATH``); ``--filter @stdin`` allows piping lists of filters in via stdin.
* **Direct File Execution**; Run individual ``.py`` files without a ``tests/`` package or ``__init__.py``. Pass file paths directly to the CLI.
* **Assertion Helpers for Exceptions**; Type-safe exception assertion via generic syntax ``raises[MyException](action)``. Supports strict (``exact=True``) and subclass matching.
* **Assertion Helpers for Collections**; Assert sequences, lists, sets, dicts, and tuples using ``are_same``, ``has_length`` and ``is_none_or_empty`` for comparing elements, length bounds, and emptiness, or ordering.
* **Assertion Helpers for Numericals**; Directional comparators using ``> approx(threshold)`` with tolerance below and ``< approx(threshold)`` with tolerance above, also supports fluent syntaxes for more complex numerical requirements such as invariant boundary control, mixtures, etc.


.. toctree::
   :maxdepth: 3

   Overview <self>
   Quick Start <quickstart>
   Writing Tests <writing_tests>
   Reference <ref/index>
   SKILL <SKILL>
    MIT License <license>
    Contact <contact>

