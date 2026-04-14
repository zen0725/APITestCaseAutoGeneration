import aiohttp
import asyncio
from typing import List, Dict
from serviceDiscover.service_models import ServiceInstance, ServiceStatus
import time

class ServiceHealthChecker:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.health_check_paths = [
            '/health',
            '/actuator/health',
            '/api/health',
            '/status',
            '/healthz',
            '/ready'
        ]

    async def check_service_health(self, instance: ServiceInstance) -> ServiceStatus:
        """检查服务实例的健康状态"""
        for health_path in self.health_check_paths:
            try:
                url = f"{instance.scheme}://{instance.host}:{instance.port}{health_path}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=self.timeout) as response:
                        if response.status in [200, 204]:
                            # 检查健康响应内容
                            if health_path in ['/actuator/health', '/health']:
                                health_data = await response.json()
                                if self._is_healthy_response(health_data):
                                    return ServiceStatus.HEALTHY
                            else:
                                return ServiceStatus.HEALTHY
            except (aiohttp.ClientError, asyncio.TimeoutError):
                continue

        return ServiceStatus.UNHEALTHY

    def _is_healthy_response(self, health_data: Dict) -> bool:
        """检查健康响应是否表示健康状态"""
        if isinstance(health_data, dict):
            status = health_data.get('status', '').lower()
            if status in ['up', 'healthy']:
                return True

            # 检查详细组件状态
            components = health_data.get('components', {})
            for comp_name, comp_data in components.items():
                comp_status = comp_data.get('status', '').lower()
                if comp_status not in ['up', 'healthy']:
                    return False
            return True

        return False

    async def check_all_instances(self, instances: List[ServiceInstance]) -> List[ServiceInstance]:
        """批量检查所有服务实例的健康状态"""
        tasks = []
        for instance in instances:
            tasks.append(self._check_instance_health(instance))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        updated_instances = []
        for instance, result in zip(instances, results):
            if isinstance(result, ServiceStatus):
                instance.status = result
                instance.last_heartbeat = time.time()
            updated_instances.append(instance)

        return updated_instances

    async def _check_instance_health(self, instance: ServiceInstance) -> ServiceStatus:
        """检查单个实例的健康状态"""
        try:
            return await self.check_service_health(instance)
        except Exception:
            return ServiceStatus.UNHEALTHY