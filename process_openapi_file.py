import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any
from config import config_manager
from testGeneration.test_generation_engine import SmartTestGenerationEngine
from testGeneration.test_models import TestCase as GenerationTestCase
from testExecution.execution_models import TestCase as ExecutionTestCase, ExecutionPriority
from logger import logger

async def process_openapi_file(file_path: str):
    """处理本地OpenAPI JSON文件并生成测试用例"""
    logger.info(f"开始处理OpenAPI文件: {file_path}")
    
    try:
        # 1. 读取OpenAPI文件
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            openapi_spec = json.load(f)
        
        logger.info("成功加载OpenAPI规范")
        
        # 2. 初始化测试生成引擎
        openai_api_key = config_manager.get_openai_api_key()
        test_generator = SmartTestGenerationEngine(api_key=openai_api_key)
        
        # 3. 生成测试用例
        logger.info("生成测试用例...")
        test_cases = await test_generator.generate_tests_from_openapi(openapi_spec)
        
        # 4. 转换为执行引擎需要的格式
        execution_cases = []
        for service_name, cases in test_cases.items():
            logger.info(f"为服务 {service_name} 生成了 {len(cases)} 个测试用例")
            
            for case in cases:
                # 转换GenerationTestCase到ExecutionTestCase
                execution_case = ExecutionTestCase(
                    test_id=case.test_id,
                    base_url=get_service_base_url(service_name),  # 需要根据实际情况修改
                    name=case.name,
                    service_name=service_name,
                    endpoint=case.endpoint.path,
                    method=case.endpoint.method,
                    payload=case.payload,
                    expected_status=case.expected_status,
                    assertions=[],  # 可以根据需要添加断言
                    timeout=getattr(case, 'timeout', 30),
                    priority=case.priority if hasattr(case, 'priority') else ExecutionPriority.MEDIUM,
                    dependencies=[],
                    tags=case.tags
                )
                execution_cases.append(execution_case)
        
        # 5. 导出测试用例
        export_test_cases(test_cases)
        
        logger.info(f"🎉 处理完成！总共生成了 {len(execution_cases)} 个测试用例")
        return execution_cases
        
    except Exception as e:
        logger.error(f"处理OpenAPI文件失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def get_service_base_url(service_name: str) -> str:
    """获取服务基础URL"""
    # 这里可以根据实际情况配置服务的基础URL
    # 例如从配置文件中读取或使用默认值
    service_urls = {
        'user-service': 'http://localhost:8080',
        'order-service': 'http://localhost:8081',
        'product-service': 'http://localhost:8082',
        'payment-service': 'http://localhost:8083',
        'auth-service': 'http://localhost:8084'
    }
    
    return service_urls.get(service_name, f'http://localhost:8080')

def export_test_cases(test_cases: Dict[str, Any]):
    """导出测试用例到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 导出为JSON
    json_filename = f"generated_tests/generated_test_cases_{timestamp}.json"
    os.makedirs('generated_tests', exist_ok=True)
    
    # 转换为可序列化的格式
    serializable_cases = {}
    for service, cases in test_cases.items():
        serializable_cases[service] = []
        for case in cases:
            case_dict = {
                'test_id': case.test_id,
                'name': case.name,
                'endpoint': f"{case.endpoint.method} {case.endpoint.path}",
                'payload': case.payload,
                'expected_status': case.expected_status,
                'timeout': getattr(case, 'timeout', 30),
                'priority': case.priority.value if hasattr(case, 'priority') else 'MEDIUM',
                'tags': list(case.tags)
            }
            serializable_cases[service].append(case_dict)
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(serializable_cases, f, indent=2, ensure_ascii=False)
    
    logger.info(f"测试用例已导出到: {json_filename}")
    
    # 导出为Python测试代码
    python_filename = f"generated_tests/test_generated_{timestamp}.py"
    with open(python_filename, 'w', encoding='utf-8') as f:
        f.write("import pytest\nimport requests\nimport json\n\n")
        
        for service, cases in test_cases.items():
            f.write(f"# {service} 服务测试\n\n")
            
            for case in cases:
                f.write(f"def test_{case.test_id}():\n")
                f.write(f"    \"\"\"{case.name}\"\"\"\n")
                f.write(f"    url = f\"{get_service_base_url(service)}{case.endpoint.path}\"\n")
                f.write(f"    payload = {json.dumps(case.payload, indent=4)}\n\n")
                f.write(f"    response = requests.{case.endpoint.method.lower()}(\n")
                f.write(f"        url, \n")
                f.write(f"        json=payload,\n")
                f.write(f"        timeout={getattr(case, 'timeout', 30)},\n")
                f.write(f"        headers={{\"Content-Type\": \"application/json\"}}\n")
                f.write(f"    )\n\n")
                f.write(f"    # 状态码断言\n")
                f.write(f"    assert response.status_code == {case.expected_status}, \\\n")
                f.write(f"        f\"预期状态码 {case.expected_status}，实际状态码 {{response.status_code}}\"\n\n")
                f.write(f"    # 响应体验证\n")
                f.write(f"    if response.status_code == 200:\n")
                f.write(f"        response_data = response.json()\n")
                f.write(f"        # 添加更多的响应验证逻辑\n\n")
                f.write(f"    # 性能断言（可选）\n")
                f.write(f"    assert response.elapsed.total_seconds() < 2.0, \"响应时间超过2秒\"\n\n\n")
    
    logger.info(f"Python测试代码已导出到: {python_filename}")

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="处理OpenAPI JSON文件并生成测试用例")
    parser.add_argument('file_path', type=str, help='OpenAPI JSON文件路径')
    args = parser.parse_args()
    
    await process_openapi_file(args.file_path)

if __name__ == "__main__":
    asyncio.run(main())
