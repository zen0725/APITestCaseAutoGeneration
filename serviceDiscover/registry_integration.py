import aiohttp
import asyncio
from typing import Dict, List, Optional
from serviceDiscover.service_models import ServiceInstance, ServiceStatus, ServiceDefinition, ServiceType
import json
import logging

class RegistryClient:
    def __init__(self):
        self.logger = logging.getLogger("RegistryClient")

    async def discover_services(self, registry_url: str) -> List[ServiceDefinition]:
        """从服务注册中心发现服务"""
        clients = [
            self._discover_eureka(registry_url),
            self._discover_consul(registry_url),
            self._discover_nacos(registry_url),
            self._discover_kubernetes(registry_url)
        ]

        for client in clients:
            try:
                services = await client
                if services:
                    return services
            except Exception as e:
                self.logger.debug(f"注册中心发现失败: {e}")
                continue

        raise Exception("无法从任何注册中心发现服务")

    async def _discover_eureka(self, eureka_url: str) -> List[ServiceDefinition]:
        """发现Eureka注册的服务"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{eureka_url}/eureka/apps"
                async with session.get(url, headers={"Accept": "application/json"}) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_eureka_response(data)
        except Exception as e:
            self.logger.error(f"Eureka发现失败: {e}")
            return []

    def _parse_eureka_response(self, data: Dict) -> List[ServiceDefinition]:
        """解析Eureka响应"""
        services = []
        apps = data.get('applications', {}).get('application', [])

        for app in apps:
            service_name = app.get('name', '').lower()
            instances = app.get('instance', [])

            service_instances = []
            for instance in instances:
                status = ServiceStatus.HEALTHY if instance.get('status') == 'UP' else ServiceStatus.UNHEALTHY
                service_instances.append(ServiceInstance(
                    service_name=service_name,
                    host=instance.get('ipAddr', 'localhost'),
                    port=instance.get('port', {}).get('$', 8080),
                    status=status,
                    metadata=instance.get('metadata', {})
                ))

            services.append(ServiceDefinition(
                service_name=service_name,
                service_type=ServiceType.HTTP_REST,
                instances=service_instances
            ))

        return services

    async def _discover_consul(self, consul_url: str) -> List[ServiceDefinition]:
        """发现Consul注册的服务"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{consul_url}/v1/catalog/services"
                async with session.get(url) as response:
                    if response.status == 200:
                        services_data = await response.json()
                        return await self._get_consul_service_details(consul_url, services_data)
        except Exception as e:
            self.logger.error(f"Consul发现失败: {e}")
            return []

    async def _get_consul_service_details(self, consul_url: str, services_data: Dict) -> List[ServiceDefinition]:
        """获取Consul服务的详细实例信息"""
        services = []

        for service_name in services_data.keys():
            if service_name.startswith('consul'):
                continue

            async with aiohttp.ClientSession() as session:
                url = f"{consul_url}/v1/catalog/service/{service_name}"
                async with session.get(url) as response:
                    if response.status == 200:
                        instances_data = await response.json()

                        service_instances = []
                        for instance in instances_data:
                            service_instances.append(ServiceInstance(
                                service_name=service_name,
                                host=instance.get('ServiceAddress', 'localhost'),
                                port=instance.get('ServicePort', 8080),
                                status=ServiceStatus.HEALTHY,
                                metadata=instance.get('ServiceMeta', {})
                            ))

                        services.append(ServiceDefinition(
                            service_name=service_name,
                            service_type=ServiceType.HTTP_REST,
                            instances=service_instances
                        ))

        return services

    async def _discover_nacos(self, nacos_url: str) -> List[ServiceDefinition]:
        """发现Nacos注册的服务"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{nacos_url}/nacos/v1/ns/service/list"
                async with session.get(url, params={'pageNo': 1, 'pageSize': 100}) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._get_nacos_service_details(nacos_url, data)
        except Exception as e:
            self.logger.error(f"Nacos发现失败: {e}")
            return []

    async def _discover_kubernetes(self, k8s_api_url: str) -> List[ServiceDefinition]:
        """发现Kubernetes服务"""
        try:
            # 这里需要Kubernetes客户端配置
            # 简化实现：通过API发现服务
            async with aiohttp.ClientSession() as session:
                url = f"{k8s_api_url}/api/v1/services"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_kubernetes_services(data)
        except Exception as e:
            self.logger.error(f"Kubernetes发现失败: {e}")
            return []

    def _parse_kubernetes_services(self, data: Dict) -> List[ServiceDefinition]:
        """解析Kubernetes服务"""
        services = []
        items = data.get('items', [])

        for item in items:
            metadata = item.get('metadata', {})
            spec = item.get('spec', {})

            service_name = metadata.get('name', '')
            service_instances = []

            # 对于Kubernetes，我们通常通过Service的ClusterIP和Port访问
            cluster_ip = spec.get('clusterIP', '')
            ports = spec.get('ports', [])

            for port in ports:
                service_instances.append(ServiceInstance(
                    service_name=service_name,
                    host=cluster_ip,
                    port=port.get('port', 8080),
                    status=ServiceStatus.HEALTHY,
                    metadata={
                        'namespace': metadata.get('namespace', 'default'),
                        'k8s_service': 'true'
                    }
                ))

            services.append(ServiceDefinition(
                service_name=service_name,
                service_type=ServiceType.HTTP_REST,
                instances=service_instances
            ))

        return services