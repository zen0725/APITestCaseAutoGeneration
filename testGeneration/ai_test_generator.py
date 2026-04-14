import openai
import json
from typing import Dict, List, Optional
from testGeneration.test_models import APIEndpoint, TestCase, TestType, GenerationContext, TestPriority, APIParameter
import re
import asyncio
import hashlib
#from deepseek import DeepSeekAPI
import deepseek


class AITestGenerator:
    def __init__(self, api_key: str, config):
        #openai.api_key = openai_api_key
        self.api_key = api_key
        self.config = config
        self.prompt_templates = self._load_prompt_templates()
        self.knowledge_base = self._load_knowledge_base()
        self.patterns = self._initialize_patterns()
        self.value_generators = self._initialize_value_generators()

    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """初始化正则表达式模式"""
        return {
            'test_case_start': re.compile(r'^Test\s*Case\s*[:：]?\s*(.+)$', re.IGNORECASE),
            'test_name': re.compile(r'^(?:Name|测试名称)[:：]?\s*(.+)$', re.IGNORECASE),
            'test_description': re.compile(r'^(?:Description|描述|说明)[:：]?\s*(.+)$', re.IGNORECASE),
            'payload_section': re.compile(r'^(?:Payload|请求数据|请求负载)[:：]?$', re.IGNORECASE),
            'payload_json': re.compile(r'```json\n(.*?)\n```', re.DOTALL),
            'payload_line': re.compile(r'^\s*[\'"]([^"\']+)[\'"][:：]?\s*[\'"]([^"\']+)[\'"]\s*$'),
            'expected_status': re.compile(r'^(?:Expected Status|预期状态码|状态码)[:：]?\s*(\d{3})$'),
            'validation_rules': re.compile(r'^(?:Validation|验证规则|断言)[:：]?\s*(.+)$', re.IGNORECASE),
            'tags': re.compile(r'^(?:Tags|标签)[:：]?\s*(.+)$', re.IGNORECASE),
            'separator': re.compile(r'^[-=*_]{3,}$'),
            'blank_line': re.compile(r'^\s*$')
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

    async def generate_test_cases(self, context: GenerationContext) -> List[TestCase]:
        """使用AI生成测试用例"""
        test_cases = []

        #for test_type in test_types:
        #    if self.config.enable_ai:
        #        ai_cases = await self._generate_ai_test_cases(endpoint, test_type)
        #        test_cases.extend(ai_cases)
        #    else:
                # 回退到规则-based生成
        #        rule_cases = self._generate_rule_based_cases(endpoint, test_type)
        #        test_cases.extend(rule_cases)
        #return test_cases
        try:
            prompt = self._build_ai_prompt(context)
            print('------------------------------------------------------\n')
            print(prompt)
            #response = await self._call_openai_ai_api(prompt)
            #response = await self._call_deepseek_ai_api(prompt)
            response = self._get_local_api()
            ai_cases = self._parse_ai_response(response, context)
            test_cases.extend(ai_cases)

        except Exception as e:
            print(f"AI测试生成失败: {e}")
            # 回退到规则-based生成
            #rule_cases = self._generate_rule_based_cases(context)
            #test_cases.extend(rule_cases)

        return self._deduplicate_and_optimize(test_cases, context.existing_cases)

    def _build_ai_prompt(self, context: GenerationContext) -> str:
        """构建AI提示词"""
        template = self.prompt_templates.get(context.test_type.value, self.prompt_templates['default'])

        prompt = template.format(
            service_name=context.service_name,
            service_url=context.service_url,
            endpoint_path=context.endpoint.path,
            endpoint_method=context.endpoint.method,
            endpoint_summary=context.endpoint.summary,
            parameters=json.dumps([self._param_to_dict(p) for p in context.endpoint.parameters], indent=2, ensure_ascii=False),
            request_body=json.dumps(context.endpoint.request_body, indent=2) if context.endpoint.request_body else "None",
            responses=json.dumps(context.endpoint.responses, indent=2),
            test_type=context.test_type.value.upper(),
            domain_knowledge=context.domain_knowledge or self._get_domain_knowledge(context.service_name),
            coverage_gap=self._analyze_coverage_gap(context)
        )

        return prompt

    async def _call_openai_ai_api(self, prompt: str) -> str:
        """调用OPENAI API"""
        openai.api_key = self.api_key
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.config.ai_model,
                messages=[
                    {"role": "system", "content": "你是一名资深测试开发专家，擅长微服务API测试。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"AI API调用失败: {e}")

    async def _call_deepseek_ai_api(self, prompt: str) -> str:
        """调用DEEPSEEK API"""
        client = DeepSeekAPI(self.api_key)
        try:
            response = await client.chat_completion(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一名资深测试开发专家，擅长微服务API测试。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"AI API调用失败: {e}")

    def _get_local_api(self) -> str:
        with open('/Users/huangzhen/Documents/deepseek_json.json', 'r') as f:
            local_api = json.load(f)

        return json.dumps(local_api, ensure_ascii=False)

    #async def _generate_ai_test_cases(self, endpoint: APIEndpoint, test_type: TestType) -> List[TestCase]:
    #    """使用AI生成特定类型的测试用例"""
    #    prompt = self._build_ai_prompt(endpoint, test_type)
    #
    #    try:
    #        response = await openai.ChatCompletion.acreate(
    #            model=self.config.ai_model,
    #            messages=[{"role": "user", "content": prompt}],
    #            temperature=self.config.temperature,
    #            max_tokens=2000
    #        )
    #
    #        generated_text = response.choices[0].message.content
    #        return self._parse_ai_response(generated_text, endpoint, test_type)
    #
    #    except Exception as e:
    #        print(f"AI测试生成失败: {e}")
    #        return self._generate_rule_based_cases(endpoint, test_type)

    #def _build_ai_prompt(self, endpoint: APIEndpoint, test_type: TestType) -> str:
    #    """构建AI提示词"""
    #    template = self.prompt_templates.get(test_type, self.prompt_templates['default'])
    #
    #    prompt = template.format(
    #        endpoint_path=endpoint.path,
    #        endpoint_method=endpoint.method,
    #        endpoint_summary=endpoint.summary,
    #        parameters=json.dumps([self._param_to_dict(p) for p in endpoint.parameters], indent=2),
    #        request_body=json.dumps(endpoint.request_body, indent=2) if endpoint.request_body else "None",
    #        responses=json.dumps(endpoint.responses, indent=2)
    #    )
    #
    #    if self.config.use_knowledge_base:
    #        knowledge = self._get_domain_knowledge(endpoint)
    #        prompt += f"\n\n领域知识:\n{knowledge}"
    #
    #    return prompt

    def _parse_ai_response(self, response_text: str, context: GenerationContext) -> List[TestCase]:
        """解析AI生成的响应"""
        #test_cases = []
        try:
            # 尝试提取JSON格式的测试用例
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            # 尝试提取代码块中的JSON
            code_match = re.search(r'```(.*?)```', response_text, re.DOTALL)
            if json_match:
                cases_data = json.loads(json_match.group(1))
                #for case_data in cases_data:
                #    test_case = TestCase(
                #        test_id=f"{endpoint.path}_{test_type.value}_{len(test_cases)}",
                #        endpoint=endpoint,
                #        test_type=test_type,
                #        name=case_data.get('name', ''),
                #        description=case_data.get('description', ''),
                #        payload=case_data.get('payload', {}),
                #        expected_status=case_data.get('expected_status', 200),
                #        expected_schema=case_data.get('expected_schema'),
                #        validation_rules=case_data.get('validation_rules', [])
                #    )
                return [
                    self._create_test_case(case_data, context)
                    for case_data in cases_data
                ]
            elif code_match:
                try:
                    cases_data = json.loads(code_match.group(1))
                    return [
                        self._create_test_case(case_data, context)
                        for case_data in cases_data
                    ]
                except json.JSONDecodeError:
                    pass
                    #test_cases.append(test_case)
            else:
                cases_data = json.loads(response_text)
                return [
                    self._create_test_case(case_data, context)
                    for case_data in cases_data
                ]
            # 最后尝试解析文本格式
            return self._parse_text_response(response_text, context)
        except Exception as e:
            print(f"AI响应解析失败: {e}")
            return []

        # 如果JSON解析失败，尝试文本解析
        #if not test_cases:
        #    test_cases = self._parse_text_response(response_text, endpoint, test_type)
        #
        #return test_cases[:self.config.max_test_cases_per_endpoint]

    def _create_test_case(self, case_data: Dict, context: GenerationContext) -> TestCase:
        """创建测试用例对象"""
        test_id = self._generate_test_id(context, case_data)

        return TestCase(
            test_id=test_id,
            base_url=context.service_url,
            endpoint=context.endpoint,
            test_type=context.test_type,
            name=case_data.get('name', f"{context.test_type.value}_{test_id}"),
            description=case_data.get('description', ''),
            payload=case_data.get('payload', {}),
            expected_status=case_data.get('expected_status', 200),
            expected_schema=case_data.get('expected_schema'),
            validation_rules=case_data.get('validation_rules', []),
            priority=self._determine_case_priority(case_data, context),
            tags=set(case_data.get('tags', []))
        )

    def _generate_test_id(self, context: GenerationContext, case_data: Dict) -> str:
        """生成唯一的测试ID"""
        base_str = f"{context.service_name}_{context.endpoint.path}_{context.test_type.value}_{json.dumps(case_data.get('payload', {}), sort_keys=True)}"
        return hashlib.md5(base_str.encode()).hexdigest()[:8]

    def _determine_case_priority(self, case_data: Dict, context: GenerationContext) -> TestPriority:
        """确定测试用例优先级"""
        # 基于测试类型和内容的启发式规则
        if context.test_type == TestType.SECURITY:
            return TestPriority.CRITICAL
        elif context.test_type == TestType.NEGATIVE and 'error' in case_data.get('description', '').lower():
            return TestPriority.HIGH
        elif context.test_type == TestType.BOUNDARY:
            return TestPriority.HIGH
        return TestPriority.MEDIUM

    def _parse_text_response(self, response_text: str, context: GenerationContext) -> List[TestCase]:
        """解析文本格式的AI响应"""
        lines = response_text.strip().split('\n')
        test_cases = []
        current_case = None
        in_payload_section = False
        payload_lines = []

        for line in lines:
            line = line.strip()
            # 跳过空行和分隔符
            if self.patterns['blank_line'].match(line) or self.patterns['separator'].match(line):
                continue

            # 检测测试用例开始
            match = self.patterns['test_case_start'].match(line)
            if match :
                if current_case:
                    test_cases.append(self._finalize_test_case(current_case, payload_lines, context))
                    payload_lines = []
                current_case = {
                    'name': match.group(1),
                    'description': '',
                    'payload': {},
                    'expected_status': 200,
                    'validation_rules': [],
                    'tags': set()
                }
                in_payload_section = False
                continue

            # 处理现有测试用例
            if current_case:
                # 测试名称
                if self.patterns['test_name'].match(line):
                    current_case['name'] = self.patterns['test_name'].match(line).group(1)
                # 测试描述
                elif self.patterns['test_description'].match(line):
                    current_case['description'] = self.patterns['test_description'].match(line).group(1)
                # 进入payload区域
                elif self.patterns['payload_section'].match(line):
                    in_payload_section = True
                    continue
                # 预期状态码
                elif self.patterns['expected_status'].match(line):
                    current_case['expected_status'] = int(self.patterns['expected_status'].match(line).group(1))
                # 验证规则
                elif self.patterns['validation_rules'].match(line):
                    current_case['validation_rules'].append(self.patterns['validation_rules'].match(line).group(1))
                # 标签
                elif self.patterns['tags'].match(line):
                    tags = [tag.strip() for tag in self.patterns['tags'].match(line).group(1).split(',')]
                    current_case['tags'].update(tags)
                # 处理payload内容
                elif in_payload_section:
                    payload_lines.append(line)
                # 尝试从行中提取键值对
                else:
                    self._try_extract_key_value(line, current_case)


                #if match := self.patterns['test_name'].match(line):
                #    current_case['name'] = match.group(1)
                #elif match := self.patterns['test_description'].match(line):
                #    current_case['description'] = match.group(1)
                #elif self.patterns['payload_section'].match(line):
                #    in_payload_section = True
                #    continue
                #elif match := self.patterns['expected_status'].match(line):
                #    current_case['expected_status'] = int(match.group(1))
                #elif match := self.patterns['validation_rules'].match(line):
                #    current_case['validation_rules'].append(match.group(1))
                #elif match := self.patterns['tags'].match(line):
                #    tags = [tag.strip() for tag in match.group(1).split(',')]
                #    current_case['tags'].update(tags)
                #elif in_payload_section:
                #    payload_lines.append(line)
                #else:
                #    self._try_extract_key_value(line, current_case)

            # 处理最后一个测试用例
            if current_case:
                test_cases.append(self._finalize_test_case(current_case, payload_lines, context))

        return test_cases

    def _try_extract_key_value(self, line: str, current_case: dict):
        """尝试从行中提取键值对"""
        # 尝试匹配 key: value 格式
        if ':' in line and not line.startswith((' ', '\t')):
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip().lower()
                value = parts[1].strip()

                if key in ['name', '测试名称']:
                    current_case['name'] = value
                elif key in ['description', '描述', '说明']:
                    current_case['description'] = value
                elif key in ['status', 'status code', '状态码']:
                    try:
                        current_case['expected_status'] = int(value)
                    except ValueError:
                        pass
                elif key in ['payload', '请求数据']:
                    # 可能是内联的简单payload
                    try:
                        current_case['payload'] = json.loads(value)
                    except json.JSONDecodeError:
                        # 尝试解析为简单键值对
                        self._parse_simple_payload(value, current_case)

    def _parse_simple_payload(self, payload_str: str, current_case: dict):
        """解析简单的payload字符串"""
        # 尝试解析 key=value, key2=value2 格式
        if '=' in payload_str:
            pairs = payload_str.split(',')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    current_case['payload'][key.strip()] = value.strip()

    def _finalize_test_case(self, case_data: dict, payload_lines: List[str], context: GenerationContext) -> TestCase:
        """完成测试用例的构建"""
        # 处理payload
        payload = self._parse_payload(payload_lines, case_data.get('payload', {}), context)

        # 生成测试ID
        #test_id = self._generate_test_id(context, case_data['name'], payload)
        test_id = self._generate_test_id(context, case_data)

        # 设置默认值
        if not case_data.get('description'):
            case_data['description'] = f"{context.test_type.value} test for {context.endpoint.path}"

        # 创建测试用例对象
        return TestCase(
            test_id=test_id,
            endpoint=context.endpoint,
            test_type=context.test_type,
            name=case_data['name'],
            description=case_data['description'],
            payload=payload,
            expected_status=case_data['expected_status'],
            validation_rules=case_data.get('validation_rules', []),
            priority=self._determine_case_priority(case_data, context),
            tags=case_data.get('tags', set()),
            timeout=30
        )

    def _parse_payload(self, payload_lines: List[str], existing_payload: dict, context: GenerationContext) -> dict:
        """解析payload内容"""
        payload = existing_payload.copy()

        # 首先尝试提取JSON代码块
        full_text = '\n'.join(payload_lines)
        json_match = self.patterns['payload_json'].search(full_text)
        if json_match:
            try:
                json_payload = json.loads(json_match.group(1))
                payload.update(json_payload)
                return payload
            except json.JSONDecodeError:
                pass

        # 逐行解析payload
        for line in payload_lines:
            line = line.strip()

            # 跳过注释和空行
            if line.startswith('#') or line.startswith('//') or not line:
                continue

            # 尝试解析JSON行
            if line.startswith('{') and line.endswith('}'):
                try:
                    line_payload = json.loads(line)
                    payload.update(line_payload)
                    continue
                except json.JSONDecodeError:
                    pass

            # 尝试解析键值对
            match = self.patterns['payload_line'].match(line)
            if match:
                key, value = match.groups()
                payload[key] = value
            elif ':' in line and not line.startswith((' ', '\t')):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    # 清理引号
                    if value.startswith(('"', "'")) and value.endswith(('"', "'")):
                        value = value[1:-1]

                    payload[key] = value

        # 如果payload仍然为空，生成基于参数的payload
        if not payload and context.endpoint.parameters:
            payload = self._generate_parameter_based_payload(context)

        return payload

    def _generate_parameter_based_payload(self, context: GenerationContext) -> dict:
        """基于参数生成payload"""
        payload = {}

        for param in context.endpoint.parameters:
            if param.required:
                generator = self.value_generators.get(param.param_type.value, self._generate_string_value)
                payload[param.name] = generator(param)

        return payload

    def _generate_string_value(self, param) -> str:
        """生成字符串值"""
        if param.enum_values:
            return param.enum_values[0]

        examples = {
            'email': 'test@example.com',
            'uuid': '123e4567-e89b-12d3-a456-426614174000',
            'date': '2023-12-20',
            'date-time': '2023-12-20T10:30:00Z',
            'name': 'Test User',
            'title': 'Test Title',
            'description': 'This is a test description'
        }

        if param.format and param.format in examples:
            return examples[param.format]

        if param.example:
            return str(param.example)

        return 'test_value'

    def _generate_integer_value(self, param) -> int:
        """生成整数值"""
        if param.enum_values:
            return param.enum_values[0]

        if param.example:
            return int(param.example)

        if param.min_value is not None:
            return max(param.min_value, 1)

        return 42

    def _generate_number_value(self, param) -> float:
        """生成数字值"""
        if param.enum_values:
            return param.enum_values[0]

        if param.example:
            return float(param.example)

        return 3.14

    def _generate_boolean_value(self, param) -> bool:
        """生成布尔值"""
        return True

    def _generate_array_value(self, param) -> list:
        """生成数组值"""
        return ['item1', 'item2', 'item3']

    def _generate_object_value(self, param) -> dict:
        """生成对象值"""
        return {'key': 'value'}

    # def _generate_test_id(self, context: GenerationContext, name: str, payload: dict) -> str:
    #     """生成测试ID"""
    #     import hashlib
    #     base_str = f"{context.service_name}_{context.endpoint.path}_{name}_{json.dumps(payload, sort_keys=True)}"
    #     return hashlib.md5(base_str.encode()).hexdigest()[:12]

    # def _determine_priority(self, test_type: TestType, case_data: dict) -> TestPriority:
    #     """确定测试优先级"""
    #     priority_map = {
    #         TestType.SECURITY: TestPriority.CRITICAL,
    #         TestType.NEGATIVE: TestPriority.HIGH,
    #         TestType.BOUNDARY: TestPriority.HIGH,
    #         TestType.PERFORMANCE: TestPriority.MEDIUM,
    #         TestType.POSITIVE: TestPriority.MEDIUM,
    #         TestType.EDGE_CASE: TestPriority.LOW,
    #         TestType.COMPATIBILITY: TestPriority.LOW
    #     }
    #
    #     # 根据测试类型确定基础优先级
    #     base_priority = priority_map.get(test_type, TestPriority.MEDIUM)
    #
    #     # 根据内容调整优先级
    #     description = case_data.get('description', '').lower()
    #     if any(keyword in description for keyword in ['error', 'failure', 'invalid', 'security']):
    #         return TestPriority.HIGH
    #
    #     return base_priority

    def _extract_validation_rules(self, text: str) -> List[str]:
        """从文本中提取验证规则"""
        rules = []

        # 常见验证规则模式
        validation_patterns = [
            r'验证\s*(.+?)',
            r'assert\s*(.+?)',
            r'检查\s*(.+?)',
            r'确保\s*(.+?)',
            r'应该\s*(.+?)'
        ]

        for pattern in validation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            rules.extend(matches)

        return rules

    def _enhance_with_context(self, case_data: dict, context: GenerationContext) -> dict:
        """使用上下文信息增强测试用例"""
        # 添加基于端点的标签
        endpoint_tags = self._generate_endpoint_tags(context.endpoint)
        case_data['tags'].update(endpoint_tags)

        # 添加基于测试类型的标签
        case_data['tags'].add(context.test_type.value)
        case_data['tags'].add(context.service_name)

        # 增强描述
        if not case_data['description'] or case_data['description'] == 'None':
            case_data['description'] = self._generate_description(context)

        return case_data

    def _generate_endpoint_tags(self, endpoint: APIEndpoint) -> set:
        """生成端点相关的标签"""
        tags = set()

        # 基于HTTP方法
        tags.add(endpoint.method.lower())

        # 基于路径段
        path_parts = [part for part in endpoint.path.split('/') if part and not part.startswith('{')]
        tags.update(path_parts[:2])  # 添加前两个路径段作为标签

        # 基于操作ID
        if endpoint.operation_id:
            tags.add(endpoint.operation_id)

        return tags

    def _generate_description(self, context: GenerationContext) -> str:
        """生成测试描述"""
        descriptions = {
            TestType.POSITIVE: f"正向测试：验证{context.endpoint.path}的正常功能",
            TestType.NEGATIVE: f"异常测试：验证{context.endpoint.path}的错误处理",
            TestType.BOUNDARY: f"边界测试：验证{context.endpoint.path}的参数边界",
            TestType.SECURITY: f"安全测试：验证{context.endpoint.path}的安全防护",
            TestType.PERFORMANCE: f"性能测试：验证{context.endpoint.path}的性能表现",
            TestType.EDGE_CASE: f"边界情况测试：验证{context.endpoint.path}的特殊场景",
            TestType.COMPATIBILITY: f"兼容性测试：验证{context.endpoint.path}的兼容性"
        }

        return descriptions.get(context.test_type, f"{context.test_type.value} test for {context.endpoint.path}")

    # def _generate_rule_based_cases(self, context: GenerationContext) -> List[TestCase]:
    #     """规则-based测试用例生成回退"""
    #     # 实现基本的规则-based生成
    #     return []

    def _param_to_dict(self, param: APIParameter) -> Dict:
        """参数对象转字典"""
        return {
            'name': param.name,
            'type': param.param_type,
            'position': param.position,
            'required': param.required,
            'constraints': {
                'min': param.min_value,
                'max': param.max_value,
                'min_length': param.min_length,
                'max_length': param.max_length,
                'pattern': param.pattern,
                'enum': param.enum_values,
                'format': param.format
            },
            'example': param.example,
            'description': param.description
        }


    def _get_domain_knowledge(self, service_name: str) -> str:
        """获取领域知识"""
        return self.knowledge_base.get(service_name, "通用微服务API最佳实践")

    def _analyze_coverage_gap(self, context: GenerationContext) -> str:
        """分析覆盖率差距"""
        if not context.existing_cases:
            return "暂无现有测试用例，需要全面覆盖"

        covered_statuses = {case.expected_status for case in context.existing_cases}
        expected_statuses = set(context.endpoint.responses.keys())
        missing_statuses = expected_statuses - covered_statuses

        if missing_statuses:
            return f"缺少对以下状态码的测试: {', '.join(missing_statuses)}"

        return "覆盖率良好，建议关注边界和异常场景"

    def _deduplicate_and_optimize(self, new_cases: List[TestCase], existing_cases: List[TestCase]) -> List[TestCase]:
        """去重和优化测试用例"""
        seen_payloads = set()
        unique_cases = []

        # 合并现有用例的payload
        for case in existing_cases:
            payload_key = json.dumps(case.payload, sort_keys=True)
            seen_payloads.add(payload_key)

        # 过滤新用例
        for case in new_cases:
            payload_key = json.dumps(case.payload, sort_keys=True)
            if payload_key not in seen_payloads:
                seen_payloads.add(payload_key)
                unique_cases.append(case)

        return unique_cases[:self.config.max_test_cases_per_endpoint]

    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载提示词模板"""
        return {
            'positive': """作为资深测试专家，为以下API生成10-15个正向测试用例：

    服务: {service_name}
    端点: {endpoint_method} {service_url}{endpoint_path}
    概述: {endpoint_summary}

    参数规范:
    {parameters}

    请求体规范:
    {request_body}

    响应定义:
    {responses}

    领域背景:
    {domain_knowledge}

    覆盖率分析:
    {coverage_gap}

    请生成覆盖正常业务流程的测试用例，每个包含：
    - 测试名称
    - 详细描述
    - 请求负载（JSON）
    - 预期状态码
    - 响应验证规则
    - 相关标签

    以JSON数组格式返回。""",

                'negative': """作为安全测试专家，为以下API生成异常测试用例：

    服务: {service_name}
    端点: {endpoint_method} {service_url}{endpoint_path}

    参数:
    {parameters}

    请求体:
    {request_body}

    请生成覆盖以下场景的测试用例：
    - 无效参数值
    - 缺失必填参数
    - 类型错误
    - 权限验证
    - 业务逻辑错误

    包含预期错误响应验证。""",

                'security': """作为安全专家，为以下API生成安全测试用例：

    端点: {endpoint_method} {service_url}{endpoint_path}

    参数:
    {parameters}

    请求体:
    {request_body}

    请测试：
    - SQL注入
    - XSS攻击
    - 路径遍历
    - 命令注入
    - 认证绕过
    - 权限提升

    包含攻击payload和预期防护行为。""",

                'default': """为以下API生成全面的{test_type}测试用例：{endpoint_method} {service_url}{endpoint_path}"""
            }

    def _load_knowledge_base(self) -> Dict[str, str]:
        """加载领域知识库"""
        return {
            'user': "用户服务处理认证、授权、个人信息。注意密码安全、会话管理和数据隐私。",
            'order': "订单服务需要保证事务一致性，处理库存锁定、支付集成和状态机流转。",
            'payment': "支付服务涉及金融交易，需要高可用性、幂等性和审计日志。",
            'product': "商品服务管理价格、库存、分类。注意并发更新和缓存策略。",
            'inventory': "库存服务处理实时库存管理，需要分布式锁和乐观锁机制。"
        }