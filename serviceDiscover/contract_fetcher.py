import aiohttp
import asyncio
from typing import Dict, Optional, List
import json
import hashlib
import time
from serviceDiscover.service_models import APIContract

class APIContractFetcher:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.api_docs_paths = [
            '/v3/api-docs',
            '/v2/api-docs',
            '/swagger.json',
            '/swagger.yaml',
            '/swagger-ui.html',
            '/api-docs',
            '/openapi.json',
            '/openapi.yaml'
        ]

    async def fetch_contract_for_service(self, service_name: str, instances: List) -> Optional[APIContract]:
        """为服务获取API契约"""
        for instance in instances:
            if instance.status.value != 'healthy':
                continue

            for docs_path in self.api_docs_paths:
                try:
                    contract = await self._try_fetch_contract(instance, docs_path)
                    if contract:
                        return APIContract(
                            service_name=service_name,
                            openapi_spec=contract,
                            endpoints=self._extract_endpoints(contract),
                            last_updated=time.time(),
                            spec_hash=self._calculate_spec_hash(contract),
                            source=docs_path
                        )
                except Exception as e:
                    continue

        return None

    async def _try_fetch_contract(self, instance, docs_path: str) -> Optional[Dict]:
        """尝试从特定路径获取契约"""
        url = f"{instance.scheme}://{instance.host}:{instance.port}{docs_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')

                    if 'application/json' in content_type:
                        return await response.json()
                    elif 'application/yaml' in content_type or 'text/yaml' in content_type:
                        import yaml
                        text = await response.text()
                        return yaml.safe_load(text)
                    else:
                        # 尝试解析为JSON
                        try:
                            return await response.json()
                        except:
                            # 尝试解析为YAML
                            try:
                                import yaml
                                text = await response.text()
                                return yaml.safe_load(text)
                            except:
                                return None
        return None

    def _extract_endpoints(self, openapi_spec: Dict) -> List[str]:
        """从OpenAPI规范中提取端点"""
        endpoints = []
        paths = openapi_spec.get('paths', {})

        for path, methods in paths.items():
            for method in methods.keys():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    endpoints.append(f"{method.upper()} {path}")

        return endpoints

    def _calculate_spec_hash(self, spec: Dict) -> str:
        """计算API规范的哈希值"""
        spec_str = json.dumps(spec, sort_keys=True)
        return hashlib.md5(spec_str.encode()).hexdigest()

    async def fetch_multiple_contracts(self, services: List) -> Dict[str, APIContract]:
        """批量获取多个服务的API契约"""
        contracts = {}
        tasks = []

        for service in services:
            if service.instances:
                tasks.append(self._fetch_single_service_contract(service))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for service, result in zip(services, results):
            if isinstance(result, APIContract):
                contracts[service.service_name] = result

        return contracts

    async def _fetch_single_service_contract(self, service) -> Optional[APIContract]:
        """获取单个服务的API契约"""
        return await self.fetch_contract_for_service(service.service_name, service.instances)