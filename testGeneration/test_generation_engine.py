import asyncio
import json
from typing import Dict, List
from testGeneration.contract_parser import OpenAPIContractParser
from testGeneration.strategy_generator import TestStrategyGenerator
from testGeneration.ai_test_generator import AITestGenerator
from testGeneration.boundary_analyzer import BoundaryValueAnalyzer
from testGeneration.rule_based_generator import RuleBasedTestGenerator
from testGeneration.test_models import TestGenerationConfig, GenerationContext, TestType, TestCase, APIEndpoint


class SmartTestGenerationEngine:
    def __init__(self, api_key: str):
        self.config = TestGenerationConfig()
        self.contract_parser = OpenAPIContractParser()
        self.strategy_generator = TestStrategyGenerator()
        self.boundary_analyzer = BoundaryValueAnalyzer()
        self.ai_generator = AITestGenerator(api_key, self.config)
        self.rule_generator = RuleBasedTestGenerator()
        self.generated_test_cases: Dict[str, List[TestCase]] = {}

    async def generate_tests_from_openapi(self, openapi_spec: Dict) -> Dict[str, List[TestCase]]:
        """从OpenAPI规范生成测试用例"""
        # 1. 解析契约
        endpoints_by_service = self.contract_parser.parse_openapi_spec(openapi_spec)

        all_test_cases = {}

        # 2. 为每个服务的每个端点生成测试
        for service_name, endpoints in endpoints_by_service.items():
            service_test_cases = []

            for endpoint in endpoints:
                endpoint_cases = await self._generate_endpoint_tests(service_name, endpoint)
                service_test_cases.extend(endpoint_cases)

            all_test_cases[service_name] = service_test_cases

        self.generated_test_cases = all_test_cases
        return all_test_cases

    async def _generate_endpoint_tests(self, service_name: str, endpoint: APIEndpoint) -> List[TestCase]:
        """为单个端点生成测试用例"""
        test_cases = []

        # 1. 生成测试策略
        test_strategies = self.strategy_generator.generate_test_strategy(endpoint, self.config)
        priority = self.strategy_generator.determine_test_priority(endpoint)

        # 2. 为每种策略生成测试用例
        for test_type in test_strategies:
            context = GenerationContext(
                service_name=service_name,
                service_url=self.contract_parser.parse_host_url(),
                endpoint=endpoint,
                test_type=test_type,
                existing_cases=test_cases
            )

            if test_type == TestType.BOUNDARY:
                # 使用边界值分析器
                boundary_cases = self.boundary_analyzer.generate_boundary_tests(endpoint)
                test_cases.extend(boundary_cases)
            else:
                try:
                    # 使用AI生成器
                    ai_cases = await self.ai_generator.generate_test_cases(context)
                    test_cases.extend(ai_cases)
                except Exception as e:
                    print(f"AI生成失败：{e}")
                    # 回退到规则-based生成
                    rule_cases = self.rule_generator.generate_rule_based_cases(context)
                    test_cases.extend(rule_cases)

        # 3. 去重和限制数量
        test_cases = self._deduplicate_test_cases(test_cases)

        return test_cases[:self.config.max_test_cases_per_endpoint]

    def _deduplicate_test_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """去重测试用例"""
        seen = set()
        unique_cases = []

        for case in test_cases:
            # 基于负载和预期状态的唯一性检查
            case_key = (json.dumps(case.payload, sort_keys=True), case.expected_status)

            if case_key not in seen:
                seen.add(case_key)
                unique_cases.append(case)

        return unique_cases

    def export_test_cases(self, format: str = 'json') -> str:
        """导出测试用例"""
        if format == 'json':
            return json.dumps({
                service: [self._test_case_to_dict(tc) for tc in cases]
                for service, cases in self.generated_test_cases.items()
            }, indent=2)
        elif format == 'python':
            return self._generate_python_code()
        else:
            raise ValueError(f"不支持的格式: {format}")

    def _test_case_to_dict(self, test_case: TestCase) -> Dict:
        """测试用例对象转字典"""
        return {
            'test_id': test_case.test_id,
            'test_type': test_case.test_type.value,
            'name': test_case.name,
            'description': test_case.description,
            'endpoint': f"{test_case.endpoint.method} {test_case.endpoint.path}",
            'payload': test_case.payload,
            'expected_status': test_case.expected_status,
            'priority': test_case.priority.value,
            'validation_rules': test_case.validation_rules,
            'tags': list(test_case.tags)
        }

    def _generate_python_code(self) -> str:
        """生成Python测试代码"""
        code = "import pytest\nimport requests\nimport json\n\n"

        for service_name, cases in self.generated_test_cases.items():
            code += f"# {service_name} 服务测试\n\n"

            for case in cases:
                code += f"""def test_{case.test_id}():
    \"\"\"{case.description}\"\"\"
    url = f"http://{service_name}:8080{case.endpoint.path}"
    payload = {json.dumps(case.payload, indent=4)}

    response = requests.{case.endpoint.method.lower()}(
        url, 
        json=payload,
        timeout={case.timeout},
        headers={{"Content-Type": "application/json"}}
    )

    # 状态码断言
    assert response.status_code == {case.expected_status}, \
        f"预期状态码 {case.expected_status}，实际状态码 {{response.status_code}}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        {self._generate_validation_code(case)}

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"

"""
        return code

    def _generate_validation_code(self, case: TestCase) -> str:
        """生成验证代码"""
        if not case.validation_rules:
            return "# 添加更多的响应验证逻辑"

        validation_code = []
        for rule in case.validation_rules:
            if "required" in rule:
                field = rule.replace("required", "").strip()
                validation_code.append(f"assert '{field}' in response_data, '缺少必填字段 {field}'")

        return "\n        ".join(validation_code) if validation_code else "# 添加更多的响应验证逻辑"


# 使用示例
async def main():
    # 初始化引擎
    engine = SmartTestGenerationEngine(api_key="your-openai-api-key")

    # 加载OpenAPI规范
    with open('/Users/huangzhen/Documents/api-docs.json', 'r') as f:
        openapi_spec = json.load(f)

    # 生成测试用例
    test_cases = await engine.generate_tests_from_openapi(openapi_spec)

    # 导出结果
    json_output = engine.export_test_cases('json')
    with open('generated_tests.json', 'w') as f:
        f.write(json_output)

    python_code = engine.export_test_cases('python')
    with open('test_generated.py', 'w') as f:
        f.write(python_code)

    print(f"✅ 生成完成！共生成 {sum(len(cases) for cases in test_cases.values())} 个测试用例")


if __name__ == "__main__":
    asyncio.run(main())