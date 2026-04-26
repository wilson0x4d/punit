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
            filterName:str = f'{testResult.packageName}/{testResult.moduleName}'
            if testResult.className is not None:
                filterName = f'{filterName}/{testResult.className}'
            filterName = f'{filterName}/{testResult.testName}'
            data = testResult.properties.get('data')
            if data is not None and len(data) > 0:
                datastr = f'({",".join([str(e) for e in data])})'
                filterName = f'{filterName}{datastr}'
            result = dict[str, Any]({
                'status': 'pass' if testResult.isSuccess else 'fail',
                'name': filterName,
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
