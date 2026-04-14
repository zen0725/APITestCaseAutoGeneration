import numpy as np
from typing import Dict, List, Optional, Any
from smartAssertion.assertion_models import ResponsePattern, AssertionConfig
from datetime import datetime, timedelta
import json
import hashlib
import statistics
from collections import defaultdict


class ResponsePatternLearner:
    def __init__(self, config: AssertionConfig):
        self.config = config
        self.patterns: Dict[str, ResponsePattern] = {}
        self.response_history: Dict[str, List[Dict]] = defaultdict(list)
        self.field_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(list))

    def learn_from_response(self, service_name: str, endpoint: str, method: str, response: Dict) -> Optional[ResponsePattern]:
        """从响应中学习模式并返回更新后的模式"""
        pattern_key = self._get_pattern_key(service_name, endpoint, method)

        if pattern_key not in self.response_history:
            self.response_history[pattern_key] = []

        # 记录响应历史
        self.response_history[pattern_key].append(response)

        # 如果样本不足，返回None
        if len(self.response_history[pattern_key])< self.config.min_learning_samples:
            return None

        # 更新模式
        return self._update_pattern(service_name, endpoint, method)

    def _update_pattern(self, service_name: str, endpoint: str, method: str) -> ResponsePattern:
        """更新响应模式"""
        pattern_key = self._get_pattern_key(service_name, endpoint, method)
        responses = self.response_history[pattern_key]

        # 提取统计信息
        successful_responses = [r for r in responses if 200 <= r.get('status_code', 0) < 300]
        # 状态码分布
        status_codes = {resp.get('status_code', 0) for resp in responses}
        # 响应时间统计
        response_times = [resp.get('response_time', 0) for resp in responses if resp.get('response_time')]

        # 计算响应时间统计
        time_stats = self._calculate_time_stats(response_times)

        # 学习schema模式（如果所有成功响应都有数据）
        schema_pattern = self._learn_schema_pattern(successful_responses)

        # 创建或更新模式
        # pattern = ResponsePattern(
        #     service_name=service_name,
        #     endpoint=endpoint,
        #     normal_status_codes=status_codes,
        #     response_time_stats=time_stats,
        #     schema_pattern=schema_pattern,
        #     learned_at=datetime.now()
        # )

        # 字段分布统计
        field_distributions = self._learn_field_distributions(successful_responses)

        # 计算置信度
        confidence = self._calculate_confidence(len(responses), len(successful_responses))

        pattern = ResponsePattern(
            service_name=service_name,
            endpoint=endpoint,
            method=method,
            normal_status_codes=status_codes,
            response_time_stats=time_stats,
            schema_pattern=schema_pattern,
            field_distributions=field_distributions,
            min_samples=len(responses),
            confidence=confidence,
            learned_at=datetime.now()
        )

        self.patterns[pattern_key] = pattern
        return pattern

    def _calculate_time_stats(self, response_times: List[float]) -> Dict[str, float]:
        """计算响应时间统计"""
        if not response_times:
            return {}

        return {
            'mean': np.mean(response_times),
            'std': np.std(response_times),
            'p50': np.percentile(response_times, 50),
            'p90': np.percentile(response_times, 90),
            'p95': np.percentile(response_times, 95),
            'p99': np.percentile(response_times, 99),
            'min': np.min(response_times),
            'max': np.max(response_times)
        }

    def _learn_schema_pattern(self, responses: List[Dict]) -> Dict:
        """学习响应数据的schema模式"""
        if not responses:
            return {}

        # 提取所有成功响应的数据结构
        schemas = []
        for resp in responses:
            if 'data' in resp and resp['data']:
                schemas.append(self._extract_schema(resp['data']))

        if not schemas:
            return {}

        # 合并schema模式
        merged_schema = self._merge_schemas(schemas)
        return merged_schema

    def _extract_schema(self, data: Any, path: str = "") -> Dict:
        """从数据中提取schema信息"""
        schema = {}
        if isinstance(data, dict):
            schema = {'type': 'object', 'properties': {}}
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                schema['properties'][key] = self._extract_schema(value, new_path)
            #return schema
        elif isinstance(data, list) and data:
            # 使用第一个元素推断数组类型
            #schema = {'type': 'array', 'items': self._extract_schema(data[0], f"{path}[]")}
            schema['type'] = 'array'
            schema['items'] = self._extract_schema(data[0], f"{path}[]")
            # 记录数组长度统计
            self.field_stats[path]['array_lengths'].append(len(data))
        else:
            schema['type'] = type(data).__name__
            # 记录基本类型值的统计
            if isinstance(data, (int, float)):
                self.field_stats[path]['values'].append(data)
            elif isinstance(data, str):
                self.field_stats[path]['string_lengths'].append(len(data))
                self.field_stats[path]['unique_values'].append(data)

        return schema

    def _learn_field_distributions(self, responses: List[Dict]) -> Dict:
        """学习字段值分布"""
        distributions = {}

        for path, stats in self.field_stats.items():
            if 'values' in stats and stats['values']:
                distributions[path] = {
                    'type': 'numeric',
                    'min': min(stats['values']),
                    'max': max(stats['values']),
                    'mean': statistics.mean(stats['values']),
                    'std': statistics.stdev(stats['values']) if len(stats['values']) > 1 else 0
                }
            elif 'string_lengths' in stats and stats['string_lengths']:
                distributions[path] = {
                    'type': 'string',
                    'min_length': min(stats['string_lengths']),
                    'max_length': max(stats['string_lengths']),
                    'avg_length': statistics.mean(stats['string_lengths']),
                    'unique_count': len(set(stats['unique_values']))
                }
            elif 'array_lengths' in stats and stats['array_lengths']:
                distributions[path] = {
                    'type': 'array',
                    'min_length': min(stats['array_lengths']),
                    'max_length': max(stats['array_lengths']),
                    'avg_length': statistics.mean(stats['array_lengths'])
                }

        return distributions

    def _calculate_confidence(self, total_samples: int, successful_samples: int) -> float:
        """计算模式置信度"""
        if total_samples == 0:
            return 0.0

        success_ratio = successful_samples / total_samples
        sample_confidence = min(1.0, total_samples / self.config.min_learning_samples)

        return success_ratio * sample_confidence

    def _merge_schemas(self, schemas: List[Dict]) -> Dict:
        """合并多个schema"""
        if not schemas:
            return {}

        base_schema = schemas[0]
        for schema in schemas[1:]:
            base_schema = self._deep_merge(base_schema, schema)

        return base_schema

    def _deep_merge(self, dict1: Dict, dict2: Dict) -> Dict:
        """深度合并两个字典"""
        if not isinstance(dict1, dict) or not isinstance(dict2, dict):
            return dict1
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _get_pattern_key(self, service_name: str, endpoint: str, method: str) -> str:
        """获取模式存储的键"""
        return f"{service_name}_{method}_{endpoint}".replace('/', '_')

    def get_pattern(self, service_name: str, endpoint: str, method: str) -> Optional[ResponsePattern]:
        """获取学习到的模式"""
        pattern_key = self._get_pattern_key(service_name, endpoint, method)
        return self.patterns.get(pattern_key)

    def get_learning_progress(self, service_name: str, endpoint: str, method: str) -> float:
        """获取学习进度"""
        pattern_key = self._get_pattern_key(service_name, endpoint, method)
        history = self.response_history[pattern_key]
        return min(1.0, len(history) / self.config.min_learning_samples)