import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any
from config import config_manager
from serviceDiscover.service_discovery_engine import ServiceDiscoveryEngine
from testGeneration.test_generation_engine import SmartTestGenerationEngine
from testExecution.smart_execution_engine import SmartTestExecutionEngine
from testExecution.execution_models import TestCase
from logger import logger

class SmartMicroServiceTest:
    def __init__(self):
        self.config = config_manager
        self.discovery_engine = None
        self.test_generator = None
        self.execution_engine = None
        self.test_results = []

    async def run_full_test_suite(self, openapi_file: str = None):
        """运行完整的测试套件"""
        logger.info("🚀 开始微服务智能测试套件执行...")

        # 获取API契约
        api_contracts = {}
        if openapi_file:
            # 从本地文件加载OpenAPI规范
            logger.info(f"📁 从本地文件加载OpenAPI规范: {openapi_file}")
            try:
                import json
                from serviceDiscover.service_models import APIContract
                
                with open(openapi_file, 'r', encoding='utf-8') as f:
                    openapi_spec = json.load(f)
                
                # 从OpenAPI规范中提取服务名称
                service_name = openapi_spec.get('info', {}).get('title', 'default-service')
                
                # 提取API端点列表
                endpoints = []
                paths = openapi_spec.get('paths', {})
                for path, methods in paths.items():
                    for method in methods:
                        endpoints.append(f"{method.upper()} {path}")
                
                # 计算规范哈希
                import hashlib
                spec_str = json.dumps(openapi_spec, sort_keys=True)
                spec_hash = hashlib.md5(spec_str.encode('utf-8')).hexdigest()
                
                # 创建API契约对象
                contract = APIContract(
                    service_name=service_name,
                    openapi_spec=openapi_spec,
                    endpoints=endpoints,
                    last_updated=time.time(),
                    spec_hash=spec_hash,
                    source='openapi'
                )
                
                api_contracts[service_name] = contract
                logger.info(f"成功加载 {len(api_contracts)} 个API契约")
            except Exception as e:
                logger.error(f"加载OpenAPI文件失败: {e}")
                return []
        else:
            # 通过服务发现引擎获取API契约
            logger.info("🔍 初始化服务发现引擎...")
            discovery_config = self.config.get_discovery_config()
            self.discovery_engine = ServiceDiscoveryEngine(discovery_config)

            logger.info("🔄 启动服务发现...")
            await self.discovery_engine.start(discovery_config.registry_url)

            logger.info("📋 获取API契约...")
            api_contracts = self.discovery_engine.get_all_contracts()
            logger.info(f"成功获取 {len(api_contracts)} 个API契约")

        # 4. 初始化测试生成引擎
        logger.info("🎯 初始化测试生成引擎...")
        openai_api_key = self.config.get_openai_api_key()
        self.test_generator = SmartTestGenerationEngine(api_key=openai_api_key)

        # 5. 生成测试用例
        logger.info("📝 生成测试用例...")
        all_test_cases = []
        for service_name, contract in api_contracts.items():
            try:
                # 从契约中提取OpenAPI规范
                openapi_spec = contract.openapi_spec
                
                # 生成测试用例
                test_cases = await self.test_generator.generate_tests_from_openapi(openapi_spec)
                
                # 转换为执行引擎需要的格式
                for service, cases in test_cases.items():
                    for case in cases:
                        # 从OpenAPI规范中提取base_url
                        base_url = f"http://{openapi_spec.get('host', 'localhost')}"
                        base_path = openapi_spec.get('basePath', '')
                        if base_path:
                            base_url = f"{base_url}{base_path}"
                        
                        # 创建执行引擎需要的TestCase对象
                        execution_case = TestCase(
                            test_id=case.test_id,
                            base_url=base_url,
                            name=case.name,
                            service_name=service,
                            endpoint=case.endpoint.path,
                            method=case.endpoint.method,
                            payload=case.payload,
                            expected_status=case.expected_status,
                            assertions=[],  # 可以根据需要添加断言
                            timeout=case.timeout,
                            priority=case.priority,
                            dependencies=[],
                            tags=case.tags
                        )
                        all_test_cases.append(execution_case)
                
                logger.info(f"为 {service_name} 生成 {len(cases)} 个测试用例")
            except Exception as e:
                logger.error(f"为 {service_name} 生成测试用例失败: {e}")

        # 6. 初始化执行引擎
        logger.info("⚡ 初始化测试执行引擎...")
        execution_config = self.config.get_execution_config()
        self.execution_engine = SmartTestExecutionEngine(execution_config)

        # 7. 执行测试
        if all_test_cases:
            logger.info(f"🏃 执行 {len(all_test_cases)} 个测试用例...")
            results = await self.execution_engine.execute_test_suite(all_test_cases)
            self.test_results = results
            
            # 输出执行结果
            logger.info(f"✅ 测试执行完成！")
            logger.info(f"总计: {results['summary']['total_tests']}")
            logger.info(f"通过: {results['summary']['passed']}")
            logger.info(f"失败: {results['summary']['failed']}")
            logger.info(f"错误: {results['summary']['errors']}")
            logger.info(f"成功率: {results['summary']['success_rate']:.2%}")
            
            # 保存结果
            self._save_test_results(results)
        else:
            logger.warning("⚠️  没有生成测试用例，跳过执行")

        # 8. 停止服务发现引擎（如果已初始化）
        if not openapi_file and self.discovery_engine:
            await self.discovery_engine.stop()
        
        # 9. 停止执行引擎
        if self.execution_engine:
            await self.execution_engine.stop_execution()

        logger.info("🎉 测试套件执行完成！")
        return self.test_results

    def _save_test_results(self, results: Dict):
        """保存测试结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/test_report_{timestamp}.json"

        os.makedirs('results', exist_ok=True)
        
        # 递归将对象转换为可序列化的字典
        def convert_to_serializable(obj, visited=None):
            if visited is None:
                visited = set()
            
            # 处理循环引用
            obj_id = id(obj)
            if obj_id in visited:
                return "[Circular Reference]"
            visited.add(obj_id)
            
            import types
            if isinstance(obj, dict):
                result = {k: convert_to_serializable(v, visited) for k, v in obj.items()}
            elif isinstance(obj, list):
                result = [convert_to_serializable(item, visited) for item in obj]
            elif isinstance(obj, types.MappingProxyType):
                result = convert_to_serializable(dict(obj), visited)
            elif hasattr(obj, '__dict__'):
                # 只处理简单对象，避免处理复杂对象导致的递归问题
                result = {}
                for k, v in obj.__dict__.items():
                    # 跳过私有属性和方法
                    if not k.startswith('_'):
                        try:
                            result[k] = convert_to_serializable(v, visited)
                        except (RecursionError, TypeError):
                            result[k] = str(v)
            elif isinstance(obj, datetime):
                result = obj.isoformat()
            else:
                result = obj
            
            visited.remove(obj_id)
            return result
        
        # 转换结果为可序列化的格式
        serializable_results = convert_to_serializable(results)
        
        with open(filename, 'w') as f:
            json.dump(
                {
                    'timestamp': timestamp,
                    'results': serializable_results
                },
                f, indent=2
            )
        logger.info(f"测试结果已保存到: {filename}")

    async def continuous_testing(self, interval: int = 3600):
        """持续测试模式"""
        while True:
            logger.info(f"\n🔄 开始新一轮测试循环 ({datetime.now()})")
            try:
                await self.run_full_test_suite()
            except Exception as e:
                logger.error(f"测试循环执行失败: {e}")
            logger.info(f"⏰ 等待 {interval} 秒后进行下一轮测试...")
            await asyncio.sleep(interval)

async def main():
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="微服务智能测试套件")
    parser.add_argument('--openapi', type=str, help='本地OpenAPI规范文件路径')
    args = parser.parse_args()
    
    # 创建测试套件实例
    test_suite = SmartMicroServiceTest()

    # 运行一次完整测试
    try:
        results = await test_suite.run_full_test_suite(args.openapi)
        logger.info("测试完成！")
    except Exception as e:
        logger.error(f"测试执行失败: {e}")

    # 或者启动持续测试
    # await test_suite.continuous_testing(interval=1800)  # 每30分钟一次

if __name__ == "__main__":
    asyncio.run(main())
