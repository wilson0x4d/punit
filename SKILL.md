---
name: punit
description: pUnit xUnit-style unit testing framework for Python 3.11+ — @fact, @theory, @inlinedata, @setup, @teardown, @trait, @fails, @skip, @lifecycle, @parallel, @sequential, Mock, patch, matchers, assertions, report generators, CLI flags, TestResult, parallelism. Use as a reference document for pUnit API and concepts.
user-invocable: true
disable-model-invocation: false
type: reference
---

# pUnit — AI-First Library Reference

xUnit-style unit testing for Python 3.11+. **Zero dependencies.**

**Min Python**: 3.11

---

## AI-Usage Guidelines

Follow these rules when generating test code with pUnit:

1. **`assert` must have a message**: Every `assert` must include a message argument after the condition — `assert False, 'reason'`, not just `assert False`. The message must be a string literal (not a bare expression) and **include both the expected and actual values** that caused the assertion to fail — e.g. `assert actual == expected, f"(expected={expected}, actual={actual})"`.
2. **Use `@fact` for single-state tests, `@theory` + `@inlinedata` for multi-state**.
3. **Never use base classes** — all tests use decorators.
4. **For exception assertions**, prefer `raises[ExcType](fn)` over using `contextlib` or bare `try/except` blocks.
5. **For numeric approximate equality**, prefer `approx()` over manual tolerance math.
6. **For mock verification**, prefer `mock.called_with(matchers)` over manual call tracking.
7. **When `module_setup` / `module_teardown` names exist in test code**, recognize them as module-scoped `@setup`/`@teardown` targets by convention.
8. **`@lifecycle(Lifecycle.PER_RUN)`** means a single shared class instance across all test methods — `@setup` fires once before the first test, `@teardown` once after the last.

---

## Quick Reference

### Decorators

| Decorator | Purpose | Notes |
|---|---|---|
| `@fact` | Single-invARIANT test | Runs once |
| `@theory` + `@inlinedata(*args)` | Parameterized test | At least one `@inlinedata` required; each data point = separate result |
| `@setup` | Pre-test hook | Module-scoped (bare fn) or class-scoped (method) |
| `@teardown` | Post-test hook | Same scoping as `@setup` |
| `@trait(name, value=None)` | Test categorization | Stack multiple; CLI `--trait` filters |
| `@fails(reason='...')` | Expected failure | Must be below `@fact`/`@theory`; results inverted |
| `@skip` / `@skip(cond)` / `@skip(callable)` | Unconditional or conditional skip | Callable invoked at execution time; skip if `True` |
| `@lifecycle(Lifecycle.PER_RUN)` | Shared class instance | `PER_TEST` (default) = new instance for each test method; `PER_RUN` = single instance for all test methods. |
| `@parallel` | Run in thread pool | Without `--parallelism`: only decorated tests. With `--parallelism`: all tests run in pool unless `@sequential`. |
| `@sequential` | Exclude from thread pool | Without `--parallelism`: runs after `@parallel` tests. With `--parallelism`: excluded from pool. |

### Key Symbols

| Symbol | Import | Purpose |
|---|---|---|
| `Mock` | `from punit.mocks import Mock` | Fluent mock/stub with call tracking |
| `patch(path)` | `from punit.mocks import patch` | Context manager / decorator for module replacement |
| `raises[Exc](fn)` | `from punit.assertions.exceptions import raises` | Exception assertion |
| `approx(val)` | `from punit.assertions.numeric import approx` | Approximate numeric equality |
| `mocks.is_any()` etc. | `from punit.mocks import ...` | Matchers for `called_with` |
| `collections.*` / `strings.*` | `from punit.assertions import collections, strings` | Collection and string helpers |

---

## Core API

### Facts

```python
from punit import fact

@fact
def my_test() -> None:
    assert 1 + 1 == 2, 'simple addition'

@fact
async def async_fact() -> None:
    await asyncio.sleep(0.1)
    assert True, 'async works'

class MyTests:
    @fact
    def method_test(self) -> None: pass

    @fact
    @staticmethod
    def static_test() -> None: pass

    @fact
    @classmethod
    def class_test(cls) -> None: pass
```

### Theories

Each `@inlinedata` produces a separate test result.

```python
from punit import theory, inlinedata

@theory
@inlinedata(0, 0)
@inlinedata(1, 1)
@inlinedata(2, 4)
def verify_square(x: int, expected: int) -> None:
    assert x * x == expected

# Theory data accessible in results via TestResult.properties['data']
```

### Setup & Teardown

Two independent scopes based on whether the decorated function is a bare function or a class method.

