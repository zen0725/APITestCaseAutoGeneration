from typing import Dict, List, Optional, Tuple, Any
from smartAssertion.assertion_models import AssertionRule, AssertionConfig, ResponsePattern, AssertionLevel, AssertionType
from smartAssertion.pattern_learner import ResponsePatternLearner
from smartAssertion.assertion_generator import DynamicAssertionGenerator
from smartAssertion.anomaly_detector import AnomalyDetector
from smartAssertion.ai_assertion_enhancer import AIAssertionEnhancer
from logger import logger
from error_handler import error_handler, TestExecutionError, ErrorCode
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict


class SmartAssertionEngine:
    def __init__(self, config: AssertionConfig, openai_api_key: Optional[str] = None):
        self.config = config
        self.pattern_learner = ResponsePatternLearner(config)
        self.assertion_generator = DynamicAssertionGenerator(config)
        self.anomaly_detector = AnomalyDetector(config.anomaly_contamination)
        self.ai_enhancer = AIAssertionEnhancer(openai_api_key) if openai_api_key and config.enable_ai_assertions else None

        self.assertion_cache: Dict[str, List[AssertionRule]] = {}
        self.assertion_stats: Dict[str, Dict] = {}
        self.execution_history: Dict[str, List[Dict]] = defaultdict(list)

    def generate_assertions(self, service_name: str, endpoint: str, method: str, response_data: Dict) -> List[AssertionRule]:
        """生成智能断言"""
        pattern_key = self._get_pattern_key(service_name, endpoint, method)
        logger.debug(f"为 {service_name} {method} {endpoint} 生成智能断言")

        try:
            # 学习响应模式
            pattern = self.pattern_learner.learn_from_response(service_name, endpoint, method, response_data)
            logger.debug(f"学习到的模式: {pattern}，置信度: {pattern.confidence if pattern else 'N/A'}")

            # 生成基础断言
            if pattern and pattern.confidence >= self.config.min_confidence_threshold:
                assertions = self.assertion_generator.generate_assertions(pattern, response_data)
                logger.debug(f"基于模式生成了 {len(assertions)} 个断言")
            else:
                # 使用通用断言（学习阶段）
                assertions = list(self.assertion_generator.common_assertions.values())
                logger.debug(f"使用通用断言，共 {len(assertions)} 个")

            # 异常检测
            if self.config.enable_anomaly_detection and pattern:
                try:
                    # 学习正常模式（如果有足够数据）
                    if self.pattern_learner.get_learning_progress(service_name, endpoint) >= 1.0:
                        historical_responses = self.pattern_learner.response_history.get(pattern_key, [])
                        if len(historical_responses) >= 10:
                            self.anomaly_detector.learn_normal_pattern(pattern_key, historical_responses)
                            logger.debug(f"学习了 {len(historical_responses)} 个历史响应的正常模式")

                    # 检测当前响应的异常
                    anomaly_assertion = self.anomaly_detector.detect_anomaly(pattern_key, response_data)
                    if anomaly_assertion:
                        assertions.append(anomaly_assertion)
                        logger.debug("添加了异常检测断言")
                except Exception as e:
                    error_info = error_handler.handle_error(e)
                    logger.warning(f"异常检测失败: {e}")

            # AI增强断言
            if self.ai_enhancer and pattern and len(assertions) > 0:
                try:
                    enhanced_assertions = self.ai_enhancer.enhance_assertions(
                        endpoint, method, response_data, assertions
                    )
                    if enhanced_assertions:
                        assertions = enhanced_assertions
                        logger.debug(f"AI增强后，断言数量: {len(assertions)}")
                except Exception as e:
                    error_info = error_handler.handle_error(e)
                    logger.warning(f"AI断言增强失败: {e}")

            # 缓存断言
            self._cache_assertions(pattern_key, assertions)
            logger.debug(f"缓存了 {len(assertions)} 个断言")

            return assertions
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"生成断言失败: {e}")
            # 返回通用断言作为回退
            return list(self.assertion_generator.common_assertions.values())

    def validate_response(self, service_name: str, endpoint: str, method: str, response_data: Dict) -> Dict[str, Any]:
        """验证响应并返回结果"""
        logger.info(f"验证响应: {service_name} {method} {endpoint}")

        try:
            assertions = self.generate_assertions(service_name, endpoint, method, response_data)
            logger.debug(f"开始执行 {len(assertions)} 个断言")

            results = {
                'service_name': service_name,
                'endpoint': endpoint,
                'method': method,
                'timestamp': datetime.now(),
                'assertions_executed': len(assertions),
                'passed': [],
                'failed': [],
                'warnings': [],
                'summary': {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'warning': 0,
                    'success_rate': 0.0
                }
            }

            for assertion in assertions:
                try:
                    # 执行断言
                    start_time = datetime.now()
                    is_pass = assertion.condition(response_data)
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000

                    result = {
                        'rule_id': assertion.rule_id,
                        'description': assertion.description,
                        'level': assertion.level.value,
                        'assertion_type': assertion.assertion_type.value,
                        'source': assertion.source.value,
                        'execution_time_ms': execution_time,
                        'timestamp': datetime.now()
                    }

                    if is_pass:
                        results['passed'].append(result)
                        logger.debug(f"断言通过: {assertion.description}")
                    else:
                        result['error_message'] = assertion.error_message.format(
                            actual_status=response_data.get('status_code', 'unknown')
                        )
                        results['failed'].append(result)
                        logger.warning(f"断言失败: {assertion.description} - {result['error_message']}")

                    # 更新断言统计
                    self._update_assertion_stats(assertion.rule_id, is_pass, execution_time)

                except Exception as e:
                    # 断言执行失败
                    error_info = error_handler.handle_error(e)
                    warning = {
                        'rule_id': assertion.rule_id,
                        'description': assertion.description,
                        'level': AssertionLevel.LOW.value,
                        'error_message': f"断言执行失败: {str(e)}",
                        'assertion_type': assertion.assertion_type.value,
                        'source': assertion.source.value
                    }
                    results['warnings'].append(warning)
                    logger.warning(f"断言执行失败: {assertion.description} - {str(e)}")

            # 计算摘要统计
            total = len(assertions)
            passed = len(results['passed'])
            warning = len(results['warnings'])
            failed = len(results['failed'])

            results['summary'] = {
                'total': total,
                'passed': passed,
                'failed': failed,
                'warning': warning,
                'success_rate': passed / total if total > 0 else 0.0
            }

            # 记录执行历史
            self._record_execution_history(service_name, endpoint, method, results)

            # 记录执行结果
            logger.info(f"断言执行结果: 总计 {total}, 通过 {passed}, 失败 {failed}, 警告 {warning}, 成功率 {results['summary']['success_rate']:.2%}")

            return results
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"验证响应失败: {e}")
            # 返回错误结果
            return {
                'service_name': service_name,
                'endpoint': endpoint,
                'method': method,
                'timestamp': datetime.now(),
                'assertions_executed': 0,
                'passed': [],
                'failed': [],
                'warnings': [{
                    'rule_id': 'validation_error',
                    'description': '响应验证失败',
                    'level': AssertionLevel.HIGH.value,
                    'error_message': str(e),
                    'assertion_type': 'SYSTEM',
                    'source': 'SYSTEM'
                }],
                'summary': {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'warning': 1,
                    'success_rate': 0.0
                }
            }

    def _cache_assertions(self, pattern_key: str, assertions: List[AssertionRule]) -> None:
        """缓存断言规则"""
        # 清理过期缓存
        self._clean_expired_cache()

        # 更新缓存
        self.assertion_cache[pattern_key] = assertions

        # 更新最后使用时间
        for assertion in assertions:
            assertion.last_used = datetime.now()

    def _clean_expired_cache(self) -> None:
        """清理过期缓存"""
        expired_keys = []
        current_time = datetime.now()

        for pattern_key, assertions in self.assertion_cache.items():
            # 检查断言是否过期
            if any((current_time - (assertion.last_used or assertion.created_at)).total_seconds()/3600 >
                   self.config.assertion_ttl_hours for assertion in assertions):
                expired_keys.append(pattern_key)

        for key in expired_keys:
            del self.assertion_cache[key]

    def _update_assertion_stats(self, rule_id: str, is_pass: bool, execution_time: float) -> None:
        """更新断言统计信息"""
        if rule_id not in self.assertion_stats:
            self.assertion_stats[rule_id] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'total_execution_time': 0.0,
                'average_execution_time': 0.0,
                'success_rate': 0.0
            }

        stats = self.assertion_stats[rule_id]
        stats['total_executions'] += 1
        stats['total_execution_time'] += execution_time
        stats['average_execution_time'] = stats['total_execution_time'] / stats['total_executions']

        if is_pass:
            stats['successful_executions'] += 1
        else:
            stats['failed_executions'] += 1

        stats['success_rate'] = stats['successful_executions'] / stats['total_executions']

    def _record_execution_history(self, service_name: str, endpoint: str, method: str,
                                  results: Dict) -> None:
        """记录执行历史"""
        history_key = f"{service_name}_{endpoint}_{method}"

        # 只保留最近100条记录
        if len(self.execution_history[history_key]) >= 100:
            self.execution_history[history_key].pop(0)

        self.execution_history[history_key].append(results)

    def get_engine_stats(self) -> Dict[str, Any]:
        """获取引擎统计信息"""
        total_assertions = sum(len(assertions) for assertions in self.assertion_cache.values())
        total_executions = sum(stats['total_executions'] for stats in self.assertion_stats.values())

        return {
            'cached_patterns': len(self.assertion_cache),
            'total_assertions': total_assertions,
            'total_executions': total_executions,
            'assertion_stats': self.assertion_stats,
            'learning_progress': self._get_overall_learning_progress()
        }

    def _get_overall_learning_progress(self) -> float:
        """获取整体学习进度"""
        total_patterns = len(self.pattern_learner.response_history)
        if total_patterns == 0:
            return 0.0

        # 创建字典键的副本，避免在遍历过程中修改字典
        keys = list(self.pattern_learner.response_history.keys())
        total_progress = sum(
            self.pattern_learner.get_learning_progress(
                *key.split('_')[:3]  # 解析service, endpoint, method
            ) for key in keys
        )

        return total_progress / total_patterns

    def get_assertion_stats(self, service_name: str, endpoint: str, method: str) -> Dict:
        """获取断言统计信息"""
        pattern_key = self._get_pattern_key(service_name, endpoint, method)
        assertions = self.assertion_cache.get(pattern_key, [])

        level_counts = {level.value: 0 for level in AssertionLevel}
        type_counts = {a_type.value: 0 for a_type in AssertionType}

        for assertion in assertions:
            level_counts[assertion.level.value] += 1
            type_counts[assertion.assertion_type.value] += 1

        return {
            'total_assertions': len(assertions),
            'level_distribution': level_counts,
            'type_distribution': type_counts,
            'learning_progress': self.pattern_learner.get_learning_progress(service_name, endpoint)
        }

    def _get_pattern_key(self, service_name: str, endpoint: str, method: str) -> str:
        """获取模式键"""
        return f"{service_name}_{method}_{endpoint}".replace('/', '_')

    def reset_learning(self, service_name: str, endpoint: str, method: str) -> None:
        """重置学习状态"""
        pattern_key = self._get_pattern_key(service_name, endpoint, method)

        # if pattern_key in self.pattern_learner.response_history:
        #     del self.pattern_learner.response_history[pattern_key]
        #
        # if pattern_key in self.pattern_learner.patterns:
        #     del self.pattern_learner.patterns[pattern_key]
        #
        # if pattern_key in self.anomaly_detector.detectors:
        #     del self.anomaly_detector.detectors[pattern_key]
        #
        # if pattern_key in self.assertion_cache:
        #     del self.assertion_cache[pattern_key]
        for storage in [self.pattern_learner.response_history, self.pattern_learner.patterns,
                        self.anomaly_detector.detectors, self.anomaly_detector.scalers,
                        self.assertion_cache]:
            if pattern_key in storage:
                del storage[pattern_key]


