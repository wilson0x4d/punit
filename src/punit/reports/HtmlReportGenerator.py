# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import traceback
from ..TestResult import TestResult


class HtmlReportGenerator:

    def generate(self, test_results: list[TestResult]) -> str:
        failureCount = 0
        totalCount = 0
        for test_result in test_results:
            totalCount += 1
            if not test_result.is_success:
                failureCount += 1
        test_results = test_results.copy()
        test_results.sort(key=lambda e: e.module_name)  # type: ignore[arg-type, return-value]
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
                     .expected-failure { color: orange; font-style: italic; font-size: 0.9em }
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
        for test_result in test_results:
            if currentModuleName != test_result.module_name:
                if currentModuleName is not None:
                    lines.append('</div>')
                lines.append('<div class="testresults-module">')
                lines.append(f'<h2 class="module-name">{test_result.module_name}</h2>')
                currentModuleName = test_result.module_name
            passfailstyle = '-pass' if test_result.is_success else '-fail'
            passfailglyph = '🟩' if test_result.is_success else '🟥'
            lines.append(f'<div class="testresult testresult{passfailstyle}">')
            lines.append('<div class="testresult-heading">')
            lines.append(f'<span class="glyph glyph{passfailstyle}">{passfailglyph}</span>')
            if test_result.expected_failure_reason is not None:
                lines.append(
                    f'<span class="expected-failure">'
                    f' (expected failure: {test_result.expected_failure_reason})'
                    f'</span>'
                )
            if test_result.is_skip:
                lines.append(
                    f'<span style="color: grey; font-style: italic;"> (skipped)</span>'
                )
            class_name = "" if test_result.class_name is None else f"{test_result.class_name}."
            data = test_result.properties.get('data')
            if data is not None and len(data) > 0:
                lines.append(f'<span class="test-class">{class_name}</span><span class="test-name">{test_result.test_name}{data}</span>')
            else:
                lines.append(f'<span class="test-class">{class_name}</span><span class="test-name">{test_result.test_name}</span>')
            lines.append(f'<span class="test-time test-time{passfailstyle}">{test_result.tookPretty}</span>')
            lines.append('</div>')
            if not test_result.is_success or test_result.stdout is not None or test_result.stderr is not None:
                lines.append('<div class="testresult-body">')
                if not test_result.is_success:
                    lines.append('<div class="testresult-error">')
                    if test_result.exception is not None:
                        if len(f'{test_result.exception}') > 0:
                            lines.append(f'Error:<br/>&nbsp;&nbsp;{test_result.exception}<br/>')
                        tbstr = "".join(traceback.format_tb(test_result.exception.__traceback__)).replace('\n', '<br/>').replace(' ', '&nbsp;')
                        lines.append(f'Traceback:<br/>{tbstr}')
                    lines.append('</pre></div>')
                if test_result.stdout is not None:
                    lines.append(f'<div class="testresult-stdout"><pre>{test_result.stdout}</pre></div>')
                if test_result.stderr is not None:
                    lines.append(f'<div class="testresult-stderr"><pre>{test_result.stderr}</pre></div>')
                lines.append('</div>')
            lines.append('</div>')
        lines.append('</body>')
        lines.append('</html>')
        return '\n'.join(lines)
