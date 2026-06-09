# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
import os
import sys
import time
from pathlib import Path

from .cli import CommandLineInterface
from .discovery import TestModuleDiscovery
from .reports import HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator
from .runner import TestRunner
from .teardowns.TeardownManager import TeardownManager


async def async_main() -> None:
    ts = time.time()
    cli = CommandLineInterface.parse()
    if cli.help:  # pragma: no cover
        cli.print_help()
    elif cli.verbose and not cli.quiet:  # pragma: no cover
        cli.print_summary()
    elif not cli.quiet:  # pragma: no cover
        cli.print_version()
    os.chdir(cli.workdir)
    if cli.no_pathfix is not True:
        pathbase = str(Path.cwd())
        srcbase = os.path.join(pathbase, 'src')
        if os.path.exists(srcbase) and srcbase not in sys.path:
            sys.path.append(srcbase)
        if pathbase not in sys.path:
            sys.path.append(pathbase)
    test_module_discovery = TestModuleDiscovery(
        os.path.join(cli.workdir, cli.test_package_name),
        cli.includePatterns,
        cli.excludePatterns,
        cli)
    test_module_discovery.discover()
    testRunner = TestRunner(cli.test_package_name, test_module_discovery.filenames, cli)
    results = await testRunner.run()
    totalTime = time.time() - ts
    failureCount = 0
    for result in results:
        if not result.is_success:
            failureCount += 1  # pragma: no cover
    if not cli.quiet:
        print(f'Total: {len(results)}, Failures: {failureCount}, Took: {totalTime:.3f}s')
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

    # not everyone runs python unbuffered as they should, so force a flush
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        os.fsync(sys.stdout.fileno())
        os.fsync(sys.stderr.fileno())
    except (AttributeError, ValueError, OSError):
        pass

    if cli.no_exitcode is not True:
        if failureCount:
            # test failures trigger exit code 119 (for automation gating)
            sys.exit(119)
        if TeardownManager.instance().teardown_error_count > 0:
            # teardown errors also trigger exit code 119 (for automation gating)
            sys.exit(119)


def main() -> None:
    asyncio.run(async_main())


if (__name__ == '__main__'):
    main()
