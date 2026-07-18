`pUnit` is a modernized unit-testing framework for Python, inspired by xUnit.

This README is only a high-level introduction to **pUnit**. For more detailed documentation, please view the official docs at [https://pUnit.readthedocs.io](https://pUnit.readthedocs.io).

## Features

- **IDE Support**; Run/Debug tests and review results with full error detail from within vscode using the [x4d.punit-testadapter](https://marketplace.visualstudio.com/items?itemName=x4d.punit-testadapter) extension ([also available for VSCodium via Open VSX](https://open-vsx.org/extension/x4d/punit-testadapter))
- **Fact/Theory Based TEsting**; Separate `@fact` and `@theory` decorators distinguish invariant tests from variant (parameterized) tests, allowing for more concise test permutation syntaxes.
- **Parallel Test Execution**; Optionally run tests concurrently with multiple worker threads, each with its own async event loop. Enable via `--parallel` CLI flag or `@parallel` decorator. Mix parallel and `@sequential`-marked tests in the same file.
- **Dual-Scope Setup/Teardown**; Module-scoped and class-scoped setup/teardown as bare decorated functions, no fixture plumbing or injection required. Configure with `@setup` and `@teardown`.
- **Per-Test Output Capture**; Captures each test's stdout/stderr output in isolation, included in the test results and all report formats.
- **Traits**; Categorical name/value test metadata queryable at discovery time via CLI flags. Unlike traditional marks, traits are filterable during discovery, not at decoration, and can also be used to filter in the IDE.
- **Expected Failures with Inversion**; Invert test results for known bugs with human-readable reason tracking. Mark with `@fails(reason)`, useful for TDD workflows.
- **Mock Objects**; Single-class mocking with fluent API (`.returns()`, `.side_effect()`), origin conformance, delegate/spy support, nested child mocks, and iterator protocol. Located in `punit.mocks`.
- **Module Patching**; Decorator and context-manager patching for arbitrary Python paths with automatic restoration, with support for complex dotted attribute paths.
- **Argument Matchers**; Lightweight and extensible matchers (`is_any`, `contains`, `is_gt`, `is_lt`, `in_range`, `neg`) for flexible mock call assertions.
- **Conditionals**; Skip tests using boolean, callback, or unconditional logic via `@skip()`. Evaluates at execution time, allowing for complex state mutation/evaluation in test suites.
- **Multi-Format Reports**; Built-in HTML, jUnit XML, and JSON reports which include captured output, precise timing, and full error detail. Enable with `--report` and combine with `--output` to write to a file, great for CI/CD integrations.
- **Multi-Level Test Filtering**; Unified test pipeline that combines filename globbing, case-insensitive regex on test names, trait queries, and `--filter @FILEPATH` filters (loaded from ``FILEPATH``), `--filter @stdin` allows piping lists of filters in via stdin.
- **Direct File Execution**; Run individual `.py` files without a `tests/` package or `__init__.py`. Pass file paths directly to the CLI.
- **Assertion Helpers for Exceptions**; Type-safe exception assertion via generic syntax `raises[MyException](action)`. Supports strict (`exact=True`) and subclass matching.
- **Assertion Helpers for Collections**; Assert sequences, lists, sets, dicts, and tuples using `are_same`, `has_length` and `is_none_or_empty` for comparing elements, length bounds, and emptiness, or ordering.
- **Assertion Helpers for Numericals**; Directional comparators using `> approx(threshold)` with tolerance below and `< approx(threshold)` with tolerance above, also supports fluent syntaxes for more complex numerical requirements such as invariant boundary control, mixtures, etc.

## Command-Line Usage

Running pUnit with no arguments will perform test auto-discovery and execution:

```bash
python3 -m punit
```

By default it will look for tests in the `tests/` directory. You can override this behavior by providing a `--test-package` argument:

```bash
python3 -m punit --test-package elsewhere
```

In the above example, test discovery will instead occur in an `elsewhere/` directory.

### Report Generation

`pUnit` can generate "Test Results" reports. Currently supporting HTML and jUnit formats:

```bash
python3 -m punit --report html
```

Reports can also be output to a file where they can be lifted as part of a CI/CD pipeline and stored as an artifact or used for other purposes:

```bash
python3 -m punit --report junit --output results.xml
```

### Syntax Help

There are more options available, passing a `--help` argument will print help text:

```bash
python3 -m punit --help
```
Outputs:
```plaintext
Usage: python3 -m punit [-h|--help] [FILE ...]
                        [-q|--quiet]
                        [-v|--verbose]
                        [-z|--failfast]
                        [-p|--test-package NAME]
                        [-i|--include PATTERN]
                        [-e|--exclude PATTERN]
                        [-f|--filter PATTERN|@FILEPATH]
                        [-t|--trait [!]NAME[=VALUE]]
                        [-w|--working-directory PATH]
                        [-n|--no-default-patterns]
                        [--no-exitcode]
                        [--no-pathfix]
                        [--parallel [THREADS]]
                        [-r|--report {junit|json}]
                        [-o|--output FILENAME]

Options:
    -h, --help           Show this help text and exit
    --parallel [THREADS]
        Run tests using specified number of worker threads,
        each with its own asyncio event loop.  If omitted
        the default is half the number of CPU cores.
    -q, --quiet          Quiet output
    -v, --verbose        Verbose output
    -z, --failfast       Stop on first failure or error
    -p, --test-package NAME
        Use NAME as the test package, all tests should
        be locatable as modules in the named package.
        Default: 'tests'
    -i, --include PATTERN
        Include test files matching PATTERN
        Default: '*.py'
    -e, --exclude PATTERN
        Exclude test files matching PATTERN, overriding --include
        Default: '__*__' (dunder files)
    -f, --filter PATTERN|@FILEPATH
        Only execute tests matching PATTERN
        Default: '*'
        To specify a file containing a list of filters, prefix
        with '@' and provide the path to the file.
    -t, --trait [!]NAME[=VALUE]
        Execute tests with the specified trait, negated by prefixing with '!'.
        If VALUE is specified, matches tests with the trait having specified value.
        If VALUE is not specified, matches any test with the trait having any value.
        Default: No filtering based on traits.
    -w, --working-directory PATH
        Working directory (defaults to start directory)
    -n, --no-default-patterns
        Do not apply any default include/exclude patterns.
    --no-exitcode
        Do not exit with an error code on unit test failure.
    --no-pathfix
        Do not apply path fixes, rely on PYTHONPATH only.
    -r, --report {html|junit}
        Generate a report to stdout using either an "html"
        or "junit" format. When generating a report to stdout
        all other output is suppressed, unless `--output`
        is also specified.
    -o, --output FILENAME
        If `--report` is used, instead of writing to stdout
        write to FILENAME. In this case `--report` does not
        suppress any program output.
    FILE
        One or more .py files to run directly.
        When any FILE is specified, only those files are tested;
        -p/--test-package, --include, and --exclude patterns on
        discovered files are ignored (test filtering via -f/-t
        still applies).
```

## Writing Tests

You can write tests as functions, class methods, instance methods, or static methods with all forms offering identical functionality. You can also utilize async/await syntax without any additional overhead.

**pUnit** is based upon the fundamental concepts of `Facts` and `Theories`. These are codified using decorators, aptly named `@fact` and `@theory`. Consider these examples:

```python

from punit import fact, theory, inlinedata

@fact
async def MyLibrary_WhenInitialized_TouchMustReturnTrue:
    mylib = MyLibrary()
    mylib.initialize()
    await asyncio.sleep(1)
    assert mylib.touch(), "Expecting touch() to return true, because initialize() was called."

class MyTestFixture:

    def calc(number:int|None = None):
        if number == None:
            raise Exception('Invalid value "None".')
        return number * number

    @theory
    @inlinedata(0, 0)
    @inlinedata(1, 1)
    @inlinedata(2, 4)
    @inlinedata(3, 9)
    @inlinedata(5, 25)
    @inlinedata(8, 64)
    def verifyCalcAssumptions(self, number:int, expected:int) -> None:
        assert expected == self.calc(number)

    @fact
    def verifyCalcErrorCondition(self) -> None:
        from punit.exceptions import raises
        # assert errors are raised, or not
        def calc_None() -> None:
            self.calc(None)
        def calc_1() -> None:
            self.calc(1)
        assert raises[Exception](calc_None)
        assert not raises[Exception](calc_1)
```

Because `pUnit` is a decorative framework you are afforded the utmost freedom in how you structure and implement your tests.

Unlike other testing frameworks, the names you use for functions, classes, and methods is not relevant. There is no requirement to inherit classes from specific abstract/base classes for any particular functionality. There is no requirement that your tests be organized into modules with `__init__.py` files.

You will want to take particular note of the `--exclude` command-line parameter which allows you to restrict what `pUnit` will consider to be a valid test file. While the default behavior will fit 99% of use-cases, you _can_ exercise more control over the discovery process.

## Mocking

pUnit includes a lightweight mocking framework under `punit.mocks`:

```python
from punit.mocks import Mock

m = Mock()
m.method.returns(42)                  # fixed return
assert m.method() == 42
m.method.side_effect([1, 2, 3])       # sequential iteration on call
assert m.method() == 1                 # returns successive items
assert m.method() == 2                 # returns successive items
assert m.method() == 3                 # returns successive items
```

Mock objects configured via `.returns([...])` are directly iterable:

```python
m = Mock()
m.rows.returns([
    Mock(name='Alice'),
    Mock(name='Bob')
])

{u.name for u in m.rows}              # → {'Alice', 'Bob'}
assert len(m.rows) == 2
```

## Vision, Future, and LTS

The long-term vision is to provide both imperative and declarative syntaxes for testing while keeping `pUnit` as simple as possible in its implementation.

`pUnit` is a Python 3.11+ package and there are no plans to backport it to earlier versions of Python, however, user requests (with proposed changes) _will be accepted_ when it makes sense (for example, `pUnit` currently supports Python 3.11, but originally only supported Python 3.12.)

As Python progresses so will `pUnit` and SEMVER rules will be respected to provide developers with assurance that a major version of `pUnit` is fit for a particular purpose, thus, if there is ever a breaking change in Python that requires a breaking change in `pUnit` you can expect `pUnit` versioning to reflect this.

In any situation where an undocumented feature may be used maintainers will actively keep watch on deprecation notices and removals, will clearly identify these dependencies in the docs, and most importantly will provide a LTS alternative to any undocumented feature or such features will not be included in `pUnit`.

With respect to long-term support, we will commit to maintaining major versions for 3 years from the date they were superceded by a new major version. This should align well with Python Core Development.

## Contact

You can reach me on [Discord](https://discordapp.com/users/307684202080501761) or [open an Issue on Github](https://github.com/wilson0x4d/punit/issues/new/choose).
