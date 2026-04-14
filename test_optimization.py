import pytest
import asyncio
from config import config_manager, SmartTestConfig, ServiceConfig, TestConfig, DiscoveryConfig, ExecutionConfig
from logger import logger
from error_handler import error_handler, SmartTestError, ServiceDiscoveryError, TestGenerationError, TestExecutionError
from serviceDiscover.service_discovery_engine import ServiceDiscoveryEngine
from testGeneration.test_generation_engine import SmartTestGenerationEngine
from testExecution.smart_execution_engine import SmartTestExecutionEngine
from testExecution.execution_models import TestCase, ExecutionPriority, TestStatus
from smartAssertion.smart_assertion_engine import SmartAssertionEngine
from smartAssertion.assertion_models import AssertionConfig
from service_dependency_manager import dependency_manager
from test_data_manager import test_data_manager
import json
import os

class TestOptimization:
    """测试优化效果"""

    def test_config_manager(self):
        """测试配置管理模块"""
        # 测试配置加载
        assert config_manager is not None
        assert config_manager.config is not None
        
        # 测试服务配置获取
        services = config_manager.get_all_services()
        assert isinstance(services, list)
        
        # 测试测试配置获取
        test_config = config_manager.get_test_config()
        assert test_config is not None
        
        # 测试发现配置获取
        discovery_config = config_manager.get_discovery_config()
        assert discovery_config is not None
        
        # 测试执行配置获取
        execution_config = config_manager.get_execution_config()
        assert execution_config is not None
        
        logger.info("✅ 配置管理模块测试通过")

    def test_logger(self):
        """测试日志系统"""
        # 测试各种级别的日志
        logger.debug("测试调试日志")
        logger.info("测试信息日志")
        logger.warning("测试警告日志")
        logger.error("测试错误日志")
        logger.critical("测试严重日志")
        
        logger.info("✅ 日志系统测试通过")

    def test_error_handler(self):
        """测试错误处理机制"""
        # 测试错误处理
        try:
            raise ValueError("测试错误")
        except Exception as e:
            error_info = error_handler.handle_error(e)
            assert error_info['error_code'] == 'UNKNOWN_ERROR'
        
        # 测试服务发现错误处理
        error_info = error_handler.handle_service_discovery_error("测试服务发现错误")
        assert error_info['error_code'] == 'SERVICE_DISCOVERY_FAILED'
        
        # 测试测试生成错误处理
        error_info = error_handler.handle_test_generation_error("测试测试生成错误")
        assert error_info['error_code'] == 'TEST_GENERATION_FAILED'
        
        # 测试测试执行错误处理
        error_info = error_handler.handle_test_execution_error("测试测试执行错误")
        assert error_info['error_code'] == 'TEST_EXECUTION_FAILED'
        
        logger.info("✅ 错误处理机制测试通过")

    async def test_service_discovery_engine(self):
        """测试服务发现引擎"""
        # 创建服务发现引擎
        discovery_config = config_manager.get_discovery_config()
        discovery_engine = ServiceDiscoveryEngine(discovery_config)
        
        # 测试服务发现引擎初始化
        assert discovery_engine is not None
        assert discovery_engine.config is not None
        
        # 测试缓存机制
        assert hasattr(discovery_engine, 'cache')
        assert hasattr(discovery_engine, 'cache_expiry')
        
        # 测试服务统计信息获取
        stats = discovery_engine.get_service_stats()
        assert isinstance(stats, dict)
        assert 'total_services' in stats
        assert 'healthy_instances' in stats
        assert 'cache_status' in stats
        
        logger.info("✅ 服务发现引擎测试通过")

    async def test_test_generation_engine(self):
        """测试测试生成引擎"""
        # 创建测试生成引擎
        openai_api_key = config_manager.get_openai_api_key()
        generator = SmartTestGenerationEngine(api_key=openai_api_key)
        
        # 测试测试生成引擎初始化
        assert generator is not None
        assert generator.config is not None
        
        # 创建示例OpenAPI规范
        openapi_spec = {
            'info': {
                'title': 'Test Service'
            },
            'paths': {
                '/api/users': {
                    'get': {
                        'summary': '获取用户列表',
                        'responses': {
                            '200': {
                                'description': '成功'
                            }
                        }
                    }
                }
            }
        }
        
        # 测试测试生成
        test_cases = await generator.generate_tests_from_openapi(openapi_spec)
        assert isinstance(test_cases, dict)
        assert 'default-service' in test_cases
        
        # 测试导出功能
        json_output = generator.export_test_cases('json')
        assert isinstance(json_output, str)
        
        python_code = generator.export_test_cases('python')
        assert isinstance(python_code, str)
        
        logger.info("✅ 测试生成引擎测试通过")

    async def test_test_execution_engine(self):
        """测试测试执行引擎"""
        # 创建执行配置
        execution_config = config_manager.get_execution_config()
        executor = SmartTestExecutionEngine(execution_config)
        
        # 测试执行引擎初始化
        assert executor is not None
        assert executor.config is not None
        
        # 创建测试用例
        test_cases = [
            TestCase(
                test_id="test_health_check",
                base_url="http://localhost:8080",
                name="健康检查测试",
                service_name="user-service",
                endpoint="/health",
                method="GET",
                payload={},
                expected_status=200,
                assertions=[],
                priority=ExecutionPriority.HIGH
            )
        ]
        
        # 测试执行引擎状态获取
        status = executor.get_engine_status()
        assert isinstance(status, dict)
        assert 'is_running' in status
        assert 'test_registry_size' in status
        
        logger.info("✅ 测试执行引擎测试通过")

    def test_smart_assertion_engine(self):
        """测试智能断言引擎"""
        # 创建断言配置
        assertion_config = AssertionConfig(
            enable_ai_assertions=False,
            enable_anomaly_detection=False
        )
        
        # 创建智能断言引擎
        assertion_engine = SmartAssertionEngine(assertion_config)
        
        # 测试智能断言引擎初始化
        assert assertion_engine is not None
        assert assertion_engine.config is not None
        
        # 模拟响应数据
        response_data = {
            'status_code': 200,
            'data': {
                'id': 123,
                'name': 'Test User'
            }
        }
        
        # 测试断言生成
        assertions = assertion_engine.generate_assertions('user-service', '/api/users/1', 'GET', response_data)
        assert isinstance(assertions, list)
        
        # 测试响应验证
        results = assertion_engine.validate_response('user-service', '/api/users/1', 'GET', response_data)
        assert isinstance(results, dict)
        assert 'summary' in results
        
        # 测试引擎统计信息获取
        stats = assertion_engine.get_engine_stats()
        assert isinstance(stats, dict)
        assert 'cached_patterns' in stats
        assert 'total_assertions' in stats
        
        logger.info("✅ 智能断言引擎测试通过")

    def test_service_dependency_manager(self):
        """测试服务依赖管理"""
        # 测试服务注册
        dependency_manager.register_service('user-service', ['auth-service'])
        dependency_manager.register_service('auth-service', ['config-service'])
        dependency_manager.register_service('config-service')
        
        # 测试获取服务依赖
        dependencies = dependency_manager.get_service_dependencies('user-service')
        assert 'auth-service' in dependencies
        
        # 测试获取传递依赖
        transitive_dependencies = dependency_manager.get_transitive_dependencies('user-service')
        assert 'auth-service' in transitive_dependencies
        assert 'config-service' in transitive_dependencies
        
        # 测试服务依赖排序
        services = ['user-service', 'auth-service', 'config-service']
        sorted_services = dependency_manager.sort_services_by_dependency(services)
        assert sorted_services == ['config-service', 'auth-service', 'user-service']
        
        # 测试服务健康状态更新
        dependency_manager.update_service_health('auth-service', True)
        dependency_manager.update_service_health('config-service', True)
        
        # 测试依赖健康检查
        health = dependency_manager.check_dependency_health('user-service')
        assert health == True
        
        # 测试依赖统计信息获取
        stats = dependency_manager.get_dependency_stats()
        assert isinstance(stats, dict)
        assert 'total_services' in stats
        assert 'dependency_count' in stats
        
        # 清理依赖关系
        dependency_manager.clear()
        
        logger.info("✅ 服务依赖管理测试通过")

    def test_test_data_manager(self):
        """测试测试数据管理"""
        # 测试测试数据生成
        data_template = {
            'name': 'Test User {unique_id}',
            'email': 'test_{unique_id}@example.com',
            'created_at': '{timestamp}'
        }
        test_data = test_data_manager.generate_test_data('user-service', '/api/users', 'POST', data_template)
        assert isinstance(test_data, dict)
        assert 'name' in test_data
        assert 'email' in test_data
        assert 'created_at' in test_data
        
        # 测试临时数据创建
        temp_data_id = test_data_manager.create_temporary_data(test_data)
        assert temp_data_id != ""
        
        # 测试临时数据获取
        retrieved_data = test_data_manager.get_temporary_data(temp_data_id)
        assert retrieved_data is not None
        assert retrieved_data['name'] == test_data['name']
        
        # 测试临时数据清理
        test_data_manager.cleanup_temporary_data(temp_data_id)
        retrieved_data = test_data_manager.get_temporary_data(temp_data_id)
        assert retrieved_data is None
        
        # 测试数据统计信息获取
        stats = test_data_manager.get_data_stats()
        assert isinstance(stats, dict)
        assert 'test_data_count' in stats
        assert 'temporary_data_count' in stats
        
        # 清理所有临时数据
        test_data_manager.cleanup_all_temporary_data()
        
        logger.info("✅ 测试数据管理测试通过")

    async def test_integration(self):
        """测试集成功能"""
        # 测试配置管理
        assert config_manager is not None
        
        # 测试日志系统
        logger.info("测试集成功能")
        
        # 测试错误处理
        try:
            raise ValueError("测试集成错误")
        except Exception as e:
            error_info = error_handler.handle_error(e)
            assert error_info is not None
        
        # 测试服务依赖管理
        dependency_manager.register_service('test-service')
        
        # 测试测试数据管理
        test_data = test_data_manager.generate_test_data('test-service', '/api/test', 'GET', {})
        assert test_data is not None
        
        # 清理
        dependency_manager.clear()
        test_data_manager.cleanup_all_temporary_data()
        
        logger.info("✅ 集成功能测试通过")

if __name__ == "__main__":
    # 运行同步测试
    test = TestOptimization()
    test.test_config_manager()
    test.test_logger()
    test.test_error_handler()
    test.test_smart_assertion_engine()
    test.test_service_dependency_manager()
    test.test_test_data_manager()
    
    # 运行异步测试
    asyncio.run(test.test_service_discovery_engine())
    asyncio.run(test.test_test_generation_engine())
    asyncio.run(test.test_test_execution_engine())
    asyncio.run(test.test_integration())
    
    logger.info("🎉 所有测试通过！")
