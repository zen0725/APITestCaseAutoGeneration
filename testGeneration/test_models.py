from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Callable
from enum import Enum
import json
from datetime import datetime
import hashlib

class TestType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    PERFORMANCE = "performance"
    SECURITY = "security"
    EDGE_CASE = "edge_case"
    COMPATIBILITY = "compatibility"

class ParameterType(Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

class TestPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1

@dataclass
class APIParameter:
    name: str
    param_type: ParameterType
    position: Optional[str] = None  #header, path, body, query
    required: bool = False
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    enum_values: List[Any] = field(default_factory=list)
    format: Optional[str] = None  # email, uuid, date-time, etc.
    example: Optional[Any] = None
    description: Optional[str] = None

@dataclass
class APIEndpoint:
    path: str
    method: str
    summary: str
    operation_id: Optional[str] = None
    parameters: List[APIParameter] = field(default_factory=list)
    request_body: Optional[Dict] = None
    responses: Dict[str, Dict] = field(default_factory=dict)
    security: List[Dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False

@dataclass
class TestCase:
    test_id: str
    base_url: str
    endpoint: APIEndpoint
    test_type: TestType
    name: str
    description: str
    payload: Dict[str, Any]
    expected_status: int
    expected_schema: Optional[Dict] = None
    validation_rules: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    priority: TestPriority = TestPriority.MEDIUM
    timeout: int = 30
    retry_count: int = 0
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TestGenerationConfig:
    enable_ai: bool = True
    max_test_cases_per_endpoint: int = 15
    include_negative_tests: bool = True
    include_boundary_tests: bool = False
    include_performance_tests: bool = False
    include_security_tests: bool = False
    include_edge_cases: bool = True
    ai_model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    use_knowledge_base: bool = True
    min_coverage_percentage: float = 80.0
    enable_fuzz_testing: bool = False

@dataclass
class GenerationContext:
    service_name: str
    service_url: str
    endpoint: APIEndpoint
    test_type: TestType
    existing_cases: List[TestCase] = field(default_factory=list)
    coverage_metrics: Dict[str, float] = field(default_factory=dict)
    domain_knowledge: Optional[str] = None