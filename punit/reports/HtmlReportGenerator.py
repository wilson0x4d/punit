# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import traceback
from ..TestResult import TestResult

class HtmlReportGenerator:

    def __init__(self):
        pass

    def generate(self, testResults:list[TestResult]) -> str:
        failureCount = 0
        totalCount = 0
        for testResult in testResults:
            totalCount += 1
            if not testResult.isSuccess:
                failureCount += 1
        testResults = testResults.copy()
        testResults.sort(key=lambda e : e.moduleName)
        lines = []
        lines.append('<html>')
        lines.append('<head><title>Test Results</title></head>')
        lines.append('<body>')
        lines.append("""
                     <style>
                     body { font-family: sans-serif }
                     .testresults-summary { border-bottom:solid 3px steelblue; font-size: 2em; display: flex; flex-direction: row; justify-content: center }
                     .testresults-summary div { flex-grow: 1 }
                     .testresults-summary .pass { color: green; }
                     .testresults-summary .fail { color: red; }
                     .module-name { font-style: italic }
                     .testresult { background-color: #EEE; margin-bottom: 2em; padding: 1em }
                     .testresult-pass { border: solid 1px green }
                     .testresult-fail { border: solid 1px red }
                     .testresult .test-time { border: solid 1px black; padding: 0.3em }
                     .percent-pass { color: green }
                     .percent-fail { color: red }
                     .testresult-body { margin: 1em; border: solid 1px silver; background-color: #FFF  }
                     .testresult-error { border-left: solid 3px red; font-family: monospace; padding: 0.8em }
                     .testresult-stdout { font-family: monospace; max-height: 10em; overflow: auto; padding: 0.8em }
                     .testresult-stderr { font-family: monospace; max-height: 10em; overflow: auto; padding: 0.8em }
                     .test-time-pass { background-color: #EFE }
                     .test-time-fail { background-color: #FEE }
                     </style>
                     """)
        
        lines.append('<div class="testresults-summary">')
        lines.append('<div>&nbsp;</div>')
        lines.append(f'<div>Total Executed: <span class="pass">{totalCount-failureCount}</span></div>')
        if failureCount > 0:
            lines.append('<div>&nbsp;</div>')
            lines.append(f'<div>Total Failed: <span class="fail">{failureCount}</span></div>')
        lines.append('<div>&nbsp;</div>')
        percentstyle = 'pass' if failureCount == 0 else 'fail'
        lines.append(f'<div class="passfail-percent">Pass/Fail&nbsp;<span class="percent-{percentstyle}">{100-(((failureCount/totalCount) if totalCount > 0 else 1)*100):.1f}%</span></div>')
        lines.append('<div>&nbsp;</div>')
        lines.append('</div>')
        currentModuleName = None
        for testResult in testResults:
            if currentModuleName != testResult.moduleName:
                if currentModuleName is not None:
                    lines.append('</div>')
                lines.append('<div class="testresults-module">')
                lines.append(f'<h2 class="module-name">{testResult.packageName}/{testResult.moduleName}</h2>')
                currentModuleName = testResult.moduleName                
            passfailstyle = '-pass' if testResult.isSuccess else '-fail'
            passfailglyph = '🟩' if testResult.isSuccess else '🟥'
            lines.append(f'<div class="testresult testresult{passfailstyle}">')
            lines.append('<div class="testresult-heading">')
            lines.append(f'<span class="glyph glyph{passfailstyle}">{passfailglyph}</span>')
            lines.append(f'<span class="test-class">{"" if testResult.className is None else testResult.className}</span>')
            lines.append(f'<span class="test-name">{testResult.testName}</span>')
            lines.append(f'<span class="test-time test-time{passfailstyle}">{testResult.tookPretty}</span>')
            lines.append('</div>')
            if not testResult.isSuccess or testResult.stdout is not None or testResult.stderr is not None:
                lines.append('<div class="testresult-body">')
                if not testResult.isSuccess:
                    lines.append('<div class="testresult-error">')
                    if len(f'{testResult.exception}') > 0:
                        lines.append(f'Error:<br/>&nbsp;&nbsp;{testResult.exception}<br/>')
                    lines.append(f'Traceback:<br/>{"".join(traceback.format_tb(testResult.exception.__traceback__)).replace('\n', '<br/>').replace(' ', '&nbsp;')}')
                    lines.append('</pre></div>')
                if testResult.stdout is not None:
                    lines.append(f'<div class="testresult-stdout"><pre>{testResult.stdout}</pre></div>')
                if testResult.stderr is not None:
                    lines.append(f'<div class="testresult-stderr"><pre>{testResult.stderr}</pre></div>')
                lines.append('</div>')
            lines.append('</div>')
        lines.append('</body>')
        lines.append('</html>')
        return '\n'.join(lines)
