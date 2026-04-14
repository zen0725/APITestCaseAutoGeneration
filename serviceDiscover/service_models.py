from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
import time
import uuid
from datetime import datetime

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"

class ServiceType(Enum):
    HTTP_REST = "http_rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"
    KAFKA = "kafka"

@dataclass
class ServiceInstance:
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = ""
    host: str = "localhost"
    port: int = 8080
    scheme: str = "http"
    metadata: Dict[str, str] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_heartbeat: float = field(default_factory=time.time)
    tags: Set[str] = field(default_factory=set)

@dataclass
class ServiceDefinition:
    service_name: str
    service_type: ServiceType
    instances: List[ServiceInstance] = field(default_factory=list)
    openapi_spec: Optional[Dict] = None
    last_updated: float = field(default_factory=time.time)
    contract_hash: Optional[str] = None

@dataclass
class DiscoveryConfig:
    poll_interval: int = 30  # 秒
    health_check_timeout: int = 5
    api_docs_timeout: int = 10
    max_retries: int = 3
    cache_ttl: int = 300  # 秒
    enable_auto_refresh: bool = True

@dataclass
class APIContract:
    service_name: str
    openapi_spec: Dict
    endpoints: List[str]
    last_updated: float
    spec_hash: str
    source: str  # swagger, openapi, manual