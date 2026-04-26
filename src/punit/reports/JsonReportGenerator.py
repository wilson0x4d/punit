# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import json
import traceback
from typing import Any

from ..TestResult import TestResult



class JsonReportGenerator:

    def generate(self, testResults:list[TestResult]) -> str:
        testResults.sort(key=lambda e : e.moduleName)
        results = list[dict[str, Any]]()
        for testResult in testResults:
            result = dict[str, Any]({
                'status': 'pass' if testResult.isSuccess else 'fail',
                'name': testResult.testName,
            })
            if testResult.took is not None:
                result['took'] = round(testResult.took * 1000, 3)
            if not testResult.isSuccess:
                if testResult.exception is not None:
                    result['message'] = f'{testResult.exception}\n{"".join(traceback.format_tb(testResult.exception.__traceback__))}'
                else:
                    result['message'] = 'Unknown Error'
            results.append(result)
        return json.dumps(results)
