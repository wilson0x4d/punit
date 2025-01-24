`pUnit` is a modernized unit-testing framework for Python, inspired by xUnit.

This README is only a high-level introduction to **pUnit**. For more detailed documentation, please view the official docs at [https://pUnit.readthedocs.io](https://pUnit.readthedocs.io).

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
Usage: python3 -m punit [-h|--help]
                        [-q|--quiet] [-v|--verbose]
                        [-f|--failfast]
                        [-p|--test-package NAME]
                        [-i|--include PATTERN]
                        [-e|--exclude PATTERN]
                        [-t|--filter PATTERN]
                        [-w|--workdir DIRECTORY]
                        [-n|--no-default-patterns]
                        [-r|--report {junit|json}]
                        [-o|--output FILENAME]

Options:
    -h, --help           Show this help text and exit
    -q, --quiet          Quiet output
    -v, --verbose        Verbose output
    -f, --failfast       Stop on first failure or error
    -p, --test-package NAME
        Use NAME as the test package, all tests should
        be locatable as modules in the named package.
        Default: 'tests'
    -i, --include PATTERN
        Include any tests matching PATTERN
        Default: '*.py'
    -e, --exclude PATTERN
        Exclude any tests matching PATTERN, overriding --include
        Default: '__*__' (dunder files), '/.*/' (dot-directories)
    -t, --filter PATTERN
        Only execute tests matching PATTERN
        Default: '*'
    -w, --working-directory DIRECTORY
        Working directory (defaults to start directory)
    -n, --no-default-patterns
        Do not apply any default include/exclude patterns.
    -r, --report {html|junit}
        Generate a report to stdout using either an "html"
        or "junit" format. When generating a report to stdout
        all other output is suppressed, unless `--output`
        is also specified.
    -o, --output FILENAME
        If `--report` is used, instead of writing to stdout
        write to FILENAME. In this case `--report` does not
        suppress any program output.
```

## Writing Tests

You can write tests as functions, class methods, instance methods, or static methods with all forms offering identical functionality. You can also utilize async/await syntax without any additional overhead.

**pUnit** is based upon the fundamental concepts of `Facts` and `Theories`. These are codified using decorators, aptly named `@fact` and `@theory`. Consider these examples:

```python

from punit import *

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
        def calc_None():
            self.calc(None)
        def calc_1()
            self.calc(1)
        assert raises[Exception](calc_None)
        assert not raises[Exception](calc_1)
```

Because `pUnit` is a decorative framework you are afforded the utmost freedom in how you structure and implement your tests.

Unlike other testing frameworks, the names you use for functions, classes, and methods is not relevant. There is no requirement to inherit classes from specific abstract/base classes for any particular functionality. There is no requirement that your tests be organized into modules with `__init__.py` files.

You will want to take particular note of the `--exclude` command-line parameter which allows you to restrict what `pUnit` will consider to be a valid test file. While the default behavior will fit 99% of use-cases, you _can_ exercise more control over the discovery process.

## Vision, Future, and LTS

The long-term vision is to provide both imperative and declarative syntaxes for testing while keeping `pUnit` as simple as possible in its implementation.

`pUnit` is a Python 3.12+ package and there are no plans to backport it to earlier versions of Python, however, user contributions to support backward compatibility _will be accepted_ when it makes sense.

As Python progresses so will `pUnit` and SEMVER rules will be respected to provide developers with assurance that a major version of `pUnit` is fit for a particular purpose, thus, if there is ever a breaking change in Python that requires a breaking change in `pUnit` you can expect `pUnit` versioning to reflect this.

In any situation where an undocumented feature may be used maintainers will actively keep watch on deprecation notices and removals, will clearly identify these dependencies in the docs, and most importantly will provide a LTS alternative to any undocumented feature or such features will not be included in `pUnit`.

With respect to long-term support, we will commit to maintaining major versions for 3 years from the date they were superceded by a new major version. This should align well with Python Core Development.

## Contact

You can reach me on [Discord](https://discordapp.com/users/307684202080501761) or [open an Issue on Github](https://github.com/wilson0x4d/punit/issues/new/choose).
