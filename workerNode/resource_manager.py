import psutil
from typing import Dict, Any
from workerNode.worker_models import WorkerConfig
import logging
import sys
import datetime
import multiprocessing

class ResourceManager:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.logger = logging.getLogger("ResourceManager")
        self.resource_limits = {
            'memory_mb': config.max_memory_mb,
            'cpu_percent': config.max_cpu_percent
        }
        self.current_usage = {}
        self.task_resources = {}

    async def check_resource_availability(self, task_requirements: Dict) -> bool:
        """检查资源是否可用"""
        current_usage = await self.get_current_usage()

        # 检查内存
        required_memory = task_requirements.get('memory_mb', 100)
        if current_usage['memory_mb'] + required_memory > self.resource_limits['memory_mb']:
            self.logger.warning(
                f"内存不足: {current_usage['memory_mb']} + {required_memory} > {self.resource_limits['memory_mb']}")
            return False

        # 检查CPU
        required_cpu = task_requirements.get('cpu_percent', 10)
        if current_usage['cpu_percent'] + required_cpu > self.resource_limits['cpu_percent']:
            self.logger.warning(
                f"CPU不足: {current_usage['cpu_percent']} + {required_cpu} > {self.resource_limits['cpu_percent']}")
            return False

        return True

    async def get_current_usage(self) -> Dict[str, float]:
        """获取当前资源使用情况"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)

        self.current_usage = {
            'memory_mb': memory.used / 1024 / 1024,
            'cpu_percent': cpu,
            'memory_percent': memory.percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

        return self.current_usage

    def allocate_resources(self, task_id: str, requirements: Dict):
        """分配资源给任务"""
        self.task_resources[task_id] = {
            'memory_mb': requirements.get('memory_mb', 100),
            'cpu_percent': requirements.get('cpu_percent', 10),
            'allocated_at': datetime.now()
        }
        self.logger.info(f"为任务 {task_id} 分配资源: {requirements}")

    def release_resources(self, task_id: str):
        """释放任务资源"""
        if task_id in self.task_resources:
            released = self.task_resources.pop(task_id)
            self.logger.info(f"释放任务 {task_id} 的资源: {released}")

    def get_worker_capabilities(self) -> Dict[str, Any]:
        """获取工作节点能力信息"""
        return {
            'max_memory_mb': self.resource_limits['memory_mb'],
            'max_cpu_percent': self.resource_limits['cpu_percent'],
            'available_memory_mb': self.resource_limits['memory_mb'] - self.current_usage.get('memory_mb', 0),
            'available_cpu_percent': self.resource_limits['cpu_percent'] - self.current_usage.get('cpu_percent', 0),
            'total_workers': multiprocessing.cpu_count(),
            'platform': sys.platform,
            'python_version': sys.version
        }