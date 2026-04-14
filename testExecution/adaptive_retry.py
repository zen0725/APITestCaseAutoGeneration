import asyncio
import random
from typing import Dict, Optional, Callable, Any, List
from testExecution.execution_models import TestCase, ExecutionResult, TestStatus
from datetime import datetime, timedelta
import logging

class AdaptiveRetryMechanism:
    def __init__(self, config):
        self.config = config
        self.retry_history = {}
        self.error_patterns = {}
        self.logger = logging.getLogger("AdaptiveRetry")

    async def should_retry(self, test_case: TestCase, result: ExecutionResult) -> bool:
        """判断是否应该重试"""
        # 检查重试次数限制
        if result.retry_count >= self.config.max_retries:
            return False

        # 检查错误类型（某些错误不应该重试）
        if not self._is_retryable_error(result):
            return False

        # 自适应重试决策
        retry_delay = self._calculate_retry_delay(test_case, result)
        retry_probability = self._calculate_retry_probability(test_case, result)

        # 记录重试决策
        self._record_retry_decision(test_case, result, retry_delay, retry_probability)

        # 基于概率决定是否重试
        should_retry = random.random() < retry_probability

        if should_retry:
            self.logger.info(f"测试 {test_case.test_id} 将在 {retry_delay}s 后重试")
            await asyncio.sleep(retry_delay)

        return should_retry

    def _is_retryable_error(self, result: ExecutionResult) -> bool:
        """判断错误是否可重试"""
        error_message = result.error_message or ""

        # 不可重试的错误类型
        non_retryable_errors = [
            "400", "Bad Request", "validation error", "invalid",
            "401", "Unauthorized", "auth", "permission",
            "403", "Forbidden",
            "404", "Not Found",
            "501", "Not Implemented"
        ]

        # 可重试的错误类型
        retryable_errors = [
            "500", "Internal Server Error", "timeout", "time out",
            "502", "Bad Gateway", "503", "Service Unavailable",
            "504", "Gateway Timeout", "connection", "network"
        ]

        # 检查错误消息
        error_lower = error_message.lower()

        # 如果是明确的不可重试错误
        if any(error in error_lower for error in non_retryable_errors):
            return False

        # 如果是明确的可重试错误
        if any(error in error_lower for error in retryable_errors):
            return True

        # 默认情况下，对于服务器错误进行重试
        if result.status == TestStatus.ERROR and "50" in error_message:
            return True

        return False

    def _calculate_retry_delay(self, test_case: TestCase, result: ExecutionResult) -> float:
        """计算重试延迟"""
        base_delay = self.config.retry_delay

        # 基于重试次数的指数退避
        exponential_backoff = base_delay * (2 ** result.retry_count)

        # 基于错误类型的调整
        error_adjustment = self._get_error_type_adjustment(result)

        # 基于服务负载的调整（模拟）
        load_adjustment = self._get_load_adjustment()

        # 随机抖动（避免惊群效应）
        jitter = random.uniform(0.8, 1.2)

        final_delay = exponential_backoff * error_adjustment * load_adjustment * jitter

        # 限制最大延迟
        max_delay = 60.0  # 最大60秒
        return min(final_delay, max_delay)

    def _calculate_retry_probability(self, test_case: TestCase, result: ExecutionResult) -> float:
        """计算重试概率"""
        base_probability = 0.8  # 基础重试概率

        # 基于重试次数的调整
        retry_count_penalty = 0.9 ** result.retry_count

        # 基于错误历史的调整
        history_adjustment = self._get_history_adjustment(test_case.test_id)

        # 基于测试优先级的调整
        priority_boost = test_case.priority.value / 5.0  # 归一化到0-1

        # 基于错误严重性的调整
        severity_adjustment = self._get_error_severity_adjustment(result)

        final_probability = (base_probability * retry_count_penalty *
                             history_adjustment * (1 + priority_boost * 0.2) * severity_adjustment)

        return max(0.1, min(1.0, final_probability))  # 限制在0.1-1.0之间

    def _get_error_type_adjustment(self, result: ExecutionResult) -> float:
        """基于错误类型的延迟调整"""
        error_message = result.error_message or ""

        if any(keyword in error_message.lower() for keyword in ["timeout", "gateway"]):
            return 1.5  # 网络相关错误，增加延迟

        if "database" in error_message.lower():
            return 2.0  # 数据库错误，显著增加延迟

        if "external" in error_message.lower():
            return 1.2  # 外部服务错误，稍微增加延迟

        return 1.0  # 默认调整因子

    def _get_load_adjustment(self) -> float:
        """基于系统负载的调整"""
        # 这里可以集成真实的系统监控数据
        # 模拟实现：基于时间段的负载估计
        current_hour = datetime.now().hour

        if 9 <= current_hour <= 17:  # 工作时间
            return 1.5  # 高负载，增加延迟
        elif 0 <= current_hour <= 6:  # 深夜
            return 0.7  # 低负载，减少延迟
        else:  # 其他时间
            return 1.0  # 正常负载

    def _get_history_adjustment(self, test_id: str) -> float:
        """基于历史成功率的调整"""
        if test_id not in self.retry_history:
            return 1.0  # 无历史数据，使用默认值

        history = self.retry_history[test_id]
        total_attempts = history.get('total_attempts', 0)
        successful_retries = history.get('successful_retries', 0)

        if total_attempts == 0:
            return 1.0

        success_rate = successful_retries / total_attempts

        # 历史成功率越高，重试概率越高
        return 0.5 + success_rate * 0.5  # 映射到0.5-1.0范围

    def _get_error_severity_adjustment(self, result: ExecutionResult) -> float:
        """基于错误严重性的调整"""
        error_message = result.error_message or ""

        if "critical" in error_message.lower() or "fatal" in error_message.lower():
            return 0.3  # 严重错误，降低重试概率

        if "warning" in error_message.lower() or "minor" in error_message.lower():
            return 1.2  # 轻微错误，提高重试概率

        return 1.0  # 一般错误

    def _record_retry_decision(self, test_case: TestCase, result: ExecutionResult,
                               delay: float, probability: float):
        """记录重试决策"""
        test_id = test_case.test_id

        if test_id not in self.retry_history:
            self.retry_history[test_id] = {
                'total_attempts': 0,
                'successful_retries': 0,
                'last_retry': None,
                'retry_pattern': []
            }

        history = self.retry_history[test_id]
        history['total_attempts'] += 1
        history['last_retry'] = datetime.now()
        history['retry_pattern'].append({
            'timestamp': datetime.now(),
            'delay': delay,
            'probability': probability,
            'error': result.error_message
        })

        # 只保留最近20次重试记录
        if len(history['retry_pattern']) > 20:
            history['retry_pattern'] = history['retry_pattern'][-20:]

    def record_retry_success(self, test_id: str):
        """记录重试成功"""
        if test_id in self.retry_history:
            self.retry_history[test_id]['successful_retries'] += 1

    def get_retry_stats(self) -> Dict[str, Any]:
        """获取重试统计信息"""
        total_tests = len(self.retry_history)
        total_retries = sum(history['total_attempts'] for history in self.retry_history.values())
        successful_retries = sum(history['successful_retries'] for history in self.retry_history.values())

        success_rate = successful_retries / total_retries if total_retries > 0 else 0.0

        return {
            'total_tests_with_retries': total_tests,
            'total_retry_attempts': total_retries,
            'successful_retries': successful_retries,
            'retry_success_rate': success_rate,
            'recent_retry_patterns': self._get_recent_retry_patterns()
        }

    def _get_recent_retry_patterns(self) -> List[Dict]:
        """获取最近的重试模式"""
        recent_patterns = []
        for test_id, history in list(self.retry_history.items())[-10:]:  # 最近10个测试
            recent_patterns.append({
                'test_id': test_id,
                'total_attempts': history['total_attempts'],
                'success_rate': history['successful_retries'] / history['total_attempts'] if history[
                                                                                                 'total_attempts'] > 0 else 0,
                'last_retry': history['last_retry']
            })

        return recent_patterns
