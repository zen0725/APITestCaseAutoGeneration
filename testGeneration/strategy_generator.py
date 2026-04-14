from typing import Dict, List, Set, Any
from testGeneration.test_models import APIEndpoint, TestType, TestGenerationConfig, TestPriority, ParameterType, APIParameter
import itertools

class TestStrategyGenerator:
    def __init__(self):
        #self.common_vulnerabilities = {
        #    'sql_injection': ["' OR '1'='1", "' UNION SELECT NULL--", "'; DROP TABLE users--"],
        #    'xss': ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>'],
        #    'path_traversal': ['../../etc/passwd', '..\\..\\windows\\system32\\drivers\\etc\\hosts'],
        #    'command_injection': ['; ls -la', '| cat /etc/passwd', '`id`']
        #}
        self.security_patterns = self._load_security_patterns()
        self.performance_indicators = ['search', 'export', 'report', 'batch', 'process']
        self.critical_operations = ['create', 'update', 'delete', 'payment', 'auth']

    def generate_test_strategy(self, endpoint: APIEndpoint, config: TestGenerationConfig) -> List[TestType]:
        """为端点生成测试策略"""
        strategies = [TestType.POSITIVE]

        if config.include_negative_tests:
            strategies.append(TestType.NEGATIVE)

        if config.include_boundary_tests and self._has_constrained_parameters(endpoint):
            strategies.append(TestType.BOUNDARY)

        if config.include_security_tests and self._is_security_sensitive(endpoint):
            strategies.append(TestType.SECURITY)

        if config.include_performance_tests and self._is_performance_critical(endpoint):
            strategies.append(TestType.PERFORMANCE)

        if config.include_edge_cases:
            strategies.append(TestType.EDGE_CASE)

        # 总是包含兼容性测试
        strategies.append(TestType.COMPATIBILITY)

        return strategies

    def determine_test_priority(self, endpoint: APIEndpoint) -> TestPriority:
        """确定测试优先级"""
        path = endpoint.path.lower()
        method = endpoint.method.upper()

        # 关键操作高优先级
        if any(op in path for op in self.critical_operations):
            return TestPriority.CRITICAL

        # 写操作高优先级
        if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return TestPriority.HIGH

        # 读操作中等优先级
        if method in ['GET', 'HEAD']:
            return TestPriority.MEDIUM

        return TestPriority.LOW

    def _has_constrained_parameters(self, endpoint: APIEndpoint) -> bool:
        """检查是否有约束参数"""
        for param in endpoint.parameters:
            if (param.min_value is not None or param.max_value is not None or
                    param.min_length is not None or param.max_length is not None or
                    param.pattern is not None or param.enum_values):
                return True

        if endpoint.request_body:
            return self._check_schema_for_constraints(endpoint.request_body)

        return False

    def _check_schema_for_constraints(self, schema: Dict) -> bool:
        """检查Schema中的约束"""
        constraints = ['minimum', 'maximum', 'minLength', 'maxLength', 'pattern', 'enum']

        for constraint in constraints:
            if constraint in schema:
                return True

        if schema.get('type') == 'object' and 'properties' in schema:
            for prop_schema in schema['properties'].values():
                if self._check_schema_for_constraints(prop_schema):
                    return True

        if schema.get('type') == 'array' and 'items' in schema:
            return self._check_schema_for_constraints(schema['items'])

        return False

    def _has_numeric_parameters(self, endpoint: APIEndpoint) -> bool:
        """检查是否有数值型参数"""
        numeric_types = {ParameterType.INTEGER, ParameterType.NUMBER}

        for param in endpoint.parameters:
            if param.param_type in numeric_types:
                return True

        if endpoint.request_body:
            return self._check_schema_for_numeric(endpoint.request_body)

        return False

    def _check_schema_for_numeric(self, schema: Dict) -> bool:
        """检查Schema中是否有数值类型"""
        if schema.get('type') in ['integer', 'number']:
            return True

        if schema.get('type') == 'object' and 'properties' in schema:
            for prop_schema in schema['properties'].values():
                if self._check_schema_for_numeric(prop_schema):
                    return True

        if schema.get('type') == 'array' and 'items' in schema:
            return self._check_schema_for_numeric(schema['items'])

        return False

    def _is_security_sensitive(self, endpoint: APIEndpoint) -> bool:
        """检查是否是安全敏感端点"""
        sensitive_paths = ['/auth', '/login', '/user', '/admin', '/password', '/token']
        sensitive_methods = ['POST', 'PUT', 'DELETE']

        path = endpoint.path.lower()
        if any(sensitive_path in path for sensitive_path in sensitive_paths):
            return True

        if endpoint.method in sensitive_methods and endpoint.parameters:
            return True

        if endpoint.security:
            return True

        # 检查操作ID或摘要中的安全关键词
        operation_text = (endpoint.operation_id or '').lower() + (endpoint.summary or '').lower()
        security_keywords = ['auth', 'login', 'password', 'token', 'secret', 'key']
        return any(keyword in operation_text for keyword in security_keywords)


    def _is_performance_critical(self, endpoint: APIEndpoint) -> bool:
        """检查是否是性能关键端点"""
        #performance_critical_paths = ['/search', '/export', '/report', '/batch']
        #return any(path in endpoint.path for path in performance_critical_paths)
        path = endpoint.path.lower()
        return any(indicator in path for indicator in self.performance_indicators)

    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """加载安全测试模式"""
        return {
            'sql_injection': [
                "' OR '1'='1", "' UNION SELECT NULL--", "'; DROP TABLE users--",
                "' OR 1=1--", "admin'--", "' OR 'a'='a"
            ],
            'xss': [
                '<script>alert(1)</script>', '<img src=x onerror=alert(1)>',
                '<svg onload=alert(1)>', 'javascript:alert(1)'
            ],
            'path_traversal': [
                '../../etc/passwd', '..\\..\\windows\\system32\\drivers\\etc\\hosts',
                '%2e%2e%2fetc%2fpasswd'
            ],
            'command_injection': [
                '; ls -la', '| cat /etc/passwd', '`id`', '$(whoami)'
            ],
            'nosql_injection': [
                '{"$ne": null}', '{"$gt": ""}', '{"$where": "sleep(1000)"}'
            ]
        }

    def generate_parameter_combinations(self, endpoint: APIEndpoint, max_combinations: int = 50) -> List[Dict]:
        """生成参数组合用于测试"""
        param_values = {}

        for param in endpoint.parameters:
            param_values[param.name] = self._generate_param_values(param)

        # 生成组合，但限制数量
        combinations = []
        for combination in itertools.product(*param_values.values()):
            if len(combinations) >= max_combinations:
                break
            param_dict = dict(zip(param_values.keys(), combination))
            combinations.append(param_dict)

        return combinations

    def _generate_param_values(self, param: APIParameter) -> List[Any]:
        """为参数生成测试值"""
        values = []

        # 基本值
        if param.param_type == ParameterType.STRING:
            values.extend(self._generate_string_values(param))
        elif param.param_type == ParameterType.INTEGER:
            values.extend(self._generate_integer_values(param))
        elif param.param_type == ParameterType.BOOLEAN:
            values.extend([True, False])

        # 枚举值
        if param.enum_values:
            values.extend(param.enum_values)

        return list(set(values))  # 去重

    def _generate_string_values(self, param: APIParameter) -> List[str]:
        """生成字符串测试值"""
        values = ['test', 'example']

        if param.format == 'email':
            values.extend(['test@example.com', 'invalid-email', ''])
        elif param.format == 'uuid':
            values.extend(['123e4567-e89b-12d3-a456-426614174000', 'invalid-uuid'])

        # 边界值
        if param.min_length is not None:
            values.append('a' * param.min_length)
        if param.max_length is not None:
            values.append('a' * param.max_length)
            values.append('a' * (param.max_length + 1) if param.max_length > 0 else '')

        return values

    def _generate_integer_values(self, param: APIParameter) -> List[int]:
        """生成整数测试值"""
        values = [0, 1, 100]

        if param.min_value is not None:
            values.append(param.min_value)
            values.append(param.min_value - 1)
        if param.max_value is not None:
            values.append(param.max_value)
            values.append(param.max_value + 1)

        return values