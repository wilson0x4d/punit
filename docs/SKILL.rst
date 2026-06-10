SKILL.rst
=========

Claude Code Skill — ``punit``
-----------------------------

This document describes the ``punit`` skill for Claude Code and embeds the full
``SKILL.md`` snippet. Copy the embedded ``SKILL.md`` content (see below) to
``.claude/skills/punit/SKILL.md`` in any project that consumes or develops pUnit
tests — Claude Code loads it automatically when the user mentions "punit" or
discusses unit testing.

**Source code:** https://github.com/wilson0x4d/punit
**Docs:** https://punit.readthedocs.io/
**Install:** ``python3 -m pip install punit``


Overview
========

**pUnit** is a modernized xUnit-style unit-testing framework for Python. It provides
two core test types: **Facts** (invariant state tests) and **Theories** (parameterized
tests via ``@inlinedata``). Tests are plain functions/methods — no base classes,
no ``__init__.py`` required.


Embedded Skill Markdown
=======================

The full ``SKILL.md`` content follows verbatim. It is also maintained as a separate
file at [docs/SKILL.md](SKILL.md) for standalone use.

.. code-block:: markdown
    :linenos:
    :caption: docs/SKILL.md

    ---
    name: punit
    description: Provides additional unit-testing guidance for the pUnit framework. MUST use when user mentions "punit" or discusses unit testing. MUST use when creating, refactoring, or reading files inside the `tests/` directory. MUST use when creating or modifying files matching `*test*.py`.
    user-invocable: true
    disable-model-invocation: false
    ---

    `punit` requires Python 3.11+. It exposes `@fact`, `@theory`, `@inlinedata`, `@trait`, and `@fails` decorators to organize code into unit tests. Tests are plain functions/methods — no inheritance required, no `__init__.py` needed. By default pUnit discovers tests under the `tests/` directory.

    - **Documentation:** https://punit.readthedocs.io/
    - **Install:** `python3 -m pip install punit`
    - **Source:** https://github.com/wilson0x4d/punit

    ## CLI Invocation

    Always prefix with the project's virtual-environment interpreter and always supply a filter:

    ```bash
    .venv/bin/python -m punit --filter '*'
    ```

    Multiple filters narrow results (logical AND):

    ```bash
    .venv/bin/python -m punit --filter '*Widget*' --filter '*Cache*'
    ```

    ## CLI Flags Reference

    | Flag | Meaning | Example |
    | :--- | :--- | :--- |
    | `-q, --quiet` | Suppress normal output | `--quiet` |
    | `-v, --verbose` | Exhaustive discovery & result detail | `--verbose` |
    | `-z, --failfast` | Stop on first failure or error | `--failfast` |
    | `-p, --test-package NAME` | Override test package (default `tests`) | `--test-package foo` |
    | `-i, --include PATTERN` | Include pattern for file discovery | `--include '*widget*'` |
    | `-e, --exclude PATTERN` | Exclude pattern (overrides include) | `--exclude '*hardcoded*'` |
    | `-f, --filter PATTERN\|@FILE` | Restrict tests by qualified name/path | `--filter 'MyClass.fact'` |
    | `-t, --trait [!]NAME[=VALUE]` | Include/exclude by trait (`!` to exclude) | `--trait '!integration'` |
    | `--no-pathfix` | Rely on PYTHONPATH instead of adding `src/` | `--no-pathfix` |
    | `-r, --report {html\|json}` | Generate a report to stdout | `--report json` |
    | `-o, --output FILENAME` | Write report to file (not stdout) | `--output result.json` |

    **Wildcard syntax** for include/exclude/filter:
    - `*` — match one or more characters
    - `?` — match any single character

    ## Filters File

    Use `--filter '@path/to/file.txt'` to load patterns from a plaintext file (one per line; lines starting with `#` are comments). Prefix individual filter entries with `!` to exclude them. Order matters: the first matching rule wins.

    Piped input via stdin is also supported:

    ```bash
    cat tests/filters-file.txt | .venv/bin/python -m punit --filter '@stdin'
    ```

    ## Writing Tests

    ### Facts — single-case assertions

    ```python
    from punit import fact

    @fact
    async def when_initialized_touch_must_return_true():
        mylib = MyLibrary()
        mylib.initialize()
        await asyncio.sleep(1)
        assert mylib.touch(), 'Expected touch() == True after initialize().'
    ```

    ### Theories — parametrized assertions

    Each `@inlinedata(...)` call produces one test instance; values are passed positionally:

    ```python
    from punit import theory, inlinedata

    @theory
    @inlinedata(2, 2, 4, 'two plus two equals four')
    @inlinedata(1, 1, 2, 'one plus one equals two')
    def add_theory(x: int, y: int, z: int, message: str):
        assert x + y == z, message
    ```

    ### Traits — categorize tests for CI filtering

    ```python
    from punit import theory, inlinedata, trait

    @theory
    @inlinedata(0, 1, 1)
    @trait('integration')
    @trait('redis')
    def api_query_theory(a: int, b: int, c: int):
        assert a + b == c
    ```

    ### Expected Failures — regression detection for known bugs

    The `@fails` decorator marks a test as expected to fail; the runner inverts its result (passing becomes failure). Useful for tracking known issues. Always stack **below** `@fact` or `@theory`:

    ```python
    from punit import fact, fails

    @fact
    @fails(reason='bug #123: pending fix')
    def broken_feature_should_pass():
        assert False  # reported as passed; a fix that makes this pass = regression
    ```

    Requires the `reason=` keyword argument (positional not allowed). Raises if stacked below another pUnit decorator or double-stacked.

    ### Methods & Classes — same decorators, no inheritance required

    ```python
    class MyTestFixture:

        @fact
        def verify_calc_error_condition(self):
            from punit.assertions.exceptions import raises
            def call_with_none(): self.calc(None)
            assert raises[Exception](call_with_none)
            assert not raises[Exception](lambda: self.calc(1))
    ```

    ### Setup & Teardown

    ```python
    from punit import setup, teardown

    @setup  # runs before each test (module-scoped if at module level; class-scoped if a method inside a test class)
    def prepare_data(): ...

    @teardown  # runs after each test (same scoping model as @setup)
    def cleanup(): ...
    ```

    ## Assertion Helpers

    pUnit uses Python's `assert` directly. Optional helper modules live under `punit.assertions`:

    ### Collections

    Both `punit` top-level re-exports (`from punit import collections`) and submodule paths (`from punit.assertions import collections`) are supported.

    ```python
    from punit.assertions import collections

    assert collections.are_same([1, 2], (1, 2))   # element-wise equality
    assert collections.has_length(lst, min=3)      # length check (keyword args only: min, max)
    assert collections.is_none_or_empty([])        # None or empty?
    ```

    ### Strings

    Both `punit` top-level re-exports (`from punit import strings`) and submodule paths (`from punit.assertions import strings`) are supported.

    ```python
    from punit.assertions import strings

    assert strings.are_same('a', 'a')              # string equality
    assert strings.has_length(s, min=3)            # length check (keyword args only: min, max)
    assert strings.is_none_or_empty(None)          # None or empty?
    assert strings.is_none_or_whitespace('  ')     # whitespace-only?
    ```

    ### Exceptions

    Both `punit` top-level re-exports (`from punit import raises`) and submodule paths (`from punit.assertions.exceptions import raises`) are supported.

    ```python
    # Preferred: generic syntax (Python 3.11+)
    assert raises[TypeError](lambda: int("bad"))

    # Fallback: function-arg syntax
    assert raises(lambda: int("bad"), expect=TypeError, exact=True)
    ```

    ### Numeric

    Both `punit` top-level re-exports (`from punit import approx`) and submodule paths (`from punit.assertions.numeric import approx, isclose, isnan, isinfinite, percentage`) are supported.

    The `approx` class supports natural Python comparison syntax with directional (one-sided) tolerance:

        * ``x == approx(expected)``; approximately equal (bidirectional tolerance)
        * ``x > approx(threshold)``; strictly greater than (tolerance extends above)
        * ``x >= approx(threshold)``; at least the threshold (tolerance extends below)
        * ``x < approx(threshold)``; strictly less than (tolerance extends above)
        * ``x <= approx(threshold)``; at most the threshold (tolerance extends below)

    ```python
    from punit.assertions.numeric import approx, isclose, isnan, isinfinite, percentage

    # Primary: operator overloads (preferred by user)
    assert 0.1 + 0.2 == approx(0.3)                        # approximately equal
    assert value >  approx(5)                              # strictly greater than
    assert value >= approx(5)                              # at least the threshold
    assert value <  approx(10)                             # strictly less than
    assert value <= approx(10)                             # at most the threshold

    # Secondary: fluent methods for advanced scenarios
    assert some_value == approx(3.14).greater_than()       # >= 3.14 with one-sided tolerance below
    assert some_value == approx(10.0).less_than()          # <= 10.0 with one-sided tolerance above
    assert some_value == approx(5).at_least()              # same as greater_than()
    assert some_value == approx(10).at_most()              # same as less_than()
    assert some_value == approx(5).in_range(3, 7)          # within [3, 7] with directional tolerance
    assert some_value == approx().zero()                   # approximately zero

    # Standalone helpers
    assert isclose(3.141, 3.14, rel_tol=0.01)              # drop-in math.isclose replacement
    assert isnan(float('nan'))                             # NaN check
    assert isinfinite(float('inf'))                        # infinity check
    assert percentage(10, 100) == 90.0                     # percentage difference
    ```

    ## Default CLI Invocation

    The default behavior is equivalent to:

    ```bash
    python3 -m punit \
        --test-package tests \
        --include '*.py' \
        --exclude '/__*__' \
        --filter '*'
    ```

    This includes all Python files under `tests/`, excludes dunder names, and runs every test.

    ## Troubleshooting

    - If pUnit fails to execute, prefix with the venv path: `.venv/bin/python -m punit`.
    - Use `--verbose` to debug discovery / filtering issues.
    - Test files do **not** need `__init__.py`.
    - Exit code `119` indicates one or more tests failed.