```python
from punit import fact, setup, teardown

@setup
def module_setup() -> None:
    open_temp_file()

@teardown
def module_teardown() -> None:
    close_temp_file()

class MyTests:
    @setup
    def class_setup(self) -> None:
        self.state = 'ready'

    @teardown
    def class_teardown(self) -> None:
        flush_cache()

    @fact
    def test_a(self) -> None:
        assert self.state == 'ready'
```

---

## Traits

Categorize tests for selective execution. Stack multiple `@trait`.

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
python3 -m punit --trait '!integration'        # exclude
python3 -m punit --trait integration=redis     # only integration=redis
python3 -m punit --trait category=api --trait category=ui   # OR logic
```

---

## Expected Failures

```python
from punit import fact, fails

@fact
@fails(reason='bug #42')
def test_known_bug() -> None:
    assert False  # counts as success; a pass counts as regression
```

`@fails` must stack **below** `@fact`/`@theory`. Two `@fails` on same target raises an error.

---

## Skipping Tests

```python
from punit import fact, skip

@fact
@skip()          # unconditional
def test_skip() -> None:
    assert False  # never runs

@fact
@skip(lambda: os.name == 'posix')   # conditional: skip on POSIX
def test_windows_only() -> None:
    assert True
```

Result integration:
* Console: `🟨` emoji
* JUnit: `<skipped />` element
* JSON: `status: "skip"`
* `TestResult.is_skip` property

---

## Assertions

### Exception assertions

```python
from punit import fact, raises

@fact
def test_raises() -> None:
    def failing_fn() -> None:
        raise ValueError("boom")

    assert raises[ValueError](failing_fn)               # generic syntax
    assert raises(failing_fn, expect=ValueError)        # keyword syntax
    assert raises(failing_fn, exact=True, expect=ValueError)  # exact type (no subclass)
```

### Numeric assertions

```python
from punit.assertions.numeric import approx, isclose, isnan, isinfinite, percentage

# Approximate equality
assert 0.1 + 0.2 == approx(0.3)
assert 0.1 + 0.2 == approx(0.3, rel_tol=1e-5)

# One-sided comparators
assert 5.0 == approx(3).greater_than()       # >= 3
assert 0.5 == approx(1.0).less_than()        # <= 1
assert 5.0 == approx(3).at_least()           # >= 3 (tol below)
assert 0.5 == approx(1.0).at_most()          # <= 1 (tol above)
assert 0.0 == approx().zero()                # approx zero
assert 0.0 == approx().strict_greater_than() # > 0
assert 1.0 == approx().strict_less_than()    # < 1

# Range checks
assert 5.0 == approx().in_range(1.0, 10.0)               # inclusive [1, 10]
assert 5.0 == approx().in_range(1.0, 10.0).inclusive()   # explicit

# Standalone helpers
assert isclose(1 + 2j, 1.0 + 2.0j)        # complex-aware
assert not isclose(3, 3.000000001)
assert isnan(float('nan'))
assert isinfinite(float('inf'))
assert percentage(10, 100) == 90.0         # relative_to_expected=True by default
```

`approx` supports `int`, `float`, `complex`, `decimal.Decimal`.

### Collection assertions

```python
from punit import collections

assert collections.are_same([1, 2, 3], [1, 2, 3])
assert collections.are_same([2, 1, 3], [1, 3, 2], sort=True)
assert collections.has_length([1, 2, 3], min=2, max=5)
assert collections.is_none_or_empty([])
assert collections.is_none_or_empty(None)
```

### String assertions

```python
from punit import strings

assert strings.are_same('hello', 'hello')       # case-sensitive
assert strings.has_length('abc', min=1, max=5)
assert strings.is_none_or_empty('')
assert strings.is_none_or_whitespace(' \t')
```

---

## Mocking

`Mock` — fluent API, no base classes.

### Configuration

| Method | Purpose |
|---|---|
| `.returns(value)` | Fixed return (callable receives mock as arg); clears side_effect |
| `.side_effect(exc)` | Raise exception class/instance |
| `.side_effect(callable)` | Call returns mock + args; clears returns |
| `.side_effect(iterable)` | Sequential yields per call; raises StopIteration when exhausted |
| `.when(*a, **kw)` | Conditional subgraph keyed by matchers |
| `Mock(origin=Cls)` | `isinstance(mock, Cls)` = True (virtual subclass) |
| `Mock(delegate=obj)` | Unconfigured calls forward to real object |
| `Mock(**kwargs)` | Set attributes (e.g. `Mock(migration='alpha', id=1)`) |

### Example

```python
from punit.mocks import Mock

m = Mock()
m.method.returns(42)
assert m.method() == 42

m.method.side_effect([1, 2, 3])  # fluent chain overwrites returns
assert m.method() == 1

