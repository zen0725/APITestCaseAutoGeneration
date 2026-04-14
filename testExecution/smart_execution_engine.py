import asyncio
from typing import Dict, List, Optional, Any
from testExecution.execution_models import TestCase, ExecutionResult, TestStatus, ExecutionConfig, ExecutionPriority
from testExecution.smart_scheduler import IntelligentScheduler
from testExecution.adaptive_retry import AdaptiveRetryMechanism
from testExecution.distributed_executor import DistributedTestExecutor
from testExecution.local_executor import LocalTestExecutor
from logger import logger
from datetime import datetime
import json
import aiohttp


class SmartTestExecutionEngine:
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.scheduler = IntelligentScheduler(config)
        self.retry_mechanism = AdaptiveRetryMechanism(config)
        self.executor = DistributedTestExecutor(config) if config.enable_distributed else LocalTestExecutor(config)

        self.test_registry = {}
        self.execution_stats = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'total_duration': 0.0,
            'average_duration': 0.0
        }

        self.is_running = False
        self.current_batch_id = None
        self.active_tests = 0
        self.semaphore = asyncio.Semaphore(config.max_concurrent_tests)

        # 性能统计
        self.performance_metrics = {
            'request_times': [],
            'response_sizes': [],
            'concurrent_executions': []
        }

    async def execute_test_suite(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """执行测试套件"""
        self.is_running = True
        self.current_batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"开始执行测试套件，共 {len(test_cases)} 个测试用例")

        # 注册测试用例
        for test_case in test_cases:
            self.test_registry[test_case.test_id] = test_case
            await self.scheduler.schedule_test(test_case)

        # 开始执行循环
        results = await self._execution_loop()

        self.is_running = False
        logger.info(f"测试套件执行完成")

        return results

    async def _execution_loop(self) -> Dict[str, Any]:
        """执行主循环"""
        results = {
            'batch_id': self.current_batch_id,
            'start_time': datetime.now(),
            'test_results': {},
            'summary': {},
            'execution_stats': {},
            'performance_metrics': {}
        }

        # 并发执行测试
        tasks = []
        while self.is_running:
            # 获取下一个测试用例
            test_case = await self.scheduler.get_next_test()

            if test_case:
                # 使用信号量控制并发
                task = asyncio.create_task(self._execute_with_semaphore(test_case, results))
                tasks.append(task)
            else:
                # 检查是否所有测试都已完成
                if self._is_execution_complete():
                    self.is_running = False
                else:
                    # 等待新的测试用例或资源释放
                    await asyncio.sleep(0.1)

        # 等待所有任务完成
        if tasks:
            await asyncio.gather(*tasks)

        # 计算最终结果
        results['end_time'] = datetime.now()
        results['summary'] = self._generate_summary(results['test_results'])
        results['execution_stats'] = self.execution_stats
        results['performance_metrics'] = self.performance_metrics

        return results

    async def _execute_with_semaphore(self, test_case: TestCase, results: Dict[str, Any]):
        """使用信号量执行测试"""
        async with self.semaphore:
            try:
                self.active_tests += 1
                self.performance_metrics['concurrent_executions'].append(self.active_tests)
                
                # 执行测试
                result = await self._execute_single_test(test_case)
                results['test_results'][test_case.test_id] = result

                # 处理重试逻辑
                if (result.status in [TestStatus.FAILED, TestStatus.ERROR] and
                        await self.retry_mechanism.should_retry(test_case, result)):

                    # 准备重试
                    retry_case = self._prepare_retry_test(test_case, result)
                    await self.scheduler.schedule_test(retry_case)
                    logger.info(f"测试 {test_case.test_id} 进入重试队列")

                else:
                    # 标记测试完成
                    self.scheduler.complete_test(test_case.test_id, result)

                    # 更新统计信息
                    self._update_execution_stats(result)

                    # 记录重试成功（如果适用）
                    if result.retry_count > 0 and result.status == TestStatus.PASSED:
                        self.retry_mechanism.record_retry_success(test_case.test_id)
            finally:
                self.active_tests -= 1

    async def _execute_single_test(self, test_case: TestCase) -> ExecutionResult:
        """执行单个测试用例"""
        logger.info(f"执行测试: {test_case.test_id}")

        start_time = datetime.now()

        try:
            # 构建完整的请求URL
            base_url = f"http://{test_case.service_name}:8080"
            url = f"{base_url}{test_case.endpoint}"
            logger.debug(f"请求URL: {url}")

            # 执行实际的HTTP请求
            result = await self._execute_http_request(test_case, url)

            # 记录执行时间
            result.duration = (datetime.now() - start_time).total_seconds()
            result.start_time = start_time
            result.end_time = datetime.now()

            # 记录性能指标
            self.performance_metrics['request_times'].append(result.duration)
            if result.response and 'content_length' in result.response:
                self.performance_metrics['response_sizes'].append(result.response['content_length'])

            return result

        except Exception as e:
            logger.error(f"测试执行异常: {e}")
            return ExecutionResult(
                test_id=test_case.test_id,
                status=TestStatus.ERROR,
                duration=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e),
                retry_count=test_case.metadata.get('retry_count', 0)
            )

    async def _execute_http_request(self, test_case: TestCase, url: str) -> ExecutionResult:
        """执行HTTP请求"""
        assertion_results = []
        all_passed = True
        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession() as session:
                # 准备请求参数
                request_kwargs = {
                    'timeout': aiohttp.ClientTimeout(total=test_case.timeout or self.config.default_timeout)
                }

                # 根据HTTP方法发送请求
                if test_case.method.upper() == 'GET':
                    async with session.get(url, **request_kwargs) as response:
                        result = await self._process_response(test_case, response, assertion_results)
                        result.duration = (datetime.now() - start_time).total_seconds()
                        result.start_time = start_time
                        result.end_time = datetime.now()
                        return result
                elif test_case.method.upper() == 'POST':
                    async with session.post(url, json=test_case.payload, **request_kwargs) as response:
                        result = await self._process_response(test_case, response, assertion_results)
                        result.duration = (datetime.now() - start_time).total_seconds()
                        result.start_time = start_time
                        result.end_time = datetime.now()
                        return result
                elif test_case.method.upper() == 'PUT':
                    async with session.put(url, json=test_case.payload, **request_kwargs) as response:
                        result = await self._process_response(test_case, response, assertion_results)
                        result.duration = (datetime.now() - start_time).total_seconds()
                        result.start_time = start_time
                        result.end_time = datetime.now()
                        return result
                elif test_case.method.upper() == 'DELETE':
                    async with session.delete(url, **request_kwargs) as response:
                        result = await self._process_response(test_case, response, assertion_results)
                        result.duration = (datetime.now() - start_time).total_seconds()
                        result.start_time = start_time
                        result.end_time = datetime.now()
                        return result
                else:
                    raise ValueError(f"不支持的HTTP方法: {test_case.method}")

        except Exception as e:
            end_time = datetime.now()
            assertion_results.append({
                'rule_id': 'request_error',
                'passed': False,
                'error_message': str(e)
            })
            return ExecutionResult(
                test_id=test_case.test_id,
                status=TestStatus.ERROR,
                duration=(end_time - start_time).total_seconds(),
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                assertion_results=assertion_results,
                retry_count=test_case.metadata.get('retry_count', 0)
            )

    async def _process_response(self, test_case: TestCase, response: aiohttp.ClientResponse, assertion_results: List) -> ExecutionResult:
        """处理HTTP响应"""
        # 获取响应数据
        try:
            response_data = await response.json()
        except json.JSONDecodeError:
            response_data = await response.text()

        # 构建响应信息
        response_info = {
            'status_code': response.status,
            'headers': dict(response.headers),
            'data': response_data,
            'content_length': response.content_length
        }

        # 执行状态码断言
        status_assertion_passed = response.status == test_case.expected_status
        assertion_results.append({
            'rule_id': 'status_code',
            'passed': status_assertion_passed,
            'error_message': f"预期状态码 {test_case.expected_status}，实际状态码 {response.status}" if not status_assertion_passed else None
        })

        # 执行自定义断言
        all_passed = True
        for i, assertion in enumerate(test_case.assertions):
            try:
                assertion_passed = assertion(response_info)
                assertion_results.append({
                    'rule_id': f'assertion_{i}',
                    'passed': assertion_passed,
                    'error_message': None if assertion_passed else '自定义断言失败'
                })
                if not assertion_passed:
                    all_passed = False
            except Exception as e:
                assertion_results.append({
                    'rule_id': f'assertion_{i}',
                    'passed': False,
                    'error_message': str(e)
                })
                all_passed = False

        # 确定测试状态
        if not status_assertion_passed:
            status = TestStatus.FAILED
        elif not all_passed:
            status = TestStatus.FAILED
        else:
            status = TestStatus.PASSED

        # 创建ExecutionResult对象，只包含必填参数
        result = ExecutionResult(
            test_id=test_case.test_id,
            status=status,
            duration=0.0,  # 将在调用方设置
            start_time=datetime.now(),  # 将在调用方设置
            end_time=datetime.now(),  # 将在调用方设置
            response=response_info,
            assertion_results=assertion_results,
            retry_count=test_case.metadata.get('retry_count', 0)
        )

        return result

    def _prepare_retry_test(self, original_case: TestCase, previous_result: ExecutionResult) -> TestCase:
        """准备重试测试用例"""
        retry_count = previous_result.retry_count + 1

        # 创建重试版本的测试用例
        retry_case = TestCase(
            test_id=original_case.test_id,
            name=original_case.name + f" (Retry {retry_count})",
            service_name=original_case.service_name,
            endpoint=original_case.endpoint,
            method=original_case.method,
            payload=original_case.payload,
            expected_status=original_case.expected_status,
            assertions=original_case.assertions,
            timeout=original_case.timeout,
            priority=original_case.priority,
            dependencies=original_case.dependencies,
            tags=original_case.tags,
            metadata={
                'original_test_id': original_case.test_id,
                'retry_count': retry_count,
                'previous_error': previous_result.error_message
            }
        )

        return retry_case

    def _is_execution_complete(self) -> bool:
        """检查执行是否完成"""
        scheduler_stats = self.scheduler.get_scheduler_stats()
        total_tests = len(self.test_registry)
        completed_tests = len(self.scheduler.completed_tests)

        return completed_tests >= total_tests and not self.scheduler.priority_queue

    def _update_execution_stats(self, result: ExecutionResult):
        """更新执行统计信息"""
        self.execution_stats['total_tests'] += 1
        self.execution_stats['total_duration'] += result.duration

        if result.status == TestStatus.PASSED:
            self.execution_stats['passed_tests'] += 1
        elif result.status == TestStatus.FAILED:
            self.execution_stats['failed_tests'] += 1
        elif result.status == TestStatus.SKIPPED:
            self.execution_stats['skipped_tests'] += 1

        # 计算平均持续时间
        if self.execution_stats['total_tests'] > 0:
            self.execution_stats['average_duration'] = (
                    self.execution_stats['total_duration'] / self.execution_stats['total_tests']
            )

    def _generate_summary(self, test_results: Dict[str, ExecutionResult]) -> Dict[str, Any]:
        """生成执行摘要"""
        total = len(test_results)
        passed = sum(1 for r in test_results.values() if r.status == TestStatus.PASSED)
        failed = sum(1 for r in test_results.values() if r.status == TestStatus.FAILED)
        errors = sum(1 for r in test_results.values() if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in test_results.values() if r.status == TestStatus.SKIPPED)

        durations = [r.duration for r in test_results.values()]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0

        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'success_rate': passed / total if total > 0 else 0,
            'duration_stats': {
                'average': avg_duration,
                'max': max_duration,
                'min': min_duration,
                'total': sum(durations)
            }
        }

    def get_engine_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            'is_running': self.is_running,
            'current_batch': self.current_batch_id,
            'test_registry_size': len(self.test_registry),
            'scheduler_stats': self.scheduler.get_scheduler_stats(),
            'retry_stats': self.retry_mechanism.get_retry_stats(),
            'execution_stats': self.execution_stats
        }

    async def stop_execution(self):
        """停止执行"""
        self.is_running = False
        logger.info("测试执行引擎停止")


