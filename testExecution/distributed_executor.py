import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from testExecution.execution_models import TestCase, ExecutionResult, TestStatus, ResourceType
import time
from datetime import datetime
import logging
import json

class DistributedTestExecutor:
    def __init__(self, config):
        self.config = config
        self.worker_nodes = config.worker_nodes
        self.worker_status = {}
        self.session = None
        self.logger = logging.getLogger("DistributedExecutor")

        # 初始化工作节点状态
        for node in self.worker_nodes:
            self.worker_status[node] = {
                'status': 'unknown',
                'last_heartbeat': None,
                'current_load': 0,
                'max_capacity': 10,
                'active_tests': set()
            }

    async def execute_node_test(self, test_case: TestCase) -> ExecutionResult:
        """分布式执行测试用例"""
        start_time = datetime.now()

        try:
            # 选择最优工作节点
            best_node = await self._select_best_worker(test_case)

            if not best_node:
                # 如果没有可用节点，本地执行
                #return await self._execute_locally(test_case)
                raise Exception(f"没有分配到工作节点")

            # 分布式执行
            result = await self._execute_on_worker(best_node, test_case)
            result.duration = (datetime.now() - start_time).total_seconds()

            # 更新工作节点状态
            self._update_worker_status(best_node, test_case.test_id, 'completed')

            return result
        except Exception as e:
            self.logger.error(f"分布式测试执行失败: {e}")
            return ExecutionResult(
                test_id=test_case.test_id,
                status=TestStatus.ERROR,
                duration=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e)
            )

    async def _select_best_worker(self, test_case: TestCase) -> Optional[str]:
        """选择最优工作节点"""
        available_nodes = []

        for node, status in self.worker_status.items():
            # 检查节点健康状态
            if not await self._is_worker_healthy(node):
                continue

            # 检查节点负载
            if status['current_load'] >= status['max_capacity']:
                continue

            # 计算节点得分
            score = self._calculate_worker_score(node, status, test_case)
            available_nodes.append((score, node))

        if not available_nodes:
            return None

        # 选择得分最高的节点
        available_nodes.sort(reverse=True)
        return available_nodes[0][1]

    async def _is_worker_healthy(self, node: str) -> bool:
        """检查工作节点健康状态"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(f"http://{node}/health", timeout=5) as response:
                if response.status == 200:
                    health_data = await response.json()
                    self.worker_status[node]['status'] = health_data.get('status', 'healthy')
                    self.worker_status[node]['last_heartbeat'] = datetime.now()
                    return health_data.get('status') == 'healthy'

        except (aiohttp.ClientError, asyncio.TimeoutError):
            self.worker_status[node]['status'] = 'unhealthy'
            self.logger.warning(f"工作节点 {node} 健康检查失败")

        return False

    def _calculate_worker_score(self, node: str, status: Dict, test_case: TestCase) -> float:
        """计算工作节点得分"""
        base_score = 100.0

        # 负载得分（负载越低得分越高）
        load_ratio = status['current_load'] / status['max_capacity']
        load_score = (1 - load_ratio) * 40  # 最多40分

        # 网络延迟得分（模拟）
        latency_score = 30  # 基础延迟分

        # 资源匹配得分
        resource_score = self._calculate_resource_match_score(node, test_case)

        # 历史成功率得分
        success_score = self._calculate_success_score(node)

        total_score = base_score + load_score + latency_score + resource_score + success_score
        return total_score

    def _calculate_resource_match_score(self, node: str, test_case: TestCase) -> float:
        """计算资源匹配得分"""
        # 基于测试需求和工作节点特性的匹配度
        score = 0

        if 'performance' in test_case.tags and 'high_cpu' in self.worker_status[node].get('capabilities', []):
            score += 20

        if 'memory_intensive' in test_case.tags and 'high_memory' in self.worker_status[node].get('capabilities', []):
            score += 20

        if 'network' in test_case.tags and 'low_latency' in self.worker_status[node].get('capabilities', []):
            score += 15

        return score

    def _calculate_success_score(self, node: str) -> float:
        """计算历史成功率得分"""
        # 模拟实现 - 实际中应该基于历史数据
        base_success_rate = 0.95  # 95%基础成功率
        return base_success_rate * 25  # 最多25分

    async def _execute_on_worker(self, worker_node: str, test_case: TestCase) -> ExecutionResult:
        """在工作节点上执行测试"""
        self._update_worker_status(worker_node, test_case.test_id, 'started')

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # 准备测试数据
            test_data = {
                'test_id': test_case.test_id,
                'base_url' : test_case.base_url,
                'service_name': test_case.service_name,
                'endpoint': test_case.endpoint,
                'method': test_case.method,
                'payload': test_case.payload,
                'timeout': test_case.timeout
            }

            # 发送测试请求到工作节点
            async with self.session.post(
                    f"http://{worker_node}/execute-test",
                    json=test_data,
                    timeout=test_case.timeout + 5
            ) as response:

                if response.status == 200:
                    result_data = await response.json()
                    return self._parse_worker_result(result_data, test_case)
                else:
                    raise Exception(f"工作节点返回错误状态码: {response.status}")

        except Exception as e:
            self._update_worker_status(worker_node, test_case.test_id, 'failed')
            raise e

    def _parse_worker_result(self, result_data: Dict, test_case: TestCase) -> ExecutionResult:
        """解析工作节点返回的结果"""
        status_map = {
            'passed': TestStatus.PASSED,
            'failed': TestStatus.FAILED,
            'error': TestStatus.ERROR,
            'timeout': TestStatus.TIMEOUT
        }

        return ExecutionResult(
            test_id=test_case.test_id,
            status=status_map.get(result_data.get('status', 'error'), TestStatus.ERROR),
            duration=result_data.get('duration', 0),
            start_time=datetime.fromisoformat(result_data.get('start_time', datetime.now().isoformat())),
            end_time=datetime.fromisoformat(result_data.get('end_time', datetime.now().isoformat())),
            response=result_data.get('response'),
            assertion_results=result_data.get('assertion_results', []),
            error_message=result_data.get('error_message'),
            resource_usage=result_data.get('resource_usage', {})
        )

    async def _execute_locally(self, test_case: TestCase) -> ExecutionResult:
        """本地执行测试用例"""
        self.logger.info(f"本地执行测试: {test_case.test_id}")

        start_time = datetime.now()

        try:
            # 模拟测试执行
            await asyncio.sleep(0.1)  # 模拟网络请求

            # 这里应该是实际的测试执行逻辑
            # 例如：发送HTTP请求，验证响应等

            result = ExecutionResult(
                test_id=test_case.test_id,
                status=TestStatus.PASSED,  # 模拟成功
                duration=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now(),
                response={'status': 'simulated_response'},
                assertion_results=[{'rule_id': 'test_rule', 'passed': True}]
            )

            return result

        except Exception as e:
            return ExecutionResult(
                test_id=test_case.test_id,
                status=TestStatus.ERROR,
                duration=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e)
            )

    def _update_worker_status(self, worker_node: str, test_id: str, action: str):
        """更新工作节点状态"""
        if action == 'started':
            self.worker_status[worker_node]['active_tests'].add(test_id)
            self.worker_status[worker_node]['current_load'] = len(self.worker_status[worker_node]['active_tests'])
        elif action in ['completed', 'failed']:
            self.worker_status[worker_node]['active_tests'].discard(test_id)
            self.worker_status[worker_node]['current_load'] = len(self.worker_status[worker_node]['active_tests'])

    async def close(self):
        """关闭执行器"""
        if self.session:
            await self.session.close()