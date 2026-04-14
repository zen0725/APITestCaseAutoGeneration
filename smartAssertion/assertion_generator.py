from typing import Dict, List, Optional, Callable, Any
from smartAssertion.assertion_models import AssertionRule, AssertionType, AssertionLevel, ResponsePattern, AssertionConfig, AssertionSource
import re
import json
import numpy as np


class DynamicAssertionGenerator:
    def __init__(self, config: AssertionConfig):
        self.config = config
        self.common_assertions = self._initialize_common_assertions()

    def generate_assertions(self, pattern: ResponsePattern, response_data: Dict) -> List[AssertionRule]:
        """生成动态断言"""
        assertions = []

        # 基础断言
        assertions.extend(self._generate_basic_assertions(pattern, response_data))

        # Schema验证断言
        if pattern.schema_pattern:
            assertions.extend(self._generate_schema_assertions(pattern.schema_pattern))

        # 性能断言
        assertions.extend(self._generate_performance_assertions(pattern, response_data))

        # 数据验证断言
        #assertions.extend(self._generate_data_validation_assertions(response_data))

        # 数据分布断言
        assertions.extend(self._generate_data_distribution_assertions(pattern, response_data))

        # 业务规则断言（基于端点模式）
        assertions.extend(self._generate_business_rule_assertions(pattern.endpoint, response_data))

        return self._optimize_assertions(assertions)

    def _generate_basic_assertions(self, pattern: ResponsePattern, response_data: Dict) -> List[AssertionRule]:
        """生成基础断言"""
        assertions = []

        # 状态码断言
        assertions.extend(self._generate_status_code_assertions(pattern))

        # JSON有效性断言
        assertions.append(self._create_assertion(
            rule_id="json_validity",
            assertion_type=AssertionType.SCHEMA_VALIDATION,
            description="验证响应为有效JSON",
            condition=lambda resp: self._is_valid_json(resp.get('raw_response', '')),
            level=AssertionLevel.CRITICAL,
            error_message="响应不是有效的JSON格式"
        ))

        return assertions

    def _generate_status_code_assertions(self, pattern: ResponsePattern) -> List[AssertionRule]:
        """生成状态码断言"""
        assertions = []

        # 期望的状态码断言
        for status_code in pattern.normal_status_codes:
            assertions.append(self._create_assertion(
                rule_id=f"status_code_{status_code}",
                assertion_type=AssertionType.STATUS_CODE,
                description=f"验证状态码为{status_code}",
                condition=lambda resp, sc=status_code: resp.get('status_code') == sc,
                level=AssertionLevel.HIGH,
                error_message=f"预期状态码 {status_code}，实际状态码 {{actual_status}}",
                metadata={'expected_status': status_code}
            ))

            return assertions

    def _generate_performance_assertions(self, pattern: ResponsePattern, response_data: Dict) -> List[AssertionRule]:
        """生成性能断言"""
        assertions = []
        response_time = response_data.get('response_time')
        if response_time and pattern.response_time_stats:
            stats = pattern.response_time_stats

            # 响应时间不超过P99的2倍
            threshold = stats['p99', 1000] * 2
            assertions.append(self._create_assertion(
                rule_id="response_time_performance",
                assertion_type=AssertionType.PERFORMANCE,
                description="验证响应时间在正常范围内",
                condition=lambda resp, rt=response_time, th=threshold: rt <= th,
                level=AssertionLevel.MEDIUM,
                error_message=f"响应时间 {response_time}ms 超过阈值 {threshold}ms"
            ))

        return assertions

    def _generate_data_distribution_assertions(self, pattern: ResponsePattern, response_data: Dict) -> List[AssertionRule]:
        """生成数据分布断言"""
        assertions = []

        data = response_data.get('data', {})
        if isinstance(data, dict) and pattern.field_distributions:
            for field_path, distribution in pattern.field_distributions.items():
                field_value = self._get_nested_value(data, field_path)
                if field_value is not None:
                    assertions.extend(
                        self._generate_field_distribution_assertions(field_path, field_value, distribution))

        return assertions

    def _generate_field_distribution_assertions(self, field_path: str, field_value: Any, distribution: Dict) -> List[
        AssertionRule]:
        """生成字段分布断言"""
        assertions = []
        dist_type = distribution.get('type')

        if dist_type == 'numeric':
            min_val = distribution.get('min')
            max_val = distribution.get('max')

            if isinstance(field_value, (int, float)) and min_val is not None and max_val is not None:
                assertions.append(self._create_assertion(
                    rule_id=f"field_range_{field_path}",
                    assertion_type=AssertionType.DATA_VALIDATION,
                    description=f"验证字段 {field_path} 值在正常范围内",
                    condition=lambda resp, f=field_path, v=field_value, mn=min_val, mx=max_val: (
                            mn <= self._get_nested_value(resp.get('data', {}), f) <= mx
                    ),
                    level=AssertionLevel.MEDIUM,
                    error_message=f"字段 {field_path} 值 {field_value} 超出正常范围 [{min_val}, {max_val}]"
                ))

        elif dist_type == 'string':
            min_len = distribution.get('min_length')
            max_len = distribution.get('max_length')

            if isinstance(field_value, str) and min_len is not None and max_len is not None:
                assertions.append(self._create_assertion(
                    rule_id=f"field_length_{field_path}",
                    assertion_type=AssertionType.DATA_VALIDATION,
                    description=f"验证字段 {field_path} 长度在正常范围内",
                    condition=lambda resp, f=field_path, v=field_value, mn=min_len, mx=max_len: (
                            mn <= len(self._get_nested_value(resp.get('data', {}), f)) <= mx
                    ),
                    level=AssertionLevel.LOW,
                    error_message=f"字段 {field_path} 长度 {len(field_value)} 超出正常范围 [{min_len}, {max_len}]"
                ))

        return assertions

    def _generate_schema_assertions(self, schema_pattern: Dict) -> List[AssertionRule]:
        """生成Schema验证断言"""
        assertions = []

        if schema_pattern.get('type') == 'object':
            assertions.extend(self._generate_object_schema_assertions(schema_pattern))

        elif schema_pattern.get('type') == 'array':
            assertions.extend(self._generate_array_schema_assertions(schema_pattern))

        # 递归生成字段级断言
        # if 'properties' in schema_pattern:
        #     for field, field_schema in schema_pattern['properties'].items():
        #         assertions.extend(self._generate_field_assertions(field, field_schema))

        return assertions

    def _generate_object_schema_assertions(self, schema: Dict) -> List[AssertionRule]:
        """生成对象Schema断言"""
        assertions = []

        assertions.append(self._create_assertion(
            rule_id="is_valid_object",
            assertion_type=AssertionType.SCHEMA_VALIDATION,
            description="验证响应为JSON对象",
            condition=lambda resp: isinstance(resp.get('data'), dict),
            level=AssertionLevel.HIGH,
            error_message="响应数据不是JSON对象"
        ))

        if 'properties' in schema:
            for field, field_schema in schema['properties'].items():
                assertions.extend(self._generate_field_assertions(field, field_schema))

        return assertions

    def _generate_field_assertions(self, field: str, field_schema: Dict) -> List[AssertionRule]:
        """生成字段级断言"""
        assertions = []

        # 字段存在性断言
        assertions.append(self._create_assertion(
            rule_id=f"field_exists_{field}",
            assertion_type=AssertionType.SCHEMA_VALIDATION,
            description=f"验证字段 {field} 存在",
            condition=lambda resp, f=field: f in resp.get('data', {}),
            level=AssertionLevel.HIGH,
            error_message=f"缺少必需字段 {field}"
        ))

        # 字段类型断言
        if 'type' in field_schema:
            type_assertion = self._create_type_assertion(field, field_schema['type'])
            if type_assertion:
                assertions.append(type_assertion)

        return assertions

    def _create_type_assertion(self, field: str, expected_type: str) -> Optional[AssertionRule]:
        """创建类型断言"""
        type_checks = {
            'string': lambda x: isinstance(x, str),
            'integer': lambda x: isinstance(x, int),
            'number': lambda x: isinstance(x, (int, float)),
            'boolean': lambda x: isinstance(x, bool),
            'array': lambda x: isinstance(x, list),
            'object': lambda x: isinstance(x, dict)
        }

        if expected_type in type_checks:
            return self._create_assertion(
                rule_id=f"field_type_{field}",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证字段 {field} 的类型为 {expected_type}",
                condition=lambda resp, f=field, check=type_checks[expected_type]:(check(resp.get('data', {}).get(f))),
                level=AssertionLevel.MEDIUM,
                error_message=f"字段 {field} 类型错误，预期 {expected_type}"
            )

        return None

    def _generate_array_schema_assertions(self, schema: Dict) -> List[AssertionRule]:
        """生成数组Schema验证断言"""
        assertions = []

        # 基本数组类型断言
        assertions.append(self._create_assertion(
            rule_id="is_valid_array",
            assertion_type=AssertionType.SCHEMA_VALIDATION,
            description="验证响应为JSON数组",
            condition=lambda resp: isinstance(resp.get('data'), list),
            level=AssertionLevel.HIGH,
            error_message="响应数据不是JSON数组"
        ))

        # 数组长度验证
        assertions.extend(self._generate_array_length_assertions(schema))

        # 数组元素验证
        if 'items' in schema:
            assertions.extend(self._generate_array_items_assertions(schema['items']))

        # 数组唯一性验证
        if schema.get('uniqueItems', False):
            assertions.extend(self._generate_array_uniqueness_assertions())

        # 数组排序验证
        if 'sort' in schema:
            assertions.extend(self._generate_array_sorting_assertions(schema['sort']))

        return assertions

    def _generate_array_length_assertions(self, schema: Dict) -> List[AssertionRule]:
        """生成数组长度验证断言"""
        assertions = []

        # 最小长度验证
        if 'minItems' in schema:
            min_items = schema['minItems']
            assertions.append(self._create_assertion(
                rule_id="array_min_length",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证数组长度不小于{min_items}",
                condition=lambda resp, mi=min_items: (
                        isinstance(resp.get('data'), list) and
                        len(resp['data']) >= mi
                ),
                level=AssertionLevel.HIGH,
                error_message=f"数组长度不能小于{min_items}"
            ))

        # 最大长度验证
        if 'maxItems' in schema:
            max_items = schema['maxItems']
            assertions.append(self._create_assertion(
                rule_id="array_max_length",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证数组长度不超过{max_items}",
                condition=lambda resp, mi=max_items: (
                        isinstance(resp.get('data'), list) and
                        len(resp['data']) <= mi
                ),
                level=AssertionLevel.HIGH,
                error_message=f"数组长度不能超过{max_items}"
            ))

        # 精确长度验证
        if 'exactItems' in schema:
            exact_items = schema['exactItems']
            assertions.append(self._create_assertion(
                rule_id="array_exact_length",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证数组长度等于{exact_items}",
                condition=lambda resp, ei=exact_items: (
                        isinstance(resp.get('data'), list) and
                        len(resp['data']) == ei
                ),
                level=AssertionLevel.MEDIUM,
                error_message=f"数组长度必须等于{exact_items}"
            ))

        return assertions

    def _generate_array_items_assertions(self, items_schema: Dict) -> List[AssertionRule]:
        """生成数组元素验证断言"""
        assertions = []

        # 数组元素类型验证
        item_type = items_schema.get('type')
        if item_type:
            assertions.append(self._create_assertion(
                rule_id="array_items_type",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证数组元素类型为{item_type}",
                condition=lambda resp, it=item_type: self._validate_array_items_type(resp.get('data', []), it),
                level=AssertionLevel.HIGH,
                error_message=f"数组元素类型必须为{item_type}"
            ))

        # 数组元素格式验证
        if 'format' in items_schema:
            format_type = items_schema['format']
            assertions.append(self._create_assertion(
                rule_id="array_items_format",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证数组元素格式为{format_type}",
                condition=lambda resp, ft=format_type: self._validate_array_items_format(resp.get('data', []), ft),
                level=AssertionLevel.MEDIUM,
                error_message=f"数组元素格式必须为{format_type}"
            ))

        # 数组元素枚举值验证
        if 'enum' in items_schema:
            enum_values = items_schema['enum']
            assertions.append(self._create_assertion(
                rule_id="array_items_enum",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description="验证数组元素在枚举值范围内",
                condition=lambda resp, ev=enum_values: self._validate_array_items_enum(resp.get('data', []), ev),
                level=AssertionLevel.MEDIUM,
                error_message="数组元素必须在预定义的枚举值范围内"
            ))

        # 数组元素模式验证（正则表达式）
        if 'pattern' in items_schema:
            pattern = items_schema['pattern']
            assertions.append(self._create_assertion(
                rule_id="array_items_pattern",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description="验证数组元素符合模式要求",
                condition=lambda resp, p=pattern: self._validate_array_items_pattern(resp.get('data', []), p),
                level=AssertionLevel.MEDIUM,
                error_message="数组元素不符合模式要求"
            ))

        # 嵌套对象数组验证
        if items_schema.get('type') == 'object' and 'properties' in items_schema:
            assertions.extend(self._generate_nested_object_array_assertions(items_schema))

        # 嵌套数组验证（多维数组）
        if items_schema.get('type') == 'array':
            assertions.extend(self._generate_nested_array_assertions(items_schema))

        return assertions

    def _generate_nested_object_array_assertions(self, items_schema: Dict) -> List[AssertionRule]:
        """生成嵌套对象数组验证断言"""
        assertions = []
        properties = items_schema.get('properties', {})

        for field, field_schema in properties.items():
            # 嵌套字段存在性验证
            assertions.append(self._create_assertion(
                rule_id=f"array_items_object_{field}_exists",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证数组元素对象包含字段{field}",
                condition=lambda resp, f=field: self._validate_array_object_field_exists(resp.get('data', []), f),
                level=AssertionLevel.HIGH,
                error_message=f"数组元素对象缺少必需字段{field}"
            ))

            # 嵌套字段类型验证
            field_type = field_schema.get('type')
            if field_type:
                assertions.append(self._create_assertion(
                    rule_id=f"array_items_object_{field}_type",
                    assertion_type=AssertionType.SCHEMA_VALIDATION,
                    description=f"验证数组元素对象的字段{field}类型为{field_type}",
                    condition=lambda resp, f=field, ft=field_type: self._validate_array_object_field_type(
                        resp.get('data', []), f, ft),
                    level=AssertionLevel.MEDIUM,
                    error_message=f"数组元素对象的字段{field}类型必须为{field_type}"
                ))

        return assertions

    def _generate_nested_array_assertions(self, items_schema: Dict) -> List[AssertionRule]:
        """生成嵌套数组验证断言"""
        assertions = []

        # 嵌套数组维度验证
        assertions.append(self._create_assertion(
            rule_id="nested_array_dimension",
            assertion_type=AssertionType.SCHEMA_VALIDATION,
            description="验证嵌套数组维度一致性",
            condition=lambda resp: self._validate_nested_array_dimension(resp.get('data', [])),
            level=AssertionLevel.MEDIUM,
            error_message="嵌套数组维度不一致"
        ))

        # 嵌套数组元素类型验证
        nested_item_type = items_schema.get('items', {}).get('type')
        if nested_item_type:
            assertions.append(self._create_assertion(
                rule_id="nested_array_items_type",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证嵌套数组元素类型为{nested_item_type}",
                condition=lambda resp, nit=nested_item_type: self._validate_nested_array_items_type(
                    resp.get('data', []), nit),
                level=AssertionLevel.MEDIUM,
                error_message=f"嵌套数组元素类型必须为{nested_item_type}"
            ))

        return assertions

    def _generate_array_uniqueness_assertions(self) -> List[AssertionRule]:
        """生成数组唯一性验证断言"""
        return [
            self._create_assertion(
                rule_id="array_unique_items",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description="验证数组元素唯一性",
                condition=lambda resp: self._validate_array_uniqueness(resp.get('data', [])),
                level=AssertionLevel.MEDIUM,
                error_message="数组包含重复元素"
            )
        ]

    def _generate_array_sorting_assertions(self, sort_config: Dict) -> List[AssertionRule]:
        """生成数组排序验证断言"""
        assertions = []

        sort_by = sort_config.get('by')
        order = sort_config.get('order', 'asc')  # asc or desc

        if sort_by:
            assertions.append(self._create_assertion(
                rule_id="array_sorted",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description=f"验证数组按{sort_by}字段{order}排序",
                condition=lambda resp, sb=sort_by, o=order: self._validate_array_sorted(resp.get('data', []), sb, o),
                level=AssertionLevel.LOW,
                error_message=f"数组未按{sort_by}字段{order}排序"
            ))

        return assertions

    def _validate_array_items_type(self, array_data: List, expected_type: str) -> bool:
        """验证数组元素类型"""
        if not isinstance(array_data, list):
            return False

        type_checks = {
            'string': lambda x: isinstance(x, str),
            'integer': lambda x: isinstance(x, int),
            'number': lambda x: isinstance(x, (int, float)),
            'boolean': lambda x: isinstance(x, bool),
            'object': lambda x: isinstance(x, dict),
            'array': lambda x: isinstance(x, list)
        }

        if expected_type not in type_checks:
            return True  # 未知类型，跳过验证

        check_func = type_checks[expected_type]
        return all(check_func(item) for item in array_data)

    def _validate_array_items_format(self, array_data: List, format_type: str) -> bool:
        """验证数组元素格式"""
        if not isinstance(array_data, list):
            return False

        format_checks = {
            'email': lambda x: isinstance(x, str) and re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', x),
            'uuid': lambda x: isinstance(x, str) and re.match(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', x, re.I),
            'date': lambda x: isinstance(x, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', x),
            'date-time': lambda x: isinstance(x, str) and re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', x)
        }

        if format_type not in format_checks:
            return True  # 未知格式，跳过验证

        check_func = format_checks[format_type]
        return all(check_func(item) for item in array_data if item is not None)

    def _validate_array_items_enum(self, array_data: List, enum_values: List) -> bool:
        """验证数组元素在枚举值范围内"""
        if not isinstance(array_data, list):
            return False

        return all(item in enum_values for item in array_data if item is not None)

    def _validate_array_items_pattern(self, array_data: List, pattern: str) -> bool:
        """验证数组元素符合正则表达式模式"""
        if not isinstance(array_data, list):
            return False

        try:
            regex = re.compile(pattern)
            return all(regex.match(str(item)) for item in array_data if item is not None)
        except re.error:
            return True  # 无效正则表达式，跳过验证

    def _validate_array_object_field_exists(self, array_data: List, field: str) -> bool:
        """验证数组元素对象包含指定字段"""
        if not isinstance(array_data, list):
            return False

        return all(isinstance(item, dict) and field in item for item in array_data)

    def _validate_array_object_field_type(self, array_data: List, field: str, expected_type: str) -> bool:
        """验证数组元素对象的字段类型"""
        if not isinstance(array_data, list):
            return False

        type_checks = {
            'string': lambda x: isinstance(x, str),
            'integer': lambda x: isinstance(x, int),
            'number': lambda x: isinstance(x, (int, float)),
            'boolean': lambda x: isinstance(x, bool)
        }

        if expected_type not in type_checks:
            return True

        check_func = type_checks[expected_type]
        return all(
            isinstance(item, dict) and field in item and check_func(item[field])
            for item in array_data
            if item is not None
        )

    def _validate_nested_array_dimension(self, array_data: List) -> bool:
        """验证嵌套数组维度一致性"""
        if not isinstance(array_data, list):
            return False

        # 检查所有子数组是否具有相同长度
        subarray_lengths = [len(subarray) for subarray in array_data if isinstance(subarray, list)]
        if not subarray_lengths:
            return True

        return len(set(subarray_lengths)) == 1  # 所有子数组长度相同

    def _validate_nested_array_items_type(self, array_data: List, expected_type: str) -> bool:
        """验证嵌套数组元素类型"""
        if not isinstance(array_data, list):
            return False

        type_checks = {
            'string': lambda x: isinstance(x, str),
            'integer': lambda x: isinstance(x, int),
            'number': lambda x: isinstance(x, (int, float)),
            'boolean': lambda x: isinstance(x, bool)
        }

        if expected_type not in type_checks:
            return True

        check_func = type_checks[expected_type]

        for subarray in array_data:
            if not isinstance(subarray, list):
                return False
            if not all(check_func(item) for item in subarray if item is not None):
                return False

        return True

    def _validate_array_uniqueness(self, array_data: List) -> bool:
        """验证数组元素唯一性"""
        if not isinstance(array_data, list):
            return False

        # 对于基本类型，直接比较
        if all(isinstance(item, (str, int, float, bool)) for item in array_data):
            return len(array_data) == len(set(array_data))

        # 对于复杂类型（字典、列表），使用JSON字符串比较
        try:
            unique_items = set(json.dumps(item, sort_keys=True) for item in array_data)
            return len(array_data) == len(unique_items)
        except (TypeError, ValueError):
            # 如果无法序列化，使用对象ID比较（对于同一对象的引用）
            return len(array_data) == len(set(id(item) for item in array_data))

    def _validate_array_sorted(self, array_data: List, sort_by: str, order: str) -> bool:
        """验证数组排序"""
        if not isinstance(array_data, list) or len(array_data) < 2:
            return True

        # 提取排序字段值
        sort_values = []
        for item in array_data:
            if isinstance(item, dict) and sort_by in item:
                sort_values.append(item[sort_by])
            else:
                # 如果缺少排序字段，无法验证排序
                return True

        # 检查是否按指定顺序排序
        if order == 'asc':
            return all(sort_values[i] <= sort_values[i + 1] for i in range(len(sort_values) - 1))
        else:  # desc
            return all(sort_values[i] >= sort_values[i + 1] for i in range(len(sort_values) - 1))



    def _generate_data_validation_assertions(self, response_data: Dict) -> List[AssertionRule]:
        """生成数据验证断言"""
        assertions = []
        data = response_data.get('data', {})

        if isinstance(data, dict):
            # ID字段验证
            for field in ['id', 'uuid', 'guid']:
                if field in data and data[field]:
                    assertions.append(AssertionRule(
                        rule_id=f"data_valid_{field}",
                        assertion_type=AssertionType.DATA_VALIDATION,
                        description=f"验证 {field} 字段格式",
                        condition=lambda resp, f=field: self._validate_id_format(resp.get('data', {}).get(f)),
                        level=AssertionLevel.MEDIUM,
                        error_message=f"{field} 字段格式无效"
                    ))

            # 时间字段验证
            for field in ['created_at', 'updated_at', 'timestamp']:
                if field in data and data[field]:
                    assertions.append(AssertionRule(
                        rule_id=f"data_valid_{field}",
                        assertion_type=AssertionType.DATA_VALIDATION,
                        description=f"验证 {field} 字段为有效时间戳",
                        condition=lambda resp, f=field: self._validate_timestamp(resp.get('data', {}).get(f)),
                        level=AssertionLevel.MEDIUM,
                        error_message=f"{field} 时间戳格式无效"
                    ))

        return assertions

    def _generate_business_rule_assertions(self, endpoint: str, response_data: Dict) -> List[AssertionRule]:
        """生成业务规则断言"""
        assertions = []
        data = response_data.get('data', {})

        # 基于端点模式的业务规则
        endpoint_lower = endpoint.lower()
        # if '/users/' in endpoint and 'GET' in endpoint:
        #     assertions.extend(self._generate_user_business_rules(data))
        # elif '/orders/' in endpoint:
        #     assertions.extend(self._generate_order_business_rules(data))
        # elif '/products/' in endpoint:
        #     assertions.extend(self._generate_product_business_rules(data))
        if any(keyword in endpoint_lower for keyword in ['user', 'customer']):
            assertions.extend(self._generate_user_business_rules(data))
        elif any(keyword in endpoint_lower for keyword in ['order', 'cart']):
            assertions.extend(self._generate_order_business_rules(data))
        elif any(keyword in endpoint_lower for keyword in ['product', 'item']):
            assertions.extend(self._generate_product_business_rules(data))
        elif any(keyword in endpoint_lower for keyword in ['payment', 'transaction']):
            assertions.extend(self._generate_payment_business_rules(data))

        return assertions

    def _generate_user_business_rules(self, data: Dict) -> List[AssertionRule]:
        """生成用户相关的业务规则断言"""
        assertions = []

        if 'email' in data:
            assertions.append(self._create_assertion(
                rule_id="user_email_format",
                assertion_type=AssertionType.BUSINESS_RULE,
                description="验证用户邮箱格式",
                condition=lambda resp: self._validate_email(resp.get('data', {}).get('email')),
                level=AssertionLevel.HIGH,
                error_message="用户邮箱格式无效"
            ))

        if 'status' in data:
            assertions.append(self._create_assertion(
                rule_id="business_user_status",
                assertion_type=AssertionType.BUSINESS_RULE,
                description="验证用户状态值",
                condition=lambda resp: resp.get('data', {}).get('status') in ['active', 'inactive', 'pending'],
                level=AssertionLevel.MEDIUM,
                error_message="用户状态值无效"
            ))

        return assertions

    def _generate_order_business_rules(self, data: Dict) -> List[AssertionRule]:
        """生成订单业务规则断言"""
        assertions = []

        if 'total_amount' in data and 'items' in data:
            assertions.append(self._create_assertion(
                rule_id="order_total_calculation",
                assertion_type=AssertionType.BUSINESS_RULE,
                description="验证订单总价计算正确",
                condition=lambda resp: self._validate_order_total(resp.get('data', {})),
                level=AssertionLevel.CRITICAL,
                error_message="订单总价计算错误"
            ))

        return assertions

    def _generate_product_business_rules(self, data: Dict) -> List[AssertionRule]:
        """生成商品业务规则断言"""
        assertions = []

        if 'price' in data:
            assertions.append(self._create_assertion(
                rule_id="product_price_positive",
                assertion_type=AssertionType.BUSINESS_RULE,
                description="验证商品价格为正数",
                condition=lambda resp: resp.get('data', {}).get('price', 0) > 0,
                level=AssertionLevel.HIGH,
                error_message="商品价格必须大于0"
            ))

        return assertions

    def _generate_payment_business_rules(self, data: Dict) -> List[AssertionRule]:
        """生成支付业务规则断言"""
        assertions = []

        if 'amount' in data:
            assertions.append(self._create_assertion(
                rule_id="payment_amount_positive",
                assertion_type=AssertionType.BUSINESS_RULE,
                description="验证支付金额为正数",
                condition=lambda resp: resp.get('data', {}).get('amount', 0) > 0,
                level=AssertionLevel.HIGH,
                error_message="支付金额必须大于0"
            ))

        return assertions

    def _optimize_assertions(self, assertions: List[AssertionRule]) -> List[AssertionRule]:
        """优化断言列表"""
        # 去重
        unique_assertions = []
        seen = set()

        for assertion in assertions:
            if assertion.rule_id not in seen:
                seen.add(assertion.rule_id)
                unique_assertions.append(assertion)

        # 按优先级排序并限制数量
        unique_assertions.sort(key=lambda x: x.level.value, reverse=True)
        return unique_assertions[:self.config.max_assertions_per_endpoint]

    def _create_assertion(self, rule_id: str, assertion_type: AssertionType, description: str,
                          condition: Callable, level: AssertionLevel, error_message: str,
                          metadata: Optional[Dict] = None) -> AssertionRule:
        """创建断言规则"""
        return AssertionRule(
            rule_id=rule_id,
            assertion_type=assertion_type,
            description=description,
            condition=condition,
            level=level,
            error_message=error_message,
            metadata=metadata or {},
            source=AssertionSource.RULE_BASED
        )

    def _validate_id_format(self, value: Any) -> bool:
        """验证ID格式"""
        if not isinstance(value, (str, int)):
            return False
        return bool(str(value).strip())

    def _validate_timestamp(self, value: Any) -> bool:
        """验证时间戳格式"""
        if not isinstance(value, (str, int)):
            return False

        try:
            # 尝试解析时间戳
            if isinstance(value, str):
                # ISO格式时间戳
                from datetime import datetime
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                # Unix时间戳
                from datetime import datetime
                datetime.fromtimestamp(value)
            return True
        except (ValueError, TypeError, OSError):
            return False

    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        if not isinstance(email, str):
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_order_total(self, order_data: Dict) -> bool:
        """验证订单总价计算"""
        try:
            total = order_data.get('total_amount', 0)
            items = order_data.get('items', [])

            calculated_total = sum(
                item.get('quantity', 0) * item.get('unit_price', 0)
                for item in items
            )

            # 允许小的浮点数误差
            return abs(total - calculated_total) < 0.01
        except (TypeError, ValueError):
            return False

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """获取嵌套字段值"""
        try:
            parts = path.split('.')
            value = data
            for part in parts:
                if part.endswith('[]') and isinstance(value, list):
                    part = part[:-2]
                    if value:
                        value = value[0].get(part)
                    else:
                        return None
                else:
                    value = value.get(part)
                if value is None:
                    return None
            return value
        except (AttributeError, TypeError):
            return None

    def _initialize_common_assertions(self) -> Dict[str, AssertionRule]:
        """初始化通用断言"""
        return {
            'json_valid': self._create_assertion(
                rule_id="common_json_valid",
                assertion_type=AssertionType.SCHEMA_VALIDATION,
                description="验证响应为有效JSON",
                condition=lambda resp: self._is_valid_json(resp.get('raw_response', '')),
                level=AssertionLevel.CRITICAL,
                error_message="响应不是有效的JSON"
            ),
            'no_server_error': self._create_assertion(
                rule_id="common_no_server_error",
                assertion_type=AssertionType.STATUS_CODE,
                description="验证没有服务器错误",
                condition=lambda resp: resp.get('status_code', 0) < 500,
                level=AssertionLevel.CRITICAL,
                error_message="服务器返回5xx错误"
            )
        }

    def _is_valid_json(self, text: str) -> bool:
        """验证是否为有效JSON"""
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, TypeError):
            return False