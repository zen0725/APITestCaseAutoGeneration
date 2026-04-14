from typing import Dict, List
from testGeneration.test_models import APIEndpoint, TestCase, TestType, TestPriority
import random

class BoundaryValueAnalyzer:
    def __init__(self):
        self.boundary_patterns = self._initialize_boundary_patterns()

    def generate_boundary_tests(self, endpoint: APIEndpoint) -> List[TestCase]:
        """生成边界值测试用例"""
        test_cases = []

        # 测试路径参数
        test_cases.extend(self._test_path_parameters(endpoint))

        # 测试查询参数
        test_cases.extend(self._test_query_parameters(endpoint))

        # 测试请求体
        test_cases.extend(self._test_request_body(endpoint))

        return test_cases

    def _test_path_parameters(self, endpoint: APIEndpoint) -> List[TestCase]:
        """测试路径参数边界值"""
        test_cases = []
        path_params = [p for p in endpoint.parameters if p.in_ == 'path']

        for param in path_params:
            boundary_values = self._get_boundary_values(param)
            for value_name, value in boundary_values.items():
                test_case = self._create_boundary_test_case(
                    endpoint, param, value, value_name
                )
                test_cases.append(test_case)

        return test_cases

    def _test_query_parameters(self, endpoint: APIEndpoint) -> List[TestCase]:
        """测试查询参数边界值"""
        test_cases = []
        query_params = [p for p in endpoint.parameters if p.in_ == 'query']

        for param in query_params:
            boundary_values = self._get_boundary_values(param)
            for value_name, value in boundary_values.items():
                test_case = self._create_boundary_test_case(
                    endpoint, param, value, value_name
                )
                test_cases.append(test_case)

        return test_cases

    def _test_request_body(self, endpoint: APIEndpoint) -> List[TestCase]:
        """测试请求体边界值"""
        if not endpoint.request_body:
            return []

        test_cases = []
        # 实现请求体边界值测试逻辑
        return test_cases

    def _get_boundary_values(self, param) -> Dict[str, any]:
        """获取参数的边界值"""
        values = {}

        if param.param_type.value == 'integer':
            values.update(self._get_integer_boundaries(param))
        elif param.param_type.value == 'string':
            values.update(self._get_string_boundaries(param))
        elif param.param_type.value == 'number':
            values.update(self._get_number_boundaries(param))

        return values

    def _get_integer_boundaries(self, param) -> Dict[str, int]:
        """获取整数边界值"""
        boundaries = {}

        if param.min_value is not None:
            boundaries['min_valid'] = param.min_value
            boundaries['below_min'] = param.min_value - 1
        else:
            boundaries['min_valid'] = -2**31
            boundaries['below_min'] = boundaries['min_valid'] - 1

        if param.max_value is not None:
            boundaries['max_valid'] = param.max_value
            boundaries['above_max'] = param.max_value + 1
        else:
            boundaries['max_valid'] = 2**31 - 1
            boundaries['above_max'] = boundaries['max_valid'] + 1

        boundaries.update({
            'zero': 0,
            'negative': -1,
            'large_positive': 999999,
            'large_negative': -999999
        })

        return boundaries

    def _get_string_boundaries(self, param) -> Dict[str, str]:
        """获取字符串边界值"""
        boundaries = {}

        if param.min_length is not None:
            boundaries['min_length'] = 'a' * param.min_length
            boundaries['below_min_length'] = 'a' * (param.min_length - 1) if param.min_length > 0 else ''
        else:
            boundaries['min_length'] = 'a'
            boundaries['below_min_length'] = ''

        if param.max_length is not None:
            boundaries['max_length'] = 'a' * param.max_length
            boundaries['above_max_length'] = 'a' * (param.max_length + 1)
        else:
            boundaries['max_length'] = 'a' * 100
            boundaries['above_max_length'] = 'a' * 101

        boundaries.update({
            'empty_string': '',
            'whitespace': '   ',
            'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'unicode_chars': '中文测试ñáéíóú',
            'sql_injection': "' OR '1'='1",
            'xss_payload': '<script>alert("XSS")</script>',
            'null_bytes': 'test\u0000string'
        })

        return boundaries

    def _get_number_boundaries(self, param) -> Dict[str, float]:
        """获取浮点数边界值"""
        boundaries = {}

        if param.min_value is not None:
            boundaries['min_valid'] = param.min_value
            boundaries['below_min'] = param.min_value - 1
        else:
            #boundaries['min_valid'] = -1.797e+64
            boundaries['min_valid'] = float('-inf')
            boundaries['below_min'] = boundaries['min_valid'] - 1

        if param.max_value is not None:
            boundaries['max_valid'] = param.max_value
            boundaries['above_max'] = param.max_value + 1
        else:
            #boundaries['max_valid'] = 1.797e+64
            boundaries['max_valid'] = float('inf')
            boundaries['above_max'] = boundaries['max_valid'] + 1

        boundaries.update({
            'zero': 0,
            'negative': -1,
            'min_absolute': 2.225e-64
        })

        return boundaries

    def _create_boundary_test_case(self, endpoint: APIEndpoint, param, value: any, value_name: str) -> TestCase:
        """创建边界测试用例"""
        test_id = f"{endpoint.path}_boundary_{param.name}_{value_name}"

        return TestCase(
            test_id=test_id,
            endpoint=endpoint,
            test_type=TestType.BOUNDARY,
            name=f"边界测试: {param.name}.{value_name}",
            description=f"测试参数 {param.name} 的边界值 {value_name} = {value}",
            payload={param.name: value},
            expected_status=400 if 'invalid' in value_name or 'below' in value_name or 'above' in value_name else 200,
            priority=TestPriority.HIGH,
            tags={'boundary', 'parameter', param.name}
        )

    def _initialize_boundary_patterns(self) -> Dict:
        """初始化边界模式"""
        return {
            'integer': {
                'min': -1, 'max': 1, 'zero': 0, 'negative': -100,
                'large_positive': 999999, 'large_negative': -999999
            },
            'string': {
                'empty': '', 'whitespace': '   ', 'special_chars': '!@#$%^&*()',
                'unicode': '中文测试', 'sql_injection': "' OR '1'='1",
                'xss': '<script>alert(1)</script>', 'long_string': 'a' * 1000
            }
        }