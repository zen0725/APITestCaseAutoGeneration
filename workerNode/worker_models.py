from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import asyncio
import multiprocessing
from datetime import datetime
import psutil
import socket

class WorkerStatus(Enum):
    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    DRAINING = "draining"
    STOPPING = "stopping"
    ERROR = "error"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkerConfig:
    worker_id: str
    host: str = "0.0.0.0"
    port: int = 8080
    max_workers: int = 10
    max_memory_mb: int = 4096
    max_cpu_percent: float = 80.0
    task_timeout: int = 300
    heartbeat_interval: int = 30
    master_url: str = "http://localhost:8000"
    work_dir: str = "/tmp/test_worker"
    log_level: str = "INFO"

@dataclass
class WorkerNodeInfo:
    worker_id: str
    host: str
    port: int
    status: WorkerStatus
    capabilities: Dict[str, Any]
    resource_usage: Dict[str, float]
    current_tasks: int
    max_tasks: int
    last_heartbeat: datetime

@dataclass
class ExecutionTask:
    task_id: str
    test_id: str
    service_name: str
    base_url: str
    endpoint: str
    method: str
    payload: Dict[str, Any]
    timeout: int
    assertions: List[Dict]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskResult:
    task_id: str
    test_id: str
    status: TaskStatus
    duration: float
    start_time: datetime
    end_time: datetime
    response: Optional[Dict] = None
    assertion_results: List[Dict] = field(default_factory=list)
    error_message: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)