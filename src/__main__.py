# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from .cli import *
from .discovery import *
from .reports import HtmlReportGenerator, JUnitReportGenerator
from .runner import *

async def async_main():
    ts = time.time()
    cli = CommandLineInterface.parse()
    if cli.help:
        cli.printHelp()
    elif cli.verbose and not cli.quiet:
        cli.printSummary()
    elif not cli.quiet:
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
            failureCount += 1
    if not cli.quiet:
        print(f'Total: {len(results)}, Failures: {failureCount}, Took: {totalTime:.3f}s')
    if cli.reportFormat is not None:
        report:str = None
        match cli.reportFormat:
            case 'html':
                report = HtmlReportGenerator().generate(results)
            case 'junit':
                report = JUnitReportGenerator().generate(results)
        if cli.outputFilename is None:
            print(report)
        else:
            with open(cli.outputFilename, 'wb') as file:
                file.write(report.encode())
            print(f'\n("{cli.reportFormat}" report written to: {cli.outputFilename})')
    if failureCount > 0:
        exit(119)

def main():
    asyncio.run(async_main())

if (__name__ == '__main__'):
    main()
