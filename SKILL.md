---
name: punit
description: pUnit xUnit-style unit testing framework for Python 3.11+ — @fact, @theory, @inlinedata, @setup, @teardown, @trait, @fails, @skip, Mock, patch, matchers, assertions, report generators, CLI flags, TestResult. Use as a reference document for pUnit API and concepts.
user-invocable: true
disable-model-invocation: false
type: reference
---

# pUnit — AI-First Library Reference

A modernized xUnit-style unit-testing framework for Python 3.11+.

**Minimum Python**: 3.11  |  **Zero dependencies**

---

## Quick Start

```bash
python3 -m punit                          # auto-discover & run tests in tests/
python3 -m punit --test-package elsewhere  # custom test package
python3 -m punit --report junit --output results.xml
```

---

## Core Concepts

pUnit tests are functions or methods decorated with `@fact` or `@theory`. There are **no base classes to inherit**, **no naming requirements** (test names don't affect discovery), and full async/await support out of the box.

### Facts (invariant tests)

Facts validate an invariant arrangement of state. Each decorated function runs exactly once.

```python
from punit import fact

@fact
def my_test() -> None:
    assert 1 + 1 == 2

@fact
async def async_fact() -> None:
    await asyncio.sleep(0.1)
    assert True

class MyTests:
    @fact
    def class_method_test(self) -> None:
        assert True

    @fact
    @staticmethod
    def static_method_test() -> None:
        assert True

    @fact
    @classmethod
    def class_method_test(cls) -> None:
        assert True
```

### Theories (parameterized tests)

Theories validate behavior across variant state. A `@theory` requires at least one data decorator (e.g. `@inlinedata`). Each data point produces a separate test result.

```python
from punit import theory, inlinedata

@theory
@inlinedata(0, 0)
@inlinedata(1, 1)
@inlinedata(2, 4)
@inlinedata(3, 9)
def verify_square(x: int, expected: int) -> None:
    assert x * x == expected
```

---

## Setup & Teardown

`@setup` runs before each test; `@teardown` runs after. Two independent scopes:

* **Module-scoped** — bare function; fires per test across the entire module.
* **Class-scoped** — method inside a test class; fires per test within that class.

```python
from punit import fact, setup, teardown

# --- Module-scoped ---
@setup
def module_setup() -> None:
    open_temp_file()

@teardown
def module_teardown() -> None:
    close_temp_file()

@fact
def test_one() -> None:
    pass  # setup runs, then this, then module_teardown

# --- Class-scoped ---
class MyTests:
    setup_called = 0

    @setup
    def class_setup(self) -> None:
        self.setup_called += 1

    @teardown
    def class_teardown(self) -> None:
        flush_cache()

    @fact
    def test_a(self) -> None:
        assert self.setup_called == 1  # fires per method

    @fact
    def test_b(self) -> None:
        assert self.setup_called == 2
```

---

## Traits

Traits categorize tests for selective execution. Stack multiple `@trait` decorators on a single test.

```python
from punit import fact, trait

@fact
@trait('integration')
@trait('category', 'api')
async def test_api_query() -> None:
    ...
```

CLI filters:

```bash
python3 -m punit --trait '!integration'        # exclude integration tests
python3 -m punit --trait integration=redis     # only integration=redis tests
python3 -m punit --trait category=api --trait category=ui   # OR logic (api OR ui)
```

---

## Expected Failures

`@fails` marks a test as expected to fail. Results are inverted: a failing test counts as pass, a passing one counts as a regression.

```python
from punit import fact, fails

@fact
@fails(reason='bug #42: not yet implemented')
def test_known_bug() -> None:
    assert False  # this counts as success in the report
```

`@fails` must be stacked **below** `@fact` or `@theory` (closest to the function def). Two `@fails` on the same target raises an error.

---

## Skipping Tests

`@skip` marks a test to be skipped entirely. The test body is never executed. Results show as skipped (pass with a skip indicator).

`@skip` can be stacked **above or below** any other decorator — no conflict checks are performed.

### Boolean mode

```python
from punit import fact, skip

@fact
@skip()          # bare @skip() — unconditional skip
def test_always_skipped() -> None:
    assert False  # never runs

@fact
@skip(True)      # explicit skip
def test_explicit_skip() -> None:
    assert False

@fact
@skip(False)     # skip=False — test runs (no-op; equivalent to no @skip)
def test_runs() -> None:
    assert True
```

### Callable mode

```python
import os

@fact
@skip(lambda: os.name == 'posix')   # skip on POSIX systems
def test_windows_only() -> None:
    assert True                     # runs only on non-POSIX
```

The callable is invoked at test execution time; the test is skipped if it returns `True`.

### Runner / report integration

* Console output: skipped tests show a `🟨` emoji instead of `🟩`.
* HTML report: annotated with `(skipped)`.
* JUnit report: includes a `<skipped />` element.
* JSON report: `status: "skip"`.

### TestResult.is_skip

```python
from punit.TestResult import TestResult

result = TestResult()
result.is_skip is False                    # default
result.is_skip = True                      # mark as skipped
```

---

## Assertions

pUnit uses Python's `assert`, augmented by helper modules.

### Exception assertions

```python
from punit import fact, raises

@fact
def test_raises() -> None:
    def failing_fn() -> None:
        raise ValueError("boom")

    assert raises[ValueError](failing_fn)           # Python 3.11+ generic syntax
    assert raises(failing_fn, expect=ValueError)     # keyword syntax for compat
    assert raises(failing_fn, exact=True, expect=ValueError)  # exact type match (no subclass)
```

### Numeric assertions

```python
from punit.assertions.numeric import approx, isclose, isnan, isinfinite, percentage

# Approximate equality (pytest.approx-style)
assert 0.1 + 0.2 == approx(0.3)
assert 0.1 + 0.2 == approx(0.3, rel_tol=1e-5)

# Chained comparators (one-sided tolerance)
assert 5.0 == approx(3).greater_than()   # >= 3 (tolerance extends below)
assert 0.5 == approx(1.0).less_than()    # <= 1 (tolerance extends above)
assert 5.0 == approx(3).at_least()       # >= 3 (one-sided tol below)
assert 0.5 == approx(1.0).at_most()      # <= 1 (one-sided tol above)
assert 0.1 == approx().zero()            # approximately zero

# Range checks
assert 5.0 == approx().in_range(1.0, 10.0)              # inclusive [1, 10]
assert 5.0 == approx().in_range(1.0, 10.0).inclusive()  # explicit inclusive

# Standalone helpers
assert isclose(1 + 2j, 1.0 + 2.0j)        # complex-aware
assert not isclose(3, 3.000000001)
assert isnan(float('nan'))
assert isinfinite(float('inf'))
assert percentage(10, 100) == 90.0
```

### Collection assertions

```python
from punit import collections

assert collections.are_same([1, 2, 3], [1, 2, 3])         # element-by-element
assert collections.are_same([2, 1, 3], [1, 3, 2])         # False (order matters)
assert collections.are_same([2, 1, 3], [1, 3, 2], sort=True)  # True

assert collections.has_length([1, 2, 3], min=2, max=5)    # length in range
assert collections.has_length([1, 2, 3], min=3)            # min constraint only
assert collections.is_none_or_empty([])                    # True
assert collections.is_none_or_empty(None)                   # True
```

### String assertions

```python
from punit import strings

assert strings.are_same('hello', 'hello')     # True
assert strings.are_same('Hello', 'hello')     # False (case-sensitive)
assert strings.has_length('abc', min=1, max=5)
assert strings.is_none_or_empty('')            # True
assert strings.is_none_or_whitespace(' \t')    # True
```

---

## Mocking

Lightweight mocking via `punit.mocks`. No base classes, full fluent API.

### Basic stubbing

```python
from punit.mocks import Mock

m = Mock()
m.method.returns(42)
assert m.method() == 42                          # call the stub to get the return value
m.method.returns('hello').side_effect([1, 2])    # fluent chaining
assert m.method() == 1
assert m.method() == 2
```

### Side effects

```python
m = Mock()

# Exception on call
m.method.side_effect(ValueError("boom"))
try:
    m.method()
except ValueError:
    pass

# Callable (receives mock instance as sole arg)
m.method.side_effect(lambda self: self.parent.value)

# Iterable (sequential consumption, caches iterator)
m.method.side_effect([1, 2, 3])
assert m.method() == 1
assert m.method() == 2
assert m.method() == 3
```

### Constructor fixture style

```python
row = Mock(migration='alpha', id=1)
assert row.migration == 'alpha'
assert row.id == 1
```

### Origin conformance (isinstance checks)

```python
class UserService:
    def get_user(self, user_id: int) -> str: ...

m = Mock(origin=UserService)
assert isinstance(m, UserService)                # virtual subclass registration
m.get_user.returns('Guest')
assert m.get_user() == 'Guest'
```

### Delegate forwarding (partial doubles / spies)

```python
class RealService:
    def __init__(self): self.counter = 0
    def increment(self) -> int:
        self.counter += 1
        return self.counter

m = Mock(delegate=RealService())
assert m.increment() == 1                        # unconfigured calls forward to real object
```

### Call tracking

```python
m = Mock()
m.method(1, 2, key='val')

assert m.called                              # True
assert m.call_count == 1
assert m.calls[0].args == (1, 2)
assert m.calls[0].kwargs == {'key': 'val'}
assert m.called_with(1, key='val')           # matches any recorded call
```

### Iteration support

```python
m = Mock()
m.rows.returns([Mock(name='Alice'), Mock(name='Bob')])

assert len(m.rows) == 2

# Comprehensions work directly on the mock
names = {u.name for u in m.rows}
assert names == {'Alice', 'Bob'}
```

### Context manager

```python
with Mock(origin=UserService) as child:
    child.get_user.returns('Guest')
    assert child.get_user() == 'Guest'
# child is auto-reset on exit; parent unaffected
```

### Conditional dispatch (`when` subgraphs)

Create conditionally-dispatched subgraphs keyed by matcher arguments. Identical matcher tuples return the same subgraph (deduped).

```python
from punit.mocks import Mock, is_gt, is_lte

m = Mock()

# Configure: when arg is <= 42, return 'low'; when > 42, return 'high'
m.num.when(is_lte(42)).returns('low')
m.num.when(is_gt(42)).returns('high')

assert m.num(42) == 'low'
assert m.num(50) == 'high'

# Non-matching calls fall through to flat .returns()
m.other.returns('default')
assert m.other('any_value') == 'default'

# Nested conditions on subgraphs
outer = m.num.when(is_gt(0))
outer.val.when(is_gt(10)).returns('high')
outer.val.when(is_lte(10)).returns('low')
assert m.num(5).val(5) == 'low'           # 5 > 0 matches outer, 5 <= 10 matches inner
assert m.num(1).val(20) == 'high'         # 1 > 0 matches outer, 20 > 10 matches inner
```

### Reset

```python
m = Mock()
m.method.returns(42)
m.method()                                  # call_count == 1

m.reset()                                   # clears history, keeps config
assert m.call_count == 0
assert m.method() == 42                     # config survives
assert m.call_count == 1

m.reset(preserve_stubs=False)               # clears children and config too
```

### Matching (`called_with` with matchers)

```python
from punit.mocks import Mock, is_any, is_gt, is_lt, is_lte, is_gte, is_in, is_type, contains, neg

m = Mock()
m(42, 'hello world', [1, 2, 3])

assert m.called_with(
    is_gt(10),                     # first arg > 10
    is_in('hello world', 'foo'),   # second arg in set
    contains(2),                   # third arg contains 2
)

assert m.called_with(
    is_type(str, int),             # type check: str or int
    neg(is_any()),                 # negated: always False here
)
```

#### Available matchers

| Matcher | Description | Example |
|---|---|---|
| `is_any()` | Matches any single value (singleton) | `is_any()` |
| `contains(x)` | Checks if arg is a superstring or container | `contains('foo')` |
| `is_gt(n)` | Value strictly greater than `n` | `is_gt(10)` |
| `is_gte(n)` | Value >= `n` | `is_gte(10)` |
| `is_lt(n)` | Value strictly less than `n` | `is_lt(10)` |
| `is_lte(n)` | Value <= `n` | `is_lte(10)` |
| `is_in(*values)` | Value equals one of the candidates | `is_in('a', 'b')` |
| `is_type(*types)` | `isinstance` check against given types | `is_type(str, int)` |
| `neg(inner)` | Negates inner matcher | `neg(is_in(1, 2))` |

### Patch

Replace a module-level attribute with a `Mock` via context manager or decorator. Supports async.

```python
from punit.mocks import patch

# Context manager
with patch('myapp.database.connect') as m:
    m.returns('connected')

# Decorator (sync)
@patch('myapp.database.connect')
def test_connect(m):
    assert m.called

# Decorator (async)
@patch('myapp.database.connect')
async def test_async_connect(m):
    assert m.called

# With origin constraint
@patch('myapp.db.Pool', origin=Pool)
def test_pool(m):
    m.acquire.returns(True)
```

---

## Test Results & Reporting

### TestResult properties

```python
from punit.TestResult import TestResult

result = TestResult()
result.class_name      # e.g. 'MyTests' (None for bare-function tests)
result.test_name       # function/method name
result.module_name     # module/namespace name
result.package_name    # top-level test package name
result.file_name       # source file path
result.host_name       # execution hostname
result.is_success      # pass/fail status
result.exception       # exception raised (if any)
result.start_time      # wall clock start (float)
result.stop_time       # wall clock stop (float)
result.took            # elapsed seconds
result.tookPretty      # human-friendly: '1.5s', '50ms', '250.0ns'
result.stdout          # captured stdout
result.stderr          # captured stderr
result.properties      # arbitrary dict (e.g., theory 'data' for theory params)
result.expected_failure_reason  # @fails reason string
result.is_skip                  # skip status (True if test was skipped via @skip)
```

### Report generators

```python
from punit.reports import HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator

results = [...]  # list of TestResult

html = HtmlReportGenerator().generate(results)
junit_xml = JUnitReportGenerator().generate(results)
json_str = JsonReportGenerator().generate(results)
```

Reports include status indicators, error/traceback display, stdout/stderr, and timing info with automatic expected-failure annotation.

---

## CLI Reference

```bash
python3 -m punit [-h] [-q] [-v] [-z] [-p NAME] [-i PATTERN] [-e PATTERN]
                 [-f PATTERN|@FILE] [-t [!]NAME[=VALUE]] [-w PATH]
                 [-n] [--no-exitcode] [--no-pathfix] [-r {html|junit|json}]
                 [-o FILE] [FILE ...]
```

| Flag | Description | Default |
|---|---|---|
| `-h, --help` | Show help and exit | |
| `-q, --quiet` | Quiet output | |
| `-v, --verbose` | Verbose output (show tracebacks on failure) | |
| `-z, --failfast` | Stop on first failure | |
| `-p, --test-package NAME` | Test package directory | `tests` |
| `-i, --include PATTERN` | Include test file glob | `*.py` |
| `-e, --exclude PATTERN` | Exclude test file glob | `/__*__` |
| `-f, --filter PATTERN` | Only run tests matching pattern | `*` |
| `-f, --filter @FILE` | Load filter patterns from file | |
| `-t, --trait [!]NAME[=VALUE]` | Include/exclude by trait category | |
| `-w, --working-directory PATH` | Working directory | current |
| `-n, --no-default-patterns` | Skip default include/exclude rules | |
| `--no-exitcode` | Don't exit with error code on failure | |
| `--no-pathfix` | Rely on PYTHONPATH, don't tweak sys.path | |
| `-r, --report FORMAT` | Generate report: `html`, `junit`, `json` | |
| `-o, --output FILE` | Write report to file instead of stdout | |
| `FILE` | Run specific .py files directly | auto-discover |

---

## Discovery

Test modules are auto-discovered under the test package directory. Default include `*.py`, exclude `/__*__` (dunder files). Directories matching exclude patterns are pruned entirely.

```bash
python3 -m punit --include 'test_*.py' --exclude '*internal*'
```

Direct file execution skips discovery:

```bash
python3 -m punit tests/specific_test.py tests/another_test.py
```

Filters (via `-f`) still apply when files are specified directly.

---

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | All tests passed |
| 1 | General error / CLI validation failure |
| 119 | Test failure, setup error, or teardown error (or `--no-exitcode` unset) |

---

## Package Structure

```
punit/
  __init__.py          # Top-level exports: fact, theory, inlinedata, setup, teardown,
                       # trait, fails, skip, Mock, raises, approx, mocks
  TestResult.py        # TestResult data class
  runner.py            # TestRunner: discovery, execution, result aggregation
  cli.py               # CommandLineInterface: argument parsing
  facts/               # @fact decorator, FactManager (singleton)
  theories/            # @theory, @inlinedata, TheoryManager
  traits/              # @trait decorator, TraitManager
  setups/              # @setup decorator, SetupManager
  teardowns/           # @teardown decorator, TeardownManager
  mocks/               # Mock class, Call, CallList, patch, matchers
  results/             # @fails decorator
  conditions/          # @skip decorator
  assertions/          # Helper sub-modules
    exceptions.py      # raises[...]
    numeric.py         # approx, isclose, isnan, isinfinite, percentage
    collections.py     # are_same, has_length, is_none_or_empty
    strings.py         # are_same, has_length, is_none_or_empty, is_none_or_whitespace
  reports/             # Report generators
    HtmlReportGenerator.py
    JUnitReportGenerator.py
    JsonReportGenerator.py
```

---

## Import Map

```python
# Everything you need, one import
from punit import fact, theory, inlinedata, setup, teardown, trait, fails, skip
from punit import Mock, raises, approx
from punit import mocks

# Sub-modules
from punit.assertions import collections, strings, exceptions, numeric
from punit.mocks import (
    Mock, Call, CallList, MockError, patch,
    neg, contains, is_any, is_gt, is_gte, is_lt, is_lte, is_in, is_type,
)
from punit.reports import HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator
from punit.TestResult import TestResult
```