# Constructor fixture
row = Mock(migration='alpha', id=1)
assert row.migration == 'alpha'
```

### Verification

| Property | Type | Description |
|---|---|---|
| `mock.called` | bool | Any self-invocation recorded? |
| `mock.call_count` | int | Number of self-calls |
| `mock.calls` | tuple[Call, ...] | Call records (self + child via `child_calls`, combined via `all_calls`) |
| `mock.called_with(*a, **kw)` | bool | Any recorded call matches? |

### Dispatch & Reset

```python
# Context manager: resets mock on exit
with Mock(origin=UserService) as child:
    child.get_user.returns('Guest')
    assert child.get_user() == 'Guest'
# child reset on exit

# Preserves config, clears call history
m.reset()
m.reset(preserve_stubs=False, preserve_sideeffects=False)  # clear everything
```

### Matchers

| Matcher | Description | Example |
|---|---|---|
| `is_any()` | Any value | `is_any()` |
| `contains(x)` | Substring / container membership | `contains('foo')` |
| `is_gt(n)` | > n | `is_gt(10)` |
| `is_gte(n)` | >= n | `is_gte(10)` |
| `is_lt(n)` | < n | `is_lt(10)` |
| `is_lte(n)` | <= n | `is_lte(10)` |
| `is_in(*vals)` | Equals one of vals | `is_in('a', 'b')` |
| `is_type(*types)` | `isinstance` check | `is_type(str, int)` |
| `neg(inner)` | Negates inner matcher | `neg(is_in(1, 2))` |

```python
from punit.mocks import is_gt, is_in, contains, neg

m = Mock()
m(42, 'hello', [1, 2, 3])
assert m.called_with(is_gt(10), is_in('hello'), contains(2))
assert m.called_with(is_type(str, int), neg(is_any()))  # second always False
```

### Patch

```python
from punit.mocks import patch

with patch('myapp.connect') as m:
    m.returns('ok')

@patch('myapp.connect')
def test_connect(m):
    assert m.called

@patch('myapp.Pool', origin=Pool)
def test_pool(m):
    m.acquire.returns(True)
```

---

## Lifecycle

Controls class instance management across test methods.

```python
from punit import fact, lifecycle, Lifecycle

@lifecycle(Lifecycle.PER_RUN)
class MyTests:
    # Single shared instance for all methods
    # @setup fires once before first test, @teardown once after last
    counter = 0

    @fact
    def test_a(self) -> None:
        self.counter += 1

    @fact
    def test_b(self) -> None:
        assert self.counter == 1  # shared state
```

| Value | Behavior |
|---|---|
| `Lifecycle.PER_TEST` (default) | Fresh instance per test method |
| `Lifecycle.PER_RUN` | Single shared instance for all methods in class |

---

## Parallelism

**Default (no `--parallelism` flag): tests are sequential.** Only `@parallel`-decorated tests run in the thread pool; all others run sequentially after.

**With `--parallelism` (bare, `--parallelism N`, `--parallelism 0`): all tests run in parallel** using `cpu_count // 2` workers. Tests decorated with `@sequential` are excluded from the pool and run after all parallel tests complete.

### With `@parallel` / `@sequential` (manual control, no `--parallelism`)

```bash
python3 -m punit   # sequential except @parallel-decorated tests
```

```python
from punit import parallel, sequential

@parallel
class ParallelSuite:
    @fact
    def test_a(self) -> None: ...  # runs in thread pool

@sequential
class SequentialSuite:
    @fact
    def test_b(self) -> None: ...  # runs after all @parallel tests
```

### With `--parallelism` (all tests parallel, `@sequential` excludes)

```bash
python3 -m punit --parallelism 4   # all tests run in 4 workers
```

```python
from punit import sequential

@sequential
class SequentialSuite:
    @fact
    def test_b(self) -> None: ...  # excluded from pool; runs after parallel tests
```

Each worker has its own asyncio event loop. Execution order: parallel facts → parallel theories → sequential facts → sequential theories.

---

## Test Results

### TestResult Properties

| Property | Type | Description |
|---|---|---|
| `class_name` | `str \| None` | Test class name |
| `test_name` | `str` | Function/method name |
| `module_name` | `str` | Module name |
| `package_name` | `str` | Top-level test package name |
| `file_name` | `str` | Source file path |
| `host_name` | `str` | Execution hostname |
| `is_success` | `bool` | Pass/fail status |
| `is_skip` | `bool` | Skip status |
| `exception` | `Exception \| None` | Exception raised |
| `start_time` / `stop_time` | `float` | Wall clock |
| `took` | `float` | Elapsed seconds |
| `tookPretty` | `str` | Human-friendly: `'1.5s'`, `'50ms'`, `'250.0ns'` |
| `stdout` | `str` | Captured stdout |
| `stderr` | `str` | Captured stderr |
| `properties` | `dict` | Arbitrary dict (e.g. `data` for theory params) |
| `expected_failure_reason` | `str \| None` | `@fails` reason |

