from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Callable
from enum import Enum
import json
import re
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AssertionType(Enum):
    STATUS_CODE = "status_code"
    SCHEMA_VALIDATION = "schema_validation"
    DATA_VALIDATION = "data_validation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS_RULE = "business_rule"
    PATTERN_MATCH = "pattern_match"
    ANOMALY_DETECTION = "anomaly_detection"
    CONSISTENCY = "consistency"

class AssertionLevel(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1

class AssertionSource(Enum):
    LEARNED = "learned"
    AI_GENERATED = "ai_generated"
    RULE_BASED = "rule_based"
    MANUAL = "manual"

@dataclass
class AssertionRule:
    rule_id: str
    assertion_type: AssertionType
    description: str
    condition: Callable[[Any], bool]
    level: AssertionLevel = AssertionLevel.MEDIUM
    error_message: Optional[str] = None
    source: AssertionSource = AssertionSource.RULE_BASED
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    success_rate: float = 1.0
    weight: float = 1.0

@dataclass
class ResponsePattern:
    service_name: str
    endpoint: str
    method: str
    normal_status_codes: Set[int] = field(default_factory=set)
    response_time_stats: Dict[str, float] = field(default_factory=dict)  # mean, std, p95, etc.
    schema_pattern: Optional[Dict] = None
    data_patterns: List[Dict] = field(default_factory=list)
    field_distributions: Dict[str, Dict] = field(default_factory=dict)
    anomaly_threshold: float = 0.1
    min_samples: int = 10
    learned_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0

@dataclass
class AssertionConfig:
    enable_ai_assertions: bool = True
    enable_anomaly_detection: bool = True
    min_learning_samples: int = 20
    anomaly_contamination: float = 0.05
    performance_threshold_ms: float = 2000.0
    strict_schema_validation: bool = False
    enable_security_assertions: bool = True
    assertion_ttl_hours: int = 24
    min_confidence_threshold: float = 0.7
    max_assertions_per_endpoint: int = 50