# 使用示例
def main():
    # 配置断言引擎
    config = AssertionConfig(
        enable_ai_assertions=True,
        enable_anomaly_detection=True,
        min_learning_samples=10,
        performance_threshold_ms=2000.0,
        min_confidence_threshold=0.8
    )

    # 创建断言引擎
    assertion_engine = SmartAssertionEngine(config, openai_api_key="your-api-key")

    # 模拟响应数据
    response_data = {
        'status_code': 200,
        'response_time': 150,
        'method': 'GET',
        'data': {
            'id': 123,
            'name': 'Test User',
            'email': 'test@example.com',
            'status': 'active',
            'created_at': '2023-12-20T10:30:00Z'
        },
        'raw_response': '{"id": 123, "name": "Test User", "email": "test@example.com", "status": "active"}'
    }

    # 生成并执行断言
    results = assertion_engine.validate_response(
        'user-service',
        '/api/v1/users/123',
        'GET',
        response_data
    )

    print("断言执行结果:")
    print(f"总计: {results['summary']['total']}")
    print(f"通过: {results['summary']['passed']}")
    print(f"失败: {results['summary']['failed']}")
    print(f"警告: {results['summary']['warning']}")
    print(f"成功率: {results['summary']['success_rate']:.2%}")

    # 获取引擎统计
    stats = assertion_engine.get_engine_stats()
    print(f"\n引擎统计:")
    print(f"缓存模式: {stats['cached_patterns']}")
    print(f"总断言数: {stats['total_assertions']}")
    print(f"总执行数: {stats['total_executions']}")

    # 输出失败详情
    for failed in results['failed']:
        print(f"失败断言: {failed['description']}")
        print(f"错误信息: {failed['error_message']}")


if __name__ == "__main__":
    main()