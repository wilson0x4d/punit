# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
import os
import sys
import time
from pathlib import Path

from .TextIOCapture import teardown_global_text_io
from .cli import CommandLineInterface
from .discovery import TestModuleDiscovery
from .facts.FactManager import FactManager
from .reports import HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator
from .runner import TestRunner
from .setups.SetupManager import SetupManager
from .teardowns.TeardownManager import TeardownManager
from .theories.TheoryManager import TheoryManager


async def async_main() -> None:
    start_time = time.time()
    cli = CommandLineInterface.parse()
    if cli.help:  # pragma: no cover
        cli.print_help()
    elif cli.verbose and not cli.quiet:  # pragma: no cover
        cli.print_summary()
    elif not cli.quiet:  # pragma: no cover
        cli.print_version()
    os.chdir(cli.workdir)
    if cli.no_pathfix is not True:
        cwd_path = str(Path.cwd())
        src_path = os.path.join(cwd_path, 'src')
        if os.path.exists(src_path) and src_path not in sys.path:
            sys.path.append(src_path)
        if cwd_path not in sys.path:
            sys.path.append(cwd_path)
    test_runner: TestRunner
    if cli.files:
        dotnames = []
        for filepath in cli.files:
            rel = os.path.relpath(os.path.abspath(filepath), cli.workdir)
            dotnames.append(
                rel[:-3].replace('\\', '/').replace('/', '.')
            )
        FactManager.instance().excludeTraits = cli.excludeTraits
        FactManager.instance().includeTraits = cli.includeTraits
        TheoryManager.instance().excludeTraits = cli.excludeTraits
        TheoryManager.instance().includeTraits = cli.includeTraits
        test_runner = TestRunner('', dotnames, cli)
    else:
        test_module_discovery = TestModuleDiscovery(
            os.path.join(cli.workdir, cli.test_package_name),
            cli.includePatterns,
            cli.excludePatterns,
            cli)
        test_module_discovery.discover()
        test_runner = TestRunner(cli.test_package_name, test_module_discovery.filenames, cli)
    results = await test_runner.run()
    total_time = time.time() - start_time
    # Detach IO captures so report and summary output use real stdout/stderr
    teardown_global_text_io()
    failure_count = 0
    for result in results:
        if not result.is_success:
            failure_count += 1  # pragma: no cover
    if not cli.quiet:
        print(f'Total: {len(results)}, Failures: {failure_count}, Took: {total_time:.3f}s')
    if cli.reportFormat is not None:  # pragma: no cover
        report: str = ''
        match cli.reportFormat:
            case 'html':
                report = HtmlReportGenerator().generate(results)
            case 'junit':
                report = JUnitReportGenerator().generate(results)
            case 'json':
                report = JsonReportGenerator().generate(results)
        if len(report) > 0:
            if cli.outputFilename is None:
                print(report)
            else:
                with open(cli.outputFilename, 'wb') as file:
                    file.write(report.encode())
                print(f'\n("{cli.reportFormat}" report written to: {cli.outputFilename})')

    # not everyone runs python unbuffered in CI, so force a flush
    try:
        if hasattr(sys.stdout, 'flush') and hasattr(sys.stderr, 'flush'):
            sys.stdout.flush()
            sys.stderr.flush()
        if hasattr(sys.stdout, 'fileno') and hasattr(sys.stderr, 'fileno'):
            os.fsync(sys.stdout.fileno())
            os.fsync(sys.stderr.fileno())
    except (AttributeError, ValueError, OSError):
        pass

    if cli.no_exitcode is not True:
        if failure_count:
            # test failures trigger exit code 119 (for automation gating)
            sys.exit(119)
        if TeardownManager.instance().teardown_error_count > 0:
            # teardown errors also trigger exit code 119 (for automation gating)
            sys.exit(119)
        if SetupManager.instance().setup_error_count > 0:
            # setup errors also trigger exit code 119 (for automation gating)
            sys.exit(119)


def main() -> None:
    asyncio.run(async_main())


if (__name__ == '__main__'):
    main()
