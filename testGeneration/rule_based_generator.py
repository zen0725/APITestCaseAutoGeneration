from typing import Dict, List, Optional, Set, Any
from testGeneration.test_models import APIEndpoint, TestCase, TestType, TestPriority, GenerationContext
import random
import string
import re
from datetime import datetime, timedelta

class RuleBasedTestGenerator:
    def __init__(self):
        self.security_patterns = self._initialize_security_patterns()
        self.performance_patterns = self._initialize_performance_patterns()
        self.edge_case_patterns = self._initialize_edge_case_patterns()
        self.value_generators = self._initialize_value_generators()

    def _initialize_security_patterns(self) -> Dict[str, List[str]]:
        """初始化安全测试模式"""
        return {
            'sql_injection': [
                "' OR '1'='1", "' UNION SELECT NULL--", "'; DROP TABLE users--",
                "' OR 1=1--", "admin'--", "' OR 'a'='a", "' OR 1=1#", "' OR '1'='1'--"
            ],
            'xss': [
                '<script>alert(1)</script>', '<img src=x onerror=alert(1)>',
                '<svg onload=alert(1)>', 'javascript:alert(1)',
                '"><script>alert(1)</script>', '"><img src=x onerror=alert(1)>'
            ],
            'path_traversal': [
                '../../etc/passwd', '..\\..\\windows\\system32\\drivers\\etc\\hosts',
                '%2e%2e%2fetc%2fpasswd', '....//....//etc/passwd'
            ],
            'command_injection': [
                '; ls -la', '| cat /etc/passwd', '`id`', '$(whoami)',
                '; ping -c 1 localhost', '| whoami'
            ],
            'nosql_injection': [
                '{"$ne": null}', '{"$gt": ""}', '{"$where": "sleep(1000)"}',
                '{"$exists": true}', '{"$regex": ".*"}'
            ],
            'xml_injection': [
                '<!ENTITY xxe SYSTEM "file:///etc/passwd">',
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            ],
            'ldap_injection': [
                '*', 'admin*', '(objectClass=*)', '(|(uid=*))'
            ]
        }

    def _initialize_performance_patterns(self) -> Dict[str, Any]:
        """初始化性能测试模式"""
        return {
            'large_payload_sizes': [100, 500, 1000, 5000, 10000],  # KB
            'concurrent_requests': [10, 50, 100, 200],
            'response_time_thresholds': [100, 500, 1000, 2000]  # ms
        }

    def _initialize_edge_case_patterns(self) -> Dict[str, List[Any]]:
        """初始化边缘案例模式"""
        return {
            'numeric': [0, -1, 999999, -999999, 0.0, -0.0, float('inf'), float('-inf')],
            'string': ['', ' ', '\t', '\n', '\r\n', '\0', 'null', 'NULL', 'None', 'NaN'],
            'unicode': ['中文', '🌍', 'ñáéíóú', '🚀', '😊'],
            'special_chars': ['!@#$%^&*()', '{}[]|\\;:\'"<>,./?'],
            'whitespace_variants': ['  ', '\t\t', '\n\n', '\r\n\r\n']
        }

    def _initialize_value_generators(self) -> Dict[str, callable]:
        """初始化值生成器"""
        return {
            'string': self._generate_string_value,
            'integer': self._generate_integer_value,
            'number': self._generate_number_value,
            'boolean': self._generate_boolean_value,
            'array': self._generate_array_value,
            'object': self._generate_object_value
        }

    def generate_rule_based_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成规则-based测试用例"""
        test_cases = []

        # 根据测试类型调用相应的生成器
        if context.test_type == TestType.POSITIVE:
            test_cases.extend(self._generate_positive_cases(context))
        elif context.test_type == TestType.NEGATIVE:
            test_cases.extend(self._generate_negative_cases(context))
        elif context.test_type == TestType.BOUNDARY:
            test_cases.extend(self._generate_boundary_cases(context))
        elif context.test_type == TestType.SECURITY:
            test_cases.extend(self._generate_security_cases(context))
        elif context.test_type == TestType.PERFORMANCE:
            test_cases.extend(self._generate_performance_cases(context))
        elif context.test_type == TestType.EDGE_CASE:
            test_cases.extend(self._generate_edge_cases(context))
        elif context.test_type == TestType.COMPATIBILITY:
            test_cases.extend(self._generate_compatibility_cases(context))

        # 限制生成数量并去重
        return self._deduplicate_cases(test_cases)[:10]

    def _generate_positive_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成正向测试用例"""
        test_cases = []
        endpoint = context.endpoint

        # 基础正向测试用例
        base_payload = self._generate_base_payload(endpoint, use_valid_values=True)
        test_cases.append(self._create_test_case(
            context=context,
            name=f"正向测试 - 有效参数",
            description=f"使用有效参数测试{endpoint.path}",
            payload=base_payload,
            expected_status=self._get_expected_success_status(endpoint),
            priority=TestPriority.MEDIUM,
            tags={'positive', 'valid'}
        ))

        # 可选参数测试
        if any(not param.required for param in endpoint.parameters):
            optional_payload = self._generate_optional_params_payload(endpoint)
            test_cases.append(self._create_test_case(
                context=context,
                name=f"正向测试 - 可选参数",
                description=f"测试{endpoint.path}的可选参数处理",
                payload=optional_payload,
                expected_status=self._get_expected_success_status(endpoint),
                priority=TestPriority.MEDIUM,
                tags={'positive', 'optional'}
            ))

        # 最小参数集测试
        minimal_payload = self._generate_minimal_payload(endpoint)
        test_cases.append(self._create_test_case(
            context=context,
            name=f"正向测试 - 最小参数集",
            description=f"使用最小必需参数测试{endpoint.path}",
            payload=minimal_payload,
            expected_status=self._get_expected_success_status(endpoint),
            priority=TestPriority.MEDIUM,
            tags={'positive', 'minimal'}
        ))

        return test_cases

    def _generate_negative_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成负向测试用例"""
        test_cases = []
        endpoint = context.endpoint

        # 缺失必需参数测试
        for param in endpoint.parameters:
            if param.required:
                missing_param_payload = self._generate_missing_param_payload(endpoint, param.name)
                test_cases.append(self._create_test_case(
                    context=context,
                    name=f"负向测试 - 缺失必需参数 {param.name}",
                    description=f"测试缺失必需参数{param.name}时的错误处理",
                    payload=missing_param_payload,
                    expected_status=400,
                    priority=TestPriority.HIGH,
                    tags={'negative', 'missing-required'}
                ))

        # 类型错误测试
        for param in endpoint.parameters:
            if param.param_type.value in ['integer', 'number', 'boolean']:
                wrong_type_payload = self._generate_wrong_type_payload(endpoint, param)
                test_cases.append(self._create_test_case(
                    context=context,
                    name=f"负向测试 - 参数类型错误 {param.name}",
                    description=f"测试参数{param.name}类型错误时的处理",
                    payload=wrong_type_payload,
                    expected_status=400,
                    priority=TestPriority.HIGH,
                    tags={'negative', 'type-error'}
                ))

        # 空值测试
        for param in endpoint.parameters:
            if param.required:
                empty_value_payload = self._generate_empty_value_payload(endpoint, param.name)
                test_cases.append(self._create_test_case(
                    context=context,
                    name=f"负向测试 - 空值参数 {param.name}",
                    description=f"测试必需参数{param.name}为空值时的处理",
                    payload=empty_value_payload,
                    expected_status=400,
                    priority=TestPriority.HIGH,
                    tags={'negative', 'empty-value'}
                ))

        return test_cases

    def _generate_boundary_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成边界值测试用例"""
        test_cases = []
        endpoint = context.endpoint

        for param in endpoint.parameters:
            # 数值型参数边界测试
            if param.param_type.value in ['integer', 'number']:
                boundary_values = self._get_numeric_boundary_values(param)
                for value_name, value in boundary_values.items():
                    test_cases.append(self._create_test_case(
                        context=context,
                        name=f"边界测试 - {param.name}.{value_name}",
                        description=f"测试参数{param.name}的边界值{value_name}: {value}",
                        payload=self._generate_single_param_payload(endpoint, param.name, value),
                        expected_status=400 if 'invalid' in value_name else 200,
                        priority=TestPriority.HIGH,
                        tags={'boundary', 'numeric', param.name}
                    ))

            # 字符串型参数边界测试
            elif param.param_type.value == 'string':
                boundary_values = self._get_string_boundary_values(param)
                for value_name, value in boundary_values.items():
                    test_cases.append(self._create_test_case(
                        context=context,
                        name=f"边界测试 - {param.name}.{value_name}",
                        description=f"测试参数{param.name}的边界值{value_name}",
                        payload=self._generate_single_param_payload(endpoint, param.name, value),
                        expected_status=400 if 'invalid' in value_name else 200,
                        priority=TestPriority.HIGH,
                        tags={'boundary', 'string', param.name}
                    ))

        return test_cases

    def _generate_security_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成安全测试用例"""
        test_cases = []
        endpoint = context.endpoint

        # 对每个字符串参数进行安全测试
        for param in endpoint.parameters:
            if param.param_type.value == 'string':
                for attack_type, payloads in self.security_patterns.items():
                    for i, payload in enumerate(payloads[:2]):  # 每种攻击类型测试2个payload
                        test_cases.append(self._create_test_case(
                            context=context,
                            name=f"安全测试 - {param.name}.{attack_type}",
                            description=f"测试参数{param.name}对{attack_type}攻击的防护",
                            payload=self._generate_single_param_payload(endpoint, param.name, payload),
                            expected_status=400,  # 期望返回错误而不是成功
                            priority=TestPriority.CRITICAL,
                            tags={'security', attack_type, param.name}
                        ))

        return test_cases

    def _generate_performance_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成性能测试用例"""
        test_cases = []
        endpoint = context.endpoint

        # 大数据量测试
        for size in self.performance_patterns['large_payload_sizes'][:2]:
            large_payload = self._generate_large_payload(endpoint, size)
            test_cases.append(self._create_test_case(
                context=context,
                name=f"性能测试 - 大数据量 {size}KB",
                description=f"测试{endpoint.path}处理{size}KB数据量的性能",
                payload=large_payload,
                expected_status=200,
                priority=TestPriority.MEDIUM,
                tags={'performance', 'large-payload'}
            ))

        return test_cases

    def _generate_edge_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成边缘案例测试用例"""
        test_cases = []
        endpoint = context.endpoint

        # 特殊值测试
        for param in endpoint.parameters:
            edge_values = self._get_edge_values(param)
            for value_name, value in edge_values.items():
                test_cases.append(self._create_test_case(
                    context=context,
                    name=f"边缘案例 - {param.name}.{value_name}",
                    description=f"测试参数{param.name}的特殊值: {value}",
                    payload=self._generate_single_param_payload(endpoint, param.name, value),
                    expected_status=200,  # 边缘案例可能成功也可能失败
                    priority=TestPriority.LOW,
                    tags={'edge-case', param.name, value_name}
                ))

        return test_cases

    def _generate_compatibility_cases(self, context: GenerationContext) -> List[TestCase]:
        """生成兼容性测试用例"""
        test_cases = []
        endpoint = context.endpoint

        # 不同内容类型测试
        content_types = ['application/json', 'application/x-www-form-urlencoded', 'text/plain']
        for content_type in content_types[:1]:  # 测试第一种内容类型
            test_cases.append(self._create_test_case(
                context=context,
                name=f"兼容性测试 - {content_type}",
                description=f"测试{endpoint.path}对{content_type}内容类型的兼容性",
                payload=self._generate_base_payload(endpoint, use_valid_values=True),
                expected_status=200,
                priority=TestPriority.LOW,
                tags={'compatibility', 'content-type'},
                headers={'Content-Type': content_type}
            ))

        return test_cases

    def _generate_base_payload(self, endpoint: APIEndpoint, use_valid_values: bool = True) -> Dict[str, Any]:
        """生成基础payload"""
        payload = {}

        for param in endpoint.parameters:
            if param.required or use_valid_values:
                generator = self.value_generators[param.param_type.value]
                payload[param.name] = generator(param)

        return payload

    def _generate_optional_params_payload(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """生成只包含可选参数的payload"""
        payload = {}

        for param in endpoint.parameters:
            if not param.required:
                generator = self.value_generators[param.param_type.value]
                payload[param.name] = generator(param)

        return payload

    def _generate_minimal_payload(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """生成最小参数集payload"""
        payload = {}

        for param in endpoint.parameters:
            if param.required:
                generator = self.value_generators[param.param_type.value]
                payload[param.name] = generator(param)

        return payload

    def _generate_missing_param_payload(self, endpoint: APIEndpoint, missing_param: str) -> Dict[str, Any]:
        """生成缺失指定参数的payload"""
        payload = self._generate_base_payload(endpoint)
        payload.pop(missing_param, None)
        return payload

    def _generate_wrong_type_payload(self, endpoint: APIEndpoint, param) -> Dict[str, Any]:
        """生成类型错误的payload"""
        payload = self._generate_base_payload(endpoint)

        if param.param_type.value == 'integer':
            payload[param.name] = "not_a_number"
        elif param.param_type.value == 'number':
            payload[param.name] = "not_a_float"
        elif param.param_type.value == 'boolean':
            payload[param.name] = "not_a_boolean"

        return payload

    def _generate_empty_value_payload(self, endpoint: APIEndpoint, param_name: str) -> Dict[str, Any]:
        """生成空值payload"""
        payload = self._generate_base_payload(endpoint)
        payload[param_name] = ""
        return payload

    def _generate_single_param_payload(self, endpoint: APIEndpoint, param_name: str, value: Any) -> Dict[str, Any]:
        """生成只包含单个参数的payload"""
        payload = {}
        param = next((p for p in endpoint.parameters if p.name == param_name), None)

        if param and param.required:
            payload[param_name] = value

        return payload

    def _generate_large_payload(self, endpoint: APIEndpoint, size_kb: int) -> Dict[str, Any]:
        """生成大数据量payload"""
        payload = self._generate_base_payload(endpoint)

        # 找到第一个字符串参数并填充大数据
        for param_name, param_value in payload.items():
            if isinstance(param_value, str):
                payload[param_name] = 'A' * (size_kb * 1024)
                break

        return payload

    def _generate_string_value(self, param) -> str:
        """生成字符串值"""
        if param.enum_values:
            return random.choice(param.enum_values)

        examples = {
            'email': 'test@example.com',
            'uuid': '123e4567-e89b-12d3-a456-426614174000',
            'date': '2023-12-20',
            'date-time': '2023-12-20T10:30:00Z',
            'name': 'Test User',
            'title': 'Test Title',
            'description': 'This is a test description for validation',
            'password': 'SecurePassword123!',
            'username': 'testuser'
        }

        if param.format and param.format in examples:
            return examples[param.format]

        if param.example:
            return str(param.example)

        # 根据参数名称猜测内容
        param_name = param.name.lower()
        if any(keyword in param_name for keyword in ['email', 'mail']):
            return 'user@example.com'
        elif any(keyword in param_name for keyword in ['name', 'username']):
            return 'testuser'
        elif any(keyword in param_name for keyword in ['password', 'pwd']):
            return 'Password123!'
        elif any(keyword in param_name for keyword in ['title', 'subject']):
            return 'Test Title'
        elif any(keyword in param_name for keyword in ['description', 'desc']):
            return 'Test description content'

        return 'test_value'

    def _generate_integer_value(self, param) -> int:
        """生成整数值"""
        if param.enum_values:
            return random.choice(param.enum_values)

        if param.example is not None:
            return int(param.example)

        if param.min_value is not None and param.max_value is not None:
            return random.randint(param.min_value, param.max_value)
        elif param.min_value is not None:
            return param.min_value + 1
        elif param.max_value is not None:
            return max(1, param.max_value - 1)

        # 根据参数名称猜测内容
        param_name = param.name.lower()
        if any(keyword in param_name for keyword in ['age', 'years']):
            return 30
        elif any(keyword in param_name for keyword in ['count', 'quantity', 'qty']):
            return 5
        elif any(keyword in param_name for keyword in ['limit', 'page_size']):
            return 20
        elif any(keyword in param_name for keyword in ['page', 'offset']):
            return 1

        return 42

    def _generate_number_value(self, param) -> float:
        """生成数字值"""
        if param.enum_values:
            return random.choice(param.enum_values)

        if param.example is not None:
            return float(param.example)

        if param.min_value is not None and param.max_value is not None:
            return round(random.uniform(param.min_value, param.max_value), 2)

        # 根据参数名称猜测内容
        param_name = param.name.lower()
        if any(keyword in param_name for keyword in ['price', 'amount', 'cost']):
            return 99.99
        elif any(keyword in param_name for keyword in ['rating', 'score']):
            return 4.5
        elif any(keyword in param_name for keyword in ['percentage', 'ratio']):
            return 0.85

        return 3.14

    def _generate_boolean_value(self, param) -> bool:
        """生成布尔值"""
        return True

    def _generate_array_value(self, param) -> list:
        """生成数组值"""
        return ['item1', 'item2', 'item3']

    def _generate_object_value(self, param) -> dict:
        """生成对象值"""
        return {'key': 'value', 'enabled': True, 'count': 1}

    def _get_numeric_boundary_values(self, param) -> Dict[str, Any]:
        """获取数值型参数的边界值"""
        boundaries = {}

        if param.min_value is not None:
            boundaries['min_valid'] = param.min_value
            boundaries['below_min'] = param.min_value - 1
        else:
            boundaries['min_valid'] = 1
            boundaries['below_min'] = 0

        if param.max_value is not None:
            boundaries['max_valid'] = param.max_value
            boundaries['above_max'] = param.max_value + 1
        else:
            boundaries['max_valid'] = 100
            boundaries['above_max'] = 101

        boundaries.update({
            'zero': 0,
            'negative': -1,
            'large_positive': 999999,
            'large_negative': -999999
        })

        return boundaries

    def _get_string_boundary_values(self, param) -> Dict[str, str]:
        """获取字符串型参数的边界值"""
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
            'xss_payload': '<script>alert("XSS")</script>'
        })

        return boundaries

    def _get_edge_values(self, param) -> Dict[str, Any]:
        """获取边缘值"""
        if param.param_type.value == 'integer':
            return {
                'zero': 0,
                'negative': -1,
                'max_int': 2147483647,
                'min_int': -2147483648
            }
        elif param.param_type.value == 'number':
            return {
                'zero': 0.0,
                'negative': -0.1,
                'large': 999999.99,
                'small': 0.0001
            }
        elif param.param_type.value == 'string':
            return {
                'empty': '',
                'whitespace': '   ',
                'unicode': '中文🌍',
                'special': '!@#$%^&*()'
            }
        elif param.param_type.value == 'boolean':
            return {
                'true': True,
                'false': False
            }

        return {}

    def _get_expected_success_status(self, endpoint: APIEndpoint) -> int:
        """获取预期的成功状态码"""
        # 根据HTTP方法猜测成功状态码
        method = endpoint.method.upper()
        if method == 'POST':
            return 201  # Created
        elif method in ['PUT', 'PATCH', 'DELETE']:
            return 200  # OK
        else:  # GET, HEAD, OPTIONS
            return 200  # OK

    def _create_test_case(self, context: GenerationContext, name: str, description: str,
                          payload: Dict[str, Any], expected_status: int,
                          priority: TestPriority, tags: Set[str],
                          headers: Optional[Dict[str, str]] = None) -> TestCase:
        """创建测试用例对象"""
        import hashlib
        test_id = f"{context.service_name}_{context.endpoint.path}_{hashlib.md5(name.encode()).hexdigest()[:8]}"

        return TestCase(
            test_id=test_id,
            endpoint=context.endpoint,
            test_type=context.test_type,
            name=name,
            description=description,
            payload=payload,
            expected_status=expected_status,
            validation_rules=self._generate_validation_rules(context, expected_status),
            priority=priority,
            tags=tags,
            timeout=30,
            metadata={'headers': headers} if headers else {}
        )

    def _generate_validation_rules(self, context: GenerationContext, expected_status: int) -> List[str]:
        """生成验证规则"""
        rules = []

        if expected_status == 200:
            rules.extend([
                "验证响应状态码为200",
                "验证响应包含有效JSON",
                "验证响应时间小于2秒"
            ])

            # 根据端点类型添加特定验证规则
            if context.endpoint.method.upper() == 'POST':
                rules.append("验证响应包含创建的资源ID")
            elif context.endpoint.method.upper() == 'GET':
                rules.append("验证响应数据结构和预期一致")

        elif expected_status == 201:
            rules.extend([
                "验证响应状态码为201",
                "验证响应包含Location头",
                "验证响应包含创建的资源数据"
            ])
        elif expected_status >= 400:
            rules.extend([
                f"验证响应状态码为{expected_status}",
                "验证响应包含错误信息",
                "验证错误信息格式正确"
            ])

        return rules

    def _deduplicate_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """去重测试用例"""
        seen = set()
        unique_cases = []

        for case in test_cases:
            # 基于名称和payload的唯一性检查
            case_key = (case.name, str(sorted(case.payload.items())))

            if case_key not in seen:
                seen.add(case_key)
                unique_cases.append(case)

        return unique_cases