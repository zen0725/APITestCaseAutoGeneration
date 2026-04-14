import openai
from typing import Dict, List, Optional
from smartAssertion.assertion_models import AssertionRule, AssertionType, AssertionLevel, AssertionSource
import json
import re

class AIAssertionEnhancer:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.prompt_templates = self._initialize_prompt_templates()

    def enhance_assertions(self, endpoint: str, method: str, response_data: Dict, existing_assertions: List[AssertionRule]) -> List[AssertionRule]:
        """使用AI增强断言"""
        if not self._should_enhance(endpoint, response_data, existing_assertions):
            return existing_assertions

        try:
            prompt = self._build_enhancement_prompt(endpoint, method, response_data, existing_assertions)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )

            ai_suggestions = response.choices[0].message.content
            return self._parse_ai_suggestions(ai_suggestions, existing_assertions)

        except Exception as e:
            print(f"AI断言增强失败: {e}")
            return existing_assertions

    def _should_enhance(self, endpoint: str, response_data: Dict, assertions: List[AssertionRule]) -> bool:
        """判断是否需要进行AI增强"""
        # 只在有足够数据且断言数量较少时进行增强
        data = response_data.get('data', {})
        return (isinstance(data, dict) and len(data) > 3 and
                len(assertions) < 10 and
                200 <= response_data.get('status_code', 0) < 300)

    def _build_enhancement_prompt(self, endpoint: str, method: str, response_data: Dict, assertions: List[AssertionRule]) -> str:
        """构建AI提示词"""
        existing_assertions_desc = "\n".join([
            f"- {assertion.description} (Level: {assertion.level.value})"
            for assertion in assertions
        ])

        prompt = f"""
    作为资深测试专家，请为以下API响应生成额外的智能业务断言：

    API端点: {method} {endpoint}
    响应数据:
    {json.dumps(response_data, indent=2, ensure_ascii=False)}

    现有断言:
    {existing_assertions_desc}

    请生成3-5个额外的智能断言，重点关注：
    1. 业务逻辑一致性验证
    2. 数据关系完整性检查
    3. 边界条件和异常场景
    4. 安全性和数据验证
    5. 性能相关约束

    以JSON数组格式返回，每个断言包含：
    - rule_id: 唯一规则ID
    - description: 断言描述
    - condition: 断言条件（Python lambda表达式）
    - level: 断言级别（CRITICAL, HIGH, MEDIUM, LOW）
    - error_message: 错误消息

    示例格式：
    ```json
    [
      {{
        "rule_id": "business_email_validation",
        "description": "验证用户状态为active",
        "condition": "lambda resp: resp.get('data', {{}}).get('status') == 'active'",
        "level": "HIGH",
        "error_message": "用户状态不是active"
      }}
    ]"""

        return prompt

    def _parse_ai_suggestions(self, ai_text: str, existing_assertions: List[AssertionRule]) -> List[AssertionRule]:
        """解析AI建议的断言"""
        try:
            # 提取JSON部分
            json_match = re.search(r'```json\n(.*?)\n```', ai_text, re.DOTALL)
            if not json_match:
                return existing_assertions

            suggestions = json.loads(json_match.group(1))
            enhanced_assertions = existing_assertions.copy()

            for suggestion in suggestions:
                try:
                    # 创建新的断言规则
                    new_assertion = AssertionRule(
                        #rule_id=f"ai_enhanced_{hash(suggestion['description'])[:8]}",
                        rule_id=suggestion['rule_id'],
                        assertion_type=AssertionType.BUSINESS_RULE,
                        description=suggestion['description'],
                        condition=eval(suggestion['condition']),
                        level=AssertionLevel[suggestion['level']],
                        error_message=suggestion.get('error_message', 'AI增强断言失败'),
                        source=AssertionSource.AI_GENERATED
                    )
                    enhanced_assertions.append(new_assertion)
                except (KeyError, SyntaxError) as e:
                    print(f"解析AI断言失败: {e}")
                    continue

            return enhanced_assertions
        except (json.JSONDecodeError, KeyError, SyntaxError) as e:
            print(f"解析AI断言建议失败: {e}")
            return existing_assertions

    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """初始化提示词模板"""
        return {
            'default': """
        请为以下{method} {endpoint} API生成智能断言。
        响应数据: {response_data}
        现有断言: {existing_assertions}
        """
        }
