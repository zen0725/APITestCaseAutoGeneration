import yaml
import json
from typing import Dict, List, Any
from dataclasses import dataclass
import os

@dataclass
class ServiceConfig:
    name: str
    base_url: str
    health_check: str
    api_docs_url: str
    dependencies: List[str]

@dataclass
class TestConfig:
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit_delay: float = 0.1
    cache_ttl: int = 300
    max_test_cases_per_endpoint: int = 5

@dataclass
class DiscoveryConfig:
    health_check_timeout: int = 5
    api_docs_timeout: int = 10
    poll_interval: int = 300
    enable_auto_refresh: bool = True
    registry_url: str = "http://localhost:8761/eureka"

@dataclass
class ExecutionConfig:
    max_concurrent_tests: int = 10
    default_timeout: int = 30
    max_retries: int = 3
    adaptive_retry: bool = True
    enable_distributed: bool = False
    worker_nodes: List[str] = None
    resource_limits: Dict[str, float] = None
    
    def __post_init__(self):
        if self.worker_nodes is None:
            self.worker_nodes = []
        if self.resource_limits is None:
            self.resource_limits = {}

@dataclass
class SmartTestConfig:
    services: Dict[str, ServiceConfig]
    test_config: TestConfig
    discovery_config: DiscoveryConfig
    execution_config: ExecutionConfig
    openai_api_key: str = ""
    log_level: str = "INFO"
    log_file: str = "logs/smart-microservice-test.log"

class ConfigManager:
    def __init__(self, config_path: str = "config/microservices.yaml"):
        self.config_path = config_path
        self.config: SmartTestConfig = None
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)

            # 加载服务配置
            services = {}
            for service_data in config_data.get('services', []):
                service = ServiceConfig(
                    name=service_data['name'],
                    base_url=service_data['base_url'],
                    health_check=service_data.get('health_check', '/health'),
                    api_docs_url=service_data.get('api_docs_url', '/v3/api-docs'),
                    dependencies=service_data.get('dependencies', [])
                )
                services[service.name] = service

            # 加载测试配置
            test_config_data = config_data.get('test_config', {})
            test_config = TestConfig(**test_config_data)

            # 加载发现配置
            discovery_config_data = config_data.get('discovery_config', {})
            discovery_config = DiscoveryConfig(**discovery_config_data)

            # 加载执行配置
            execution_config_data = config_data.get('execution_config', {})
            execution_config = ExecutionConfig(**execution_config_data)

            # 创建完整配置
            self.config = SmartTestConfig(
                services=services,
                test_config=test_config,
                discovery_config=discovery_config,
                execution_config=execution_config,
                openai_api_key=config_data.get('openai_api_key', ''),
                log_level=config_data.get('log_level', 'INFO'),
                log_file=config_data.get('log_file', 'logs/smart-microservice-test.log')
            )

        except FileNotFoundError:
            print("配置文件未找到，使用默认配置")
            self._create_default_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            self._create_default_config()

    def _create_default_config(self):
        """创建默认配置示例"""
        default_config = {
            'services': [
                {
                    'name': 'user-service',
                    'base_url': 'http://user-service:8080',
                    'health_check': '/actuator/health',
                    'api_docs_url': '/v3/api-docs',
                    'dependencies': ['auth-service']
                },
                {
                    'name': 'auth-service',
                    'base_url': 'http://auth-service:8080',
                    'health_check': '/actuator/health',
                    'api_docs_url': '/v3/api-docs',
                    'dependencies': []
                }
            ],
            'test_config': {
                'timeout': 30,
                'retry_attempts': 3,
                'rate_limit_delay': 0.1,
                'cache_ttl': 300,
                'max_test_cases_per_endpoint': 5
            },
            'discovery_config': {
                'health_check_timeout': 5,
                'api_docs_timeout': 10,
                'poll_interval': 300,
                'enable_auto_refresh': True,
                'registry_url': 'http://localhost:8761/eureka'
            },
            'execution_config': {
                'max_concurrent_tests': 10,
                'default_timeout': 30,
                'max_retries': 3,
                'adaptive_retry': True,
                'enable_distributed': False,
                'worker_nodes': []
            },
            'openai_api_key': 'your-api-key',
            'log_level': 'INFO',
            'log_file': 'logs/smart-microservice-test.log'
        }

        os.makedirs('config', exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f)

        # 重新加载配置
        self.load_config()

    def get_service_config(self, service_name: str) -> ServiceConfig:
        """获取服务配置"""
        return self.config.services.get(service_name)

    def get_all_services(self) -> List[ServiceConfig]:
        """获取所有服务配置"""
        return list(self.config.services.values())

    def get_test_config(self) -> TestConfig:
        """获取测试配置"""
        return self.config.test_config

    def get_discovery_config(self) -> DiscoveryConfig:
        """获取服务发现配置"""
        return self.config.discovery_config

    def get_execution_config(self) -> ExecutionConfig:
        """获取执行配置"""
        return self.config.execution_config

    def get_openai_api_key(self) -> str:
        """获取OpenAI API密钥"""
        return self.config.openai_api_key

    def get_log_config(self) -> Dict[str, str]:
        """获取日志配置"""
        return {
            'level': self.config.log_level,
            'file': self.config.log_file
        }

    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'services': [
                {
                    'name': s.name,
                    'base_url': s.base_url,
                    'health_check': s.health_check,
                    'api_docs_url': s.api_docs_url,
                    'dependencies': s.dependencies
                }
                for s in self.config.services.values()
            ],
            'test_config': {
                'timeout': self.config.test_config.timeout,
                'retry_attempts': self.config.test_config.retry_attempts,
                'rate_limit_delay': self.config.test_config.rate_limit_delay,
                'cache_ttl': self.config.test_config.cache_ttl,
                'max_test_cases_per_endpoint': self.config.test_config.max_test_cases_per_endpoint
            },
            'discovery_config': {
                'health_check_timeout': self.config.discovery_config.health_check_timeout,
                'api_docs_timeout': self.config.discovery_config.api_docs_timeout,
                'poll_interval': self.config.discovery_config.poll_interval,
                'enable_auto_refresh': self.config.discovery_config.enable_auto_refresh,
                'registry_url': self.config.discovery_config.registry_url
            },
            'execution_config': {
                'max_concurrent_tests': self.config.execution_config.max_concurrent_tests,
                'default_timeout': self.config.execution_config.default_timeout,
                'max_retries': self.config.execution_config.max_retries,
                'adaptive_retry': self.config.execution_config.adaptive_retry,
                'enable_distributed': self.config.execution_config.enable_distributed,
                'worker_nodes': self.config.execution_config.worker_nodes
            },
            'openai_api_key': self.config.openai_api_key,
            'log_level': self.config.log_level,
            'log_file': self.config.log_file
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

# 创建全局配置实例
config_manager = ConfigManager()
