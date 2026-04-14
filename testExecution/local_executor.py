import aiohttp
import asyncio
import time
import json
import psutil
from typing import Dict, List, Optional, Any, Callable
from testExecution.execution_models import TestCase, ExecutionResult, TestStatus, ResourceType
from datetime import datetime
import logging
import traceback
from urllib.parse import urljoin
import ssl
import certifi


class LocalTestExecutor:
    def __init__(self, config):
        self.config = config
        self.session = None
        self.ssl_context = None
        self.logger = logging.getLogger("LocalTestExecutor")
        self.request_history = []

        # 初始化SSL上下文
        self._setup_ssl_context()

    def _setup_ssl_context(self):
        """设置SSL上下文"""
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        # 可选：放松SSL验证（用于测试环境）
        if hasattr(self.config, 'relax_ssl_verification') and self.config.relax_ssl_verification:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

    async def execute_local_test(self, test_case: TestCase) -> ExecutionResult:
        """执行单个测试用例"""
        start_time = datetime.now()
        resource_usage = self._start_resource_monitoring()

        try:
            # 确保HTTP会话存在
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=test_case.timeout),
                    connector=aiohttp.TCPConnector(ssl=self.ssl_context)
                )

            # 构建请求
            request_data = self._build_request_data(test_case)

            # 执行HTTP请求
            response = await self._execute_http_request(test_case, request_data)

            # 处理响应
            response_data = await self._process_response(response)

            # 执行断言
            assertion_results = await self._execute_assertions(test_case, response_data)

            # 检查测试结果
            test_passed = self._evaluate_test_result(assertion_results)

            # 收集资源使用情况
            resource_usage = self._stop_resource_monitoring(resource_usage)

            return ExecutionResult(
                test_id=test_case.test_id,
                status=TestStatus.PASSED if test_passed else TestStatus.FAILED,
                duration=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now(),
                response=response_data,
                assertion_results=assertion_results,
                resource_usage=resource_usage,
                metadata={
                    'request_url': request_data['url'],
                    'request_method': request_data['method'],
                    'request_headers': dict(request_data['headers']),
                    'request_body': request_data.get('json'),
                    'response_size': len(response_data.get('raw_body', '')) if response_data else 0
                }
            )

        except asyncio.TimeoutError:
            return self._handle_timeout(test_case, start_time, resource_usage)
        except aiohttp.ClientError as e:
            return self._handle_network_error(test_case, start_time, e, resource_usage)
        except Exception as e:
            return self._handle_unexpected_error(test_case, start_time, e, resource_usage)
        finally:
            # 清理资源监控
            if 'process' in resource_usage:
                resource_usage['process'].terminate()

    def _build_request_data(self, test_case: TestCase) -> Dict[str, Any]:
        """构建请求数据"""
        # 构建完整URL
        #base_url = self._get_service_base_url(test_case.service_name)
        base_url = test_case.base_url
        full_url = urljoin(base_url, test_case.endpoint.lstrip('/'))

        # 准备请求头
        headers = self._prepare_headers(test_case)

        # 准备请求体
        json_data = self._prepare_request_body(test_case)

        return {
            'url': full_url,
            'method': test_case.method.upper(),
            'headers': headers,
            'json': json_data,
            'timeout': test_case.timeout
        }

    # def _get_service_base_url(self, service_name: str) -> str:
    #     """获取服务基础URL"""
    #     # 从配置或服务发现获取服务地址
    #     service_mapping = {
    #         'user-service': 'http://user-service:8080',
    #         'order-service': 'http://order-service:8080',
    #         'product-service': 'http://product-service:8080',
    #         'payment-service': 'http://payment-service:8080',
    #         'auth-service': 'http://auth-service:8080'
    #     }
    #
    #     return service_mapping.get(service_name, f'http://{service_name}:8080')

    def _prepare_headers(self, test_case: TestCase) -> Dict[str, str]:
        """准备请求头"""
        headers = {
            'User-Agent': 'SmartTestEngine/1.0',
            'Accept': 'application/json',
        }

        # 添加内容类型头（对于有请求体的方法）
        if test_case.method.upper() in ['POST', 'PUT', 'PATCH'] and test_case.payload:
            headers['Content-Type'] = 'application/json'

        # 添加认证头（如果测试用例需要）
        if 'auth_token' in test_case.metadata:
            headers['Authorization'] = f'Bearer {test_case.metadata["auth_token"]}'

        # 添加自定义头
        if 'headers' in test_case.metadata:
            headers.update(test_case.metadata['headers'])

        return headers

    def _prepare_request_body(self, test_case: TestCase) -> Optional[Dict]:
        """准备请求体"""
        if not test_case.payload:
            return None

        # 深度复制payload，避免修改原始数据
        import copy
        body = copy.deepcopy(test_case.payload)

        # 处理动态值（如时间戳、随机数等）
        body = self._process_dynamic_values(body)

        return body

    def _process_dynamic_values(self, data: Any) -> Any:
        """处理动态值"""
        if isinstance(data, dict):
            return {k: self._process_dynamic_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._process_dynamic_values(item) for item in data]
        elif isinstance(data, str):
            # 替换动态值标记
            if data == '{{timestamp}}':
                return str(int(time.time()))
            elif data == '{{random_int}}':
                import random
                return random.randint(1000, 9999)
            elif data == '{{uuid}}':
                import uuid
                return str(uuid.uuid4())
            else:
                return data
        else:
            return data

    async def _execute_http_request(self, test_case: TestCase, request_data: Dict) -> aiohttp.ClientResponse:
        """执行HTTP请求"""
        method = request_data['method']
        url = request_data['url']
        headers = request_data['headers']
        json_data = request_data.get('json')

        self.logger.info(f"执行请求: {method} {url}")

        # 记录请求开始时间
        request_start = time.time()

        try:
            if method == 'GET':
                response = await self.session.get(url, headers=headers)
            elif method == 'POST':
                response = await self.session.post(url, json=json_data, headers=headers)
            elif method == 'PUT':
                response = await self.session.put(url, json=json_data, headers=headers)
            elif method == 'DELETE':
                response = await self.session.delete(url, headers=headers)
            elif method == 'PATCH':
                response = await self.session.patch(url, json=json_data, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            # 记录请求耗时
            request_time = time.time() - request_start
            self.logger.debug(f"请求完成: {response.status} (耗时: {request_time:.3f}s)")

            return response

        except Exception as e:
            self.logger.error(f"请求执行失败: {e}")
            raise

    async def _process_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """处理HTTP响应"""
        response_data = {
            'status_code': response.status,
            'headers': dict(response.headers),
            'url': str(response.url),
            'elapsed': response.elapsed.total_seconds() if response.elapsed else 0
        }

        try:
            # 尝试解析响应体
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                response_data['body'] = await response.json()
                response_data['raw_body'] = json.dumps(response_data['body'])
            elif 'text/' in content_type:
                response_data['body'] = await response.text()
                response_data['raw_body'] = response_data['body']
            else:
                # 对于二进制内容，读取为字节
                response_data['body'] = await response.read()
                response_data['raw_body'] = str(response_data['body'])

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.logger.warning(f"响应体解析失败: {e}")
            response_data['body'] = await response.text()
            response_data['raw_body'] = response_data['body']
            response_data['parse_error'] = str(e)

        finally:
            # 确保响应被关闭
            await response.release()

        return response_data

    async def _execute_assertions(self, test_case: TestCase, response_data: Dict) -> List[Dict]:
        """执行断言"""
        assertion_results = []

        for i, assertion_func in enumerate(test_case.assertions):
            assertion_id = f"assertion_{i}"

            try:
                # 准备断言上下文
                assertion_context = {
                    'response': response_data,
                    'test_case': test_case,
                    'assertion_index': i
                }

                # 执行断言
                start_time = time.time()
                assertion_passed = assertion_func(assertion_context)
                execution_time = time.time() - start_time

                assertion_results.append({
                    'assertion_id': assertion_id,
                    'passed': bool(assertion_passed),
                    'execution_time': execution_time,
                    'error_message': None,
                    'expected': getattr(assertion_func, '__doc__', 'No description'),
                    'actual': self._get_assertion_actual_value(assertion_func, response_data)
                })

            except Exception as e:
                self.logger.error(f"断言执行失败: {e}")
                assertion_results.append({
                    'assertion_id': assertion_id,
                    'passed': False,
                    'execution_time': 0,
                    'error_message': f"断言执行异常: {str(e)}",
                    'stack_trace': traceback.format_exc(),
                    'expected': 'N/A',
                    'actual': 'N/A'
                })

        return assertion_results

    def _get_assertion_actual_value(self, assertion_func: Callable, response_data: Dict) -> Any:
        """获取断言的实际值（用于报告）"""
        try:
            # 尝试从断言函数中提取有用的实际值信息
            # 这是一个简化实现，实际中可以更复杂
            if 'status_code' in str(assertion_func.__code__.co_names):
                return response_data.get('status_code')
            elif 'body' in str(assertion_func.__code__.co_names):
                return response_data.get('body')
            else:
                return 'N/A'
        except:
            return 'N/A'

    def _evaluate_test_result(self, assertion_results: List[Dict]) -> bool:
        """评估测试结果"""
        if not assertion_results:
            return False

        # 所有断言都必须通过
        return all(result['passed'] for result in assertion_results)

    def _start_resource_monitoring(self) -> Dict[str, Any]:
        """开始资源监控"""
        process = psutil.Process()

        # 获取初始资源使用情况
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        return {
            'process': process,
            'initial_cpu': initial_cpu,
            'initial_memory': initial_memory,
            'start_time': time.time()
        }

    def _stop_resource_monitoring(self, resource_usage: Dict) -> Dict[str, float]:
        """停止资源监控并计算使用量"""
        process = resource_usage['process']

        # 获取最终资源使用情况
        final_cpu = process.cpu_percent()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        duration = time.time() - resource_usage['start_time']

        return {
            ResourceType.CPU.value: max(0, final_cpu - resource_usage['initial_cpu']),
            ResourceType.MEMORY.value: max(0, final_memory - resource_usage['initial_memory']),
            'duration': duration
        }

    def _handle_timeout(self, test_case: TestCase, start_time: datetime, resource_usage: Dict) -> ExecutionResult:
        """处理超时错误"""
        self.logger.error(f"测试超时: {test_case.test_id}")

        resource_usage = self._stop_resource_monitoring(resource_usage)

        return ExecutionResult(
            test_id=test_case.test_id,
            status=TestStatus.TIMEOUT,
            duration=(datetime.now() - start_time).total_seconds(),
            start_time=start_time,
            end_time=datetime.now(),
            error_message=f"请求超时 ({test_case.timeout}s)",
            resource_usage=resource_usage,
            metadata={'timeout': test_case.timeout}
        )

    def _handle_network_error(self, test_case: TestCase, start_time: datetime,
                              error: Exception, resource_usage: Dict) -> ExecutionResult:
        """处理网络错误"""
        self.logger.error(f"网络错误: {test_case.test_id} - {error}")

        resource_usage = self._stop_resource_monitoring(resource_usage)

        return ExecutionResult(
            test_id=test_case.test_id,
            status=TestStatus.ERROR,
            duration=(datetime.now() - start_time).total_seconds(),
            start_time=start_time,
            end_time=datetime.now(),
            error_message=f"网络错误: {str(error)}",
            resource_usage=resource_usage,
            metadata={'error_type': 'network'}
        )

    def _handle_unexpected_error(self, test_case: TestCase, start_time: datetime,
                                 error: Exception, resource_usage: Dict) -> ExecutionResult:
        """处理意外错误"""
        self.logger.error(f"意外错误: {test_case.test_id} - {error}")

        resource_usage = self._stop_resource_monitoring(resource_usage)

        return ExecutionResult(
            test_id=test_case.test_id,
            status=TestStatus.ERROR,
            duration=(datetime.now() - start_time).total_seconds(),
            start_time=start_time,
            end_time=datetime.now(),
            error_message=f"意外错误: {str(error)}",
            stack_trace=traceback.format_exc(),
            resource_usage=resource_usage,
            metadata={'error_type': 'unexpected'}
        )

    async def close(self):
        """关闭执行器"""
        if self.session:
            await self.session.close()
            self.session = None