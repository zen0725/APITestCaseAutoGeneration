import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Any
from smartAssertion.assertion_models import ResponsePattern, AssertionRule, AssertionType, AssertionLevel, AssertionSource


class AnomalyDetector:
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.detectors: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_vectors: Dict[str, List[List[float]]] = {}

    def extract_features(self, response: Dict) -> List[float]:
        """从响应中提取特征向量"""
        features = []

        # 状态码特征
        status_code = response.get('status_code', 0)
        features.append(status_code)

        # 响应时间特征
        response_time = response.get('response_time', 0)
        features.append(response_time)

        # 响应大小特征
        response_size = len(str(response.get('data', {})))
        features.append(response_size)

        # 数据结构复杂度
        data_complexity = self._calculate_complexity(response.get('data', {}))
        features.append(data_complexity)

        # 字段数量（如果是对象）
        if isinstance(response.get('data'), dict):
            features.append(len(response.get('data', {})))
        else:
            features.append(0)

        # HTTP方法特征（简单编码）
        http_method = response.get('method', 'GET')
        method_encoding = {'GET': 0, 'POST': 1, 'PUT': 2, 'DELETE': 3, 'PATCH': 4}
        features.append(method_encoding.get(http_method, 0))

        return features

    def _calculate_complexity(self, data: Any, depth: int = 0) -> int:
        """计算数据结构复杂度"""
        if depth > 5:  # 防止无限递归
            return 1
        if isinstance(data, dict):
            return sum(self._calculate_complexity(v, depth + 1) for v in data.values()) + len(data)
        elif isinstance(data, list):
            if data:
                return sum(self._calculate_complexity(item, depth + 1) for item in data[:3]) + len(data)
            return 1
        else:
            return 1

    def learn_normal_pattern(self, pattern_key: str, responses: List[Dict]) -> bool:
        """学习正常响应模式"""
        if not responses or len(responses)<10:
            return False

        # 提取特征矩阵
        feature_matrix = [self.extract_features(resp) for resp in responses]

        if len(feature_matrix) < 2:  # 需要至少2个样本
            return False

        # 标准化特征
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_matrix)

        # 训练异常检测模型
        try:
            detector = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100
            )
            detector.fit(scaled_features)

            # 保存模型和标准化器
            self.detectors[pattern_key] = detector
            self.scalers[pattern_key] = scaler
            self.feature_vectors[pattern_key] = feature_matrix
            return True
        except Exception:
            return False

    def detect_anomaly(self, pattern_key: str, response: Dict) -> Optional[AssertionRule]:
        """检测响应异常"""
        if pattern_key not in self.detectors:
            return None

        try:
            # 提取特征并标准化
            features = self.extract_features(response)
            scaled_features = self.scalers[pattern_key].transform([features])

            # 预测是否为异常
            prediction = self.detectors[pattern_key].predict(scaled_features)
            anomaly_score = self.detectors[pattern_key].score_samples(scaled_features)

            # 获取异常阈值
            threshold = self.get_anomaly_threshold(pattern_key)

            # 如果是异常，创建断言
            if prediction[0] == -1 or (threshold and anomaly_score[0] < threshold):  # -1表示异常
                return AssertionRule(
                    rule_id=f"anomaly_detection_{pattern_key}",
                    assertion_type=AssertionType.ANOMALY_DETECTION,
                    description="异常检测：响应模式异常",
                    condition=lambda resp: False,  # 总是失败，因为已经检测到异常
                    level=AssertionLevel.HIGH,
                    error_message=f"检测到响应异常，异常分数: {anomaly_score[0]:.3f}",
                    source=AssertionSource.LEARNED,
                    metadata={
                        'anomaly_score': float(anomaly_score[0]),
                        'threshold': float(threshold) if threshold else None,
                        'features': features
                    }
                )
        except Exception:
            pass

        return None

    def get_anomaly_threshold(self, pattern_key: str) -> Optional[float]:
        """获取异常检测阈值"""
        if pattern_key not in self.detectors:
            return None

        # 计算正常响应的异常分数
        normal_scores = self.detectors[pattern_key].score_samples(
            self.scalers[pattern_key].transform(self.feature_vectors[pattern_key])
        )

        # 使用正常分数的P95作为阈值
        return np.percentile(normal_scores, 95)