# 使用示例
async def main():
    # 创建执行配置
    config = ExecutionConfig(
        max_concurrent_tests=10,
        default_timeout=30,
        max_retries=3,
        adaptive_retry=True,
        enable_distributed=True,
        worker_nodes=['worker1:8080', 'worker2:8080']
    )

    # 创建智能执行引擎
    engine = SmartTestExecutionEngine(config)

    # 创建测试用例
    test_cases = [
        TestCase(
            test_id="test_user_create_1",
            name="用户创建测试",
            service_name="user-service",
            endpoint="/api/v1/users",
            method="POST",
            payload={"name": "test_user", "email": "test@example.com"},
            expected_status=201,
            assertions=[lambda resp: resp.get('status_code') == 201],
            priority=ExecutionPriority.HIGH,
            tags={'critical', 'user'}
        ),
        TestCase(
            test_id="test_user_get_1",
            name="用户查询测试",
            service_name="user-service",
            endpoint="/api/v1/users/1",
            method="GET",
            payload={},
            expected_status=200,
            assertions=[lambda resp: resp.get('status_code') == 200],
            priority=ExecutionPriority.MEDIUM,
            tags={'user'}
        )
    ]

    try:
        # 执行测试套件
        results = await engine.execute_test_suite(test_cases)

        # 输出结果
        print("测试执行完成!")
        print(f"总计: {results['summary']['total_tests']}")
        print(f"通过: {results['summary']['passed']}")
        print(f"失败: {results['summary']['failed']}")
        print(f"成功率: {results['summary']['success_rate']:.2%}")

        # 获取引擎状态
        status = engine.get_engine_status()
        print(f"执行统计: {status['execution_stats']}")

    except Exception as e:
        print(f"测试执行失败: {e}")

    finally:
        await engine.stop_execution()


if __name__ == "__main__":
    asyncio.run(main())