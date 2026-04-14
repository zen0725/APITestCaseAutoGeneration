from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Callable, Tuple
from enum import Enum
import asyncio
import time
from datetime import datetime, timedelta
import hashlib
import json

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"
    RETRYING = "retrying"

class ExecutionPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_API = "external_api"

@dataclass
class TestCase:
    test_id: str
    base_url: str
    name: str
    service_name: str
    endpoint: str
    method: str
    payload: Dict[str, Any]
    expected_status: int
    assertions: List[Callable]
    timeout: int = 30
    priority: ExecutionPriority = ExecutionPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionResult:
    test_id: str
    status: TestStatus
    duration: float
    start_time: datetime
    end_time: datetime
    response: Optional[Dict] = None
    assertion_results: List[Dict] = field(default_factory=list)
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    retry_count: int = 0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionConfig:
    max_concurrent_tests: int = 50
    default_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    adaptive_retry: bool = True
    enable_distributed: bool = True
    worker_nodes: List[str] = field(default_factory=list)
    result_aggregation: bool = True
    real_time_monitoring: bool = True
    performance_optimization: bool = True
    resource_limits: Dict[ResourceType, float] = field(default_factory=dict)

@dataclass
class ResourceMonitor:
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_latency: float = 0.0
    database_connections: int = 0
    external_api_calls: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class IntelligentScheduler:
    priority_queue: List[TestCase] = field(default_factory=list)
    running_tests: Set[str] = field(default_factory=set)
    completed_tests: Dict[str, ExecutionResult] = field(default_factory=dict)
    failed_tests: Dict[str, int] = field(default_factory=dict)
    resource_usage: Dict[ResourceType, float] = field(default_factory=dict)