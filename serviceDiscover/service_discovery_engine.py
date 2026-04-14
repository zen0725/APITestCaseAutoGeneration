import asyncio
import time
from typing import Dict, List, Optional
from serviceDiscover.service_models import ServiceDefinition, DiscoveryConfig, APIContract
from serviceDiscover.registry_integration import RegistryClient
from serviceDiscover.health_checker import ServiceHealthChecker
from serviceDiscover.contract_fetcher import APIContractFetcher
from logger import logger
from error_handler import error_handler, ServiceDiscoveryError, ErrorCode
import json
import hashlib

class ServiceDiscoveryEngine:
    def __init__(self, config: DiscoveryConfig):
        self.config = config
        self.registry_client = RegistryClient()
        self.health_checker = ServiceHealthChecker(config.health_check_timeout)
        self.contract_fetcher = APIContractFetcher(config.api_docs_timeout)

        self.discovered_services: Dict[str, ServiceDefinition] = {}
        self.api_contracts: Dict[str, APIContract] = {}
        self.last_discovery_time: float = 0
        self.is_running = False
        
        # 缓存机制
        self.cache = {}
        self.cache_expiry: Dict[str, float] = {}
        self.cache_ttl = 300  # 缓存过期时间（秒）

    async def start(self, registry_url: str):
        """启动服务发现引擎"""
        self.is_running = True
        self.logger.info("🚀 启动自动服务发现引擎")

        # 立即执行一次发现
        await self.run_discovery(registry_url)

        # 启动定期发现任务
        if self.config.enable_auto_refresh:
            asyncio.create_task(self._continuous_discovery(registry_url))

    async def stop(self):
        """停止服务发现引擎"""
        self.is_running = False
        self.logger.info("🛑 停止自动服务发现引擎")

    async def run_discovery(self, registry_url: str) -> Dict[str, APIContract]:
        """执行完整的服务发现流程"""
        logger.info("🔍 开始服务发现流程")

        try:
            # 检查缓存是否有效
            cache_key = f"discovery_{registry_url}"
            if self._is_cache_valid(cache_key):
                logger.info("✅ 使用缓存的服务发现结果")
                return self.cache[cache_key]

            # 1. 从注册中心发现服务
            try:
                services = await self.registry_client.discover_services(registry_url)
                logger.info(f"发现 {len(services)} 个服务")
            except Exception as e:
                error_handler.handle_service_discovery_error(
                    f"从注册中心发现服务失败: {e}",
                    {"registry_url": registry_url}
                )
                # 尝试使用缓存
                if cache_key in self.cache:
                    logger.warning("使用缓存的服务列表")
                    services = list(self.discovered_services.values())
                else:
                    raise ServiceDiscoveryError(
                        ErrorCode.SERVICE_DISCOVERY_FAILED,
                        f"从注册中心发现服务失败: {e}"
                    )

            # 2. 检查服务健康状态
            for service in services:
                try:
                    service.instances = await self.health_checker.check_all_instances(service.instances)
                    healthy_instances = [inst for inst in service.instances if inst.status.value == 'healthy']
                    logger.info(f"服务 {service.service_name}: {len(healthy_instances)}/{len(service.instances)} 个健康实例")
                except Exception as e:
                    error_handler.handle_service_discovery_error(
                        f"检查服务健康状态失败: {e}",
                        {"service_name": service.service_name}
                    )
                    # 继续处理其他服务
                    continue

            # 3. 获取API契约
            try:
                contracts = await self.contract_fetcher.fetch_multiple_contracts(services)
                logger.info(f"成功获取 {len(contracts)} 个API契约")
            except Exception as e:
                error_handler.handle_service_discovery_error(
                    f"获取API契约失败: {e}",
                    {"service_count": len(services)}
                )
                # 尝试使用缓存
                if cache_key in self.cache:
                    logger.warning("使用缓存的API契约")
                    contracts = self.cache[cache_key]
                else:
                    raise ServiceDiscoveryError(
                        ErrorCode.CONTRACT_FETCH_FAILED,
                        f"获取API契约失败: {e}"
                    )

            # 4. 更新状态
            self.discovered_services = {s.service_name: s for s in services}
            self.api_contracts.update(contracts)
            self.last_discovery_time = time.time()

            # 5. 检查契约变更
            changed_contracts = self._detect_contract_changes(contracts)
            if changed_contracts:
                logger.warning(f"检测到 {len(changed_contracts)} 个API契约变更")
                await self._notify_contract_changes(changed_contracts)

            # 6. 缓存结果
            self._cache_result(cache_key, contracts)

            return contracts

        except ServiceDiscoveryError:
            raise
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"服务发现失败: {e}")
            return {}

    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        if cache_key not in self.cache_expiry:
            return False
        return time.time() < self.cache_expiry[cache_key]

    def _cache_result(self, cache_key: str, result: Dict[str, APIContract]):
        """缓存结果"""
        self.cache[cache_key] = result
        self.cache_expiry[cache_key] = time.time() + self.cache_ttl
        logger.debug(f"缓存服务发现结果，过期时间: {self.cache_expiry[cache_key]}")

    def _invalidate_cache(self):
        """使缓存失效"""
        self.cache.clear()
        self.cache_expiry.clear()
        logger.debug("缓存已失效")

    async def _continuous_discovery(self, registry_url: str):
        """持续执行服务发现"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.poll_interval)
                await self.run_discovery(registry_url)
            except ServiceDiscoveryError as e:
                logger.error(f"持续发现错误: {e}")
                # 错误后等待更长时间
                await asyncio.sleep(120)  # 错误后等待2分钟
            except Exception as e:
                error_info = error_handler.handle_error(e)
                logger.error(f"持续发现错误: {e}")
                await asyncio.sleep(60)  # 错误后等待1分钟

    def _detect_contract_changes(self, new_contracts: Dict[str, APIContract]) -> Dict[str, APIContract]:
        """检测API契约变更"""
        changed_contracts = {}

        for service_name, new_contract in new_contracts.items():
            old_contract = self.api_contracts.get(service_name)

            if not old_contract:
                logger.info(f"新服务契约: {service_name}")
                changed_contracts[service_name] = new_contract
            elif old_contract.spec_hash != new_contract.spec_hash:
                logger.warning(f"服务契约变更: {service_name}")
                changed_contracts[service_name] = new_contract

        return changed_contracts

    async def _notify_contract_changes(self, changed_contracts: Dict[str, APIContract]):
        """通知API契约变更"""
        # 这里可以实现通知逻辑，如发送到消息队列、邮件、Slack等
        for service_name, contract in changed_contracts.items():
            logger.info(f"API契约变更通知 - 服务: {service_name}, 端点数量: {len(contract.endpoints)}")

    def get_service_contract(self, service_name: str) -> Optional[APIContract]:
        """获取指定服务的API契约"""
        try:
            contract = self.api_contracts.get(service_name)
            if not contract:
                logger.warning(f"服务 {service_name} 的API契约不存在")
            return contract
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取服务契约失败: {e}")
            return None

    def get_all_contracts(self) -> Dict[str, APIContract]:
        """获取所有API契约"""
        try:
            return self.api_contracts.copy()
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取所有契约失败: {e}")
            return {}

    def get_healthy_instances(self, service_name: str) -> List:
        """获取服务的健康实例"""
        try:
            service = self.discovered_services.get(service_name)
            if service:
                healthy_instances = [inst for inst in service.instances if inst.status.value == 'healthy']
                logger.debug(f"服务 {service_name} 有 {len(healthy_instances)} 个健康实例")
                return healthy_instances
            logger.warning(f"服务 {service_name} 不存在")
            return []
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取健康实例失败: {e}")
            return []

    def get_service_stats(self) -> Dict:
        """获取服务发现统计信息"""
        try:
            total_services = len(self.discovered_services)
            total_instances = sum(len(s.instances) for s in self.discovered_services.values())
            healthy_instances = sum(len(self.get_healthy_instances(sn)) for sn in self.discovered_services.keys())
            total_contracts = len(self.api_contracts)

            stats = {
                "total_services": total_services,
                "total_instances": total_instances,
                "healthy_instances": healthy_instances,
                "total_contracts": total_contracts,
                "last_discovery_time": self.last_discovery_time,
                "discovery_health": f"{healthy_instances}/{total_instances} ({healthy_instances/total_instances*100:.1f}%)" if total_instances > 0 else "N/A",
                "cache_status": {
                    "cache_size": len(self.cache),
                    "cache_expiry_count": len(self.cache_expiry)
                }
            }
            logger.debug(f"服务发现统计: {stats}")
            return stats
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取服务统计信息失败: {e}")
            return {
                "total_services": 0,
                "total_instances": 0,
                "healthy_instances": 0,
                "total_contracts": 0,
                "last_discovery_time": 0,
                "discovery_health": "N/A",
                "cache_status": {
                    "cache_size": 0,
                    "cache_expiry_count": 0
                }
            }