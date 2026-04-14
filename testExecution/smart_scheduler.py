import asyncio
import heapq
from typing import Dict, List, Optional, Set, Any
from testExecution.execution_models import TestCase, ExecutionResult, TestStatus, ExecutionPriority, ResourceType
import time
from datetime import datetime
import logging

class IntelligentScheduler:
    def __init__(self, config):
        self.config = config
        self.priority_queue = []
        self.running_tests = set()
        self.completed_tests = {}
        self.failed_tests = {}
        self.resource_usage = {}
        self.test_dependencies = {}
        self.execution_history = {}
        self.logger = logging.getLogger("IntelligentScheduler")

        # 初始化资源使用
        for resource in ResourceType:
            self.resource_usage[resource] = 0.0

    async def schedule_test(self, test_case: TestCase) -> str:
        """智能调度测试用例"""
        # 检查依赖关系
        if not await self._check_dependencies(test_case):
            self.logger.warning(f"测试 {test_case.test_id} 依赖未满足，进入等待")
            return "waiting"

        # 检查资源限制
        if not self._check_resource_limits(test_case):
            self.logger.warning(f"测试 {test_case.test_id} 资源限制，进入等待")
            return "waiting"

        # 计算优先级分数
        priority_score = self._calculate_priority_score(test_case)

        # 添加到优先队列
        heapq.heappush(self.priority_queue, (-priority_score, time.time(), test_case.test_id, test_case))
        self.logger.info(f"测试 {test_case.test_id} 已调度，优先级: {priority_score}")

        return "scheduled"

    async def get_next_test(self) -> Optional[TestCase]:
        """获取下一个要执行的测试用例"""
        if not self.priority_queue:
            return None

        # 检查并发限制
        if len(self.running_tests) >= self.config.max_concurrent_tests:
            return None

        while self.priority_queue:
            # 获取优先级最高的测试
            _, _, test_id, test_case = heapq.heappop(self.priority_queue)

            # 检查测试是否已经完成或正在运行
            if test_id in self.completed_tests or test_id in self.running_tests:
                continue

            # 再次检查依赖关系（可能在此期间发生变化）
            if not await self._check_dependencies(test_case):
                # 重新加入队列，降低优先级
                new_priority = self._calculate_priority_score(test_case) * 0.8
                heapq.heappush(self.priority_queue, (-new_priority, time.time(), test_id, test_case))
                continue

            # 检查资源可用性
            if not self._check_resource_availability(test_case):
                # 重新加入队列，稍后重试
                heapq.heappush(self.priority_queue,
                               (-self._calculate_priority_score(test_case), time.time() + 1, test_id, test_case))
                continue

            # 预留资源
            self._reserve_resources(test_case)
            self.running_tests.add(test_id)

            return test_case

        return None

    def complete_test(self, test_id: str, result: ExecutionResult):
        """标记测试完成"""
        self.running_tests.discard(test_id)
        self.completed_tests[test_id] = result

        # 释放资源
        self._release_resources(result)

        # 记录执行历史
        self.execution_history[test_id] = {
            'completion_time': datetime.now(),
            'status': result.status,
            'duration': result.duration
        }

        if result.status == TestStatus.FAILED:
            self.failed_tests[test_id] = self.failed_tests.get(test_id, 0) + 1

        self.logger.info(f"测试 {test_id} 完成，状态: {result.status}")

    async def _check_dependencies(self, test_case: TestCase) -> bool:
        """检查测试依赖关系"""
        for dep_id in test_case.dependencies:
            if dep_id not in self.completed_tests:
                return False

            dep_result = self.completed_tests[dep_id]
            if dep_result.status != TestStatus.PASSED:
                self.logger.warning(f"测试 {test_case.test_id} 的依赖 {dep_id} 失败")
                return False

        return True

    def _check_resource_limits(self, test_case: TestCase) -> bool:
        """检查资源限制"""
        # 估算测试资源需求
        estimated_resources = self._estimate_resource_requirements(test_case)

        for resource_type, required in estimated_resources.items():
            current_usage = self.resource_usage.get(resource_type, 0)
            limit = self.config.resource_limits.get(resource_type, float('inf'))

            if current_usage + required > limit:
                self.logger.debug(f"资源 {resource_type} 不足: {current_usage + required} > {limit}")
                return False

        return True

    def _check_resource_availability(self, test_case: TestCase) -> bool:
        """检查资源可用性"""
        # 实时资源检查（更严格的检查）
        return self._check_resource_limits(test_case)

    def _reserve_resources(self, test_case: TestCase):
        """预留资源"""
        estimated_resources = self._estimate_resource_requirements(test_case)

        for resource_type, required in estimated_resources.items():
            self.resource_usage[resource_type] = self.resource_usage.get(resource_type, 0) + required

    def _release_resources(self, result: ExecutionResult):
        """释放资源"""
        for resource_type, used in result.resource_usage.items():
            if resource_type in self.resource_usage:
                self.resource_usage[resource_type] = max(0, self.resource_usage[resource_type] - used)

    def _calculate_priority_score(self, test_case: TestCase) -> float:
        """计算优先级分数"""
        base_score = test_case.priority.value

        # 失败次数调整（失败次数越多，优先级越高）
        failure_count = self.failed_tests.get(test_case.test_id, 0)
        failure_boost = min(failure_count * 0.5, 2.0)  # 最大提升2分

        # 依赖关系调整（依赖少的测试优先）
        dependency_penalty = len(test_case.dependencies) * 0.2

        # 执行历史调整（长时间运行的测试优先）
        history_boost = 0
        if test_case.test_id in self.execution_history:
            last_duration = self.execution_history[test_case.test_id].get('duration', 0)
            history_boost = min(last_duration / 10, 1.0)  # 基于历史执行时间

        # 业务重要性调整（基于标签）
        business_boost = 0
        if 'critical' in test_case.tags:
            business_boost = 2.0
        elif 'high_priority' in test_case.tags:
            business_boost = 1.0

        final_score = base_score + failure_boost - dependency_penalty + history_boost + business_boost
        return max(1.0, final_score)

    def _estimate_resource_requirements(self, test_case: TestCase) -> Dict[ResourceType, float]:
        """估算资源需求"""
        resources = {}

        # 基础资源估算
        resources[ResourceType.CPU] = 0.1  # 0.1个CPU核心
        resources[ResourceType.MEMORY] = 50.0  # 50MB内存

        # 基于测试特征的资源估算
        if 'performance' in test_case.tags:
            resources[ResourceType.CPU] += 0.2
            resources[ResourceType.MEMORY] += 100.0

        if 'integration' in test_case.tags:
            resources[ResourceType.NETWORK] = 1.0
            resources[ResourceType.EXTERNAL_API] = 1.0

        if 'database' in test_case.tags:
            resources[ResourceType.DATABASE] = 1.0

        return resources

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        return {
            'queue_size': len(self.priority_queue),
            'running_tests': len(self.running_tests),
            'completed_tests': len(self.completed_tests),
            'failed_tests': len(self.failed_tests),
            'resource_usage': self.resource_usage,
            'average_priority': self._calculate_average_priority()
        }

    def _calculate_average_priority(self) -> float:
        """计算平均优先级"""
        if not self.priority_queue:
            return 0.0

        total_priority = sum(-score for score, _, _, _ in self.priority_queue)
        return total_priority / len(self.priority_queue)