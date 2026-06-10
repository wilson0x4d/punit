# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import json
import traceback
from typing import Any

from ..TestResult import TestResult


class JsonReportGenerator:

    def generate(self, test_results: list[TestResult]) -> str:
        test_results.sort(key=lambda e: e.module_name)  # type: ignore[arg-type, return-value]
        results = list[dict[str, Any]]()
        for test_result in test_results:
            filter_name: str = f'{test_result.module_name}'
            if test_result.class_name is not None:
                filter_name = f'{filter_name}/{test_result.class_name}'
            filter_name = f'{filter_name}/{test_result.test_name}'
            data = test_result.properties.get('data')
            if data is not None and len(data) > 0:
                filter_name = f'{filter_name}{data}'
            result = dict[str, Any]({
                'status': 'pass' if test_result.is_success else 'fail',
                'name': filter_name,
            })
            if test_result.expected_failure_reason is not None:
                result['expected_failure'] = True
                if test_result.expected_failure_reason is not None:
                    result['expected_failure_reason'] = test_result.expected_failure_reason
            if test_result.took is not None:
                result['took'] = round(test_result.took * 1000, 3)
            if not test_result.is_success:
                if test_result.exception is not None:
                    result['message'] = f'{test_result.exception}\n{"".join(traceback.format_tb(test_result.exception.__traceback__))}'
                else:
                    result['message'] = f'Unknown Error!\n\nstdout:\n{test_result.stdout}\n\nstderr:\n{test_result.stderr}'
            elif test_result.stdout is not None:
                result['message'] = test_result.stdout
            elif test_result.stderr is not None:
                result['message'] = test_result.stderr
            results.append(result)
        return json.dumps(results)