### Report Generators

```python
from punit.reports import HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator

html = HtmlReportGenerator().generate(results)
junit = JUnitReportGenerator().generate(results)
json_str = JsonReportGenerator().generate(results)
```

---

## CLI Reference

```bash
python3 -m punit [-h] [-q] [-v] [-z] [-p NAME] [-i PAT] [-e PAT]
                 [-f PAT|@FILE] [-t [!]NAME[=VAL]] [-w PATH]
                 [-n] [--no-exitcode] [--no-pathfix] [-r {html|junit|json}]
                 [-o FILE] [--parallelism [N]] [FILE ...]
```

| Flag | Description | Default |
|---|---|---|
| `-h, --help` | Show help | |
| `-q, --quiet` | Quiet output | |
| `-v, --verbose` | Show tracebacks on failure | |
| `-z, --failfast` | Stop on first failure | |
| `-p, --test-package NAME` | Test package directory | `tests` |
| `-i, --include PAT` | Include file glob | `*.py` |
| `-e, --exclude PAT` | Exclude file glob | `/__*__` |
| `-f, --filter PAT` | Test name pattern | `*` |
| `-f, --filter @FILE` | Load filter patterns from file | |
| `-t, --trait [!]N[=V]` | Include/exclude by trait | `*` |
| `-w, --working-directory` | Working directory | current |
| `-n, --no-default-patterns` | Skip default include/exclude | |
| `--no-exitcode` | Don't exit with error on failure | |
| `--no-pathfix` | Don't tweak sys.path | |
| `--parallelism [N]` | Parallel execution with N workers | `0` (disabled) |
| `-r, --report FMT` | Report format: `html`, `junit`, `json` | |
| `-o, --output FILE` | Write report to file | |
| `FILE` | Run specific files (skips discovery) | auto-discover |

---

## Discovery

Auto-discovers test modules under the test package directory. Default include `*.py`, exclude `/__*__`. Directories matching exclude patterns are pruned.

```bash
python3 -m punit --include 'test_*.py' --exclude '*internal*'
python3 -m punit tests/specific_test.py        # direct file, skips discovery
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | All tests passed |
| 1 | General error / CLI failure |
| 119 | Test failure, setup error, teardown error (or `--no-exitcode` unset) |

---

## Package Structure

```
src/punit/
  __init__.py          # Top-level exports: fact, theory, inlinedata, setup, teardown,
                       # trait, fails, skip, lifecycle, Lifecycle, parallel, sequential,
                       # Mock, raises, approx, mocks, assertions, collections, strings, numeric
  __main__.py          # CLI entry point
  cli.py               # CommandLineInterface
  runner.py            # TestRunner
  lifecycle.py         # @lifecycle decorator
  lifecycle_manager.py # PER_TEST / PER_RUN instance caching
  parallelism.py       # ThreadPool, @parallel, @sequential
  test_result.py       # TestResult
  text_io_capture.py   # stdout/stderr capture system
  discovery/           # ModuleDiscovery
  filters/             # FilterManager, FilterDescriptor
  facts/               # @fact, FactDescriptor, FactManager
  theories/            # @theory, @inlinedata, TheoryManager
  traits/              # @trait
  setups/              # @setup
  teardowns/           # @teardown
  conditions/          # @skip
  results/             # @fails
  assertions/
    exceptions.py      # raises[...]
    numeric.py         # approx, isclose, isnan, isinfinite, percentage
    collections.py     # are_same, has_length, is_none_or_empty (+ deprecated aliases)
    strings.py         # are_same, has_length, is_none_or_empty, is_none_or_whitespace
  mocks/               # Mock, Call, CallList, patch, matchers
  reports/             # HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator
  metadata/            # CallableMetadata
```

---

## Import Map

```python
# Everything you need
from punit import fact, theory, inlinedata, setup, teardown, trait, fails, skip
from punit import lifecycle, Lifecycle, parallel, sequential
from punit import Mock, raises, approx
from punit import mocks, collections, strings, numeric, assertions

# Sub-modules
from punit.mocks import (
    Mock, Call, CallList, MockError, patch, Matcher,
    neg, contains, is_any, is_gt, is_gte, is_lt, is_lte, is_in, is_type,
)
from punit.reports import HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator
from punit.test_result import TestResult
```
