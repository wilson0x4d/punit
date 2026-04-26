# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
import os
import time
from .cli import CommandLineInterface
from .discovery import TestModuleDiscovery
from .reports import HtmlReportGenerator, JUnitReportGenerator, JsonReportGenerator
from .runner import TestRunner


async def async_main() -> None:
    ts = time.time()
    cli = CommandLineInterface.parse()
    if cli.help: # pragma: no cover
        cli.printHelp()
    elif cli.verbose and not cli.quiet: # pragma: no cover
        cli.printSummary()
    elif not cli.quiet: # pragma: no cover
        cli.printVersion()
    os.chdir(cli.workdir)
    testModuleDiscovery = TestModuleDiscovery(
        os.path.join(cli.workdir, cli.testPackageName),
        cli.includePatterns,
        cli.excludePatterns,
        cli)
    testModuleDiscovery.discover()
    testRunner = TestRunner(cli.testPackageName, testModuleDiscovery.filenames, cli)
    results = await testRunner.run()
    totalTime = time.time() - ts
    failureCount = 0
    for result in results:
        if not result.isSuccess:
            failureCount += 1 # pragma: no cover
    if not cli.quiet:
        print(f'Total: {len(results)}, Failures: {failureCount}, Took: {totalTime:.3f}s')
    if cli.reportFormat is not None: # pragma: no cover
        report:str = ''
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
    if failureCount > 0:
        exit(119) # pragma: no cover

def main() -> None:
    asyncio.run(async_main())

if (__name__ == '__main__'):
    main()
