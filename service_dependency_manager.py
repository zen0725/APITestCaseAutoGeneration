from typing import Dict, List, Set, Optional, Any
from logger import logger
from error_handler import error_handler, ServiceDiscoveryError, ErrorCode
from datetime import datetime

class ServiceDependencyManager:
    """服务依赖关系管理"""
    
    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.service_health: Dict[str, bool] = {}
        self.last_update_time: float = 0
    
    def register_service(self, service_name: str, dependencies: List[str] = None):
        """注册服务及其依赖"""
        try:
            dependencies = dependencies or []
            self.dependencies[service_name] = set(dependencies)
            
            # 更新依赖图
            for dep in dependencies:
                if dep not in self.dependency_graph:
                    self.dependency_graph[dep] = []
                if service_name not in self.dependency_graph[dep]:
                    self.dependency_graph[dep].append(service_name)
            
            logger.info(f"注册服务: {service_name}，依赖: {dependencies}")
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"注册服务失败: {e}")
    
    def get_service_dependencies(self, service_name: str) -> Set[str]:
        """获取服务的直接依赖"""
        try:
            return self.dependencies.get(service_name, set())
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取服务依赖失败: {e}")
            return set()
    
    def get_transitive_dependencies(self, service_name: str) -> Set[str]:
        """获取服务的传递依赖"""
        try:
            visited = set()
            queue = [service_name]
            
            while queue:
                current = queue.pop(0)
                if current not in visited:
                    visited.add(current)
                    queue.extend(self.dependencies.get(current, set()) - visited)
            
            # 移除自身
            visited.discard(service_name)
            logger.debug(f"服务 {service_name} 的传递依赖: {visited}")
            return visited
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取传递依赖失败: {e}")
            return set()
    
    def get_service_dependents(self, service_name: str) -> List[str]:
        """获取依赖指定服务的所有服务"""
        try:
            return self.dependency_graph.get(service_name, [])
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取服务依赖者失败: {e}")
            return []
    
    def sort_services_by_dependency(self, services: List[str]) -> List[str]:
        """根据依赖关系排序服务"""
        try:
            visited = set()
            result = []
            
            def dfs(service: str):
                if service not in visited:
                    visited.add(service)
                    for dep in self.dependencies.get(service, set()):
                        if dep not in visited:
                            dfs(dep)
                    result.append(service)
            
            for service in services:
                if service not in visited:
                    dfs(service)
            
            logger.debug(f"服务依赖排序结果: {result}")
            return result
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"服务依赖排序失败: {e}")
            return services
    
    def check_dependency_health(self, service_name: str) -> bool:
        """检查服务的依赖是否健康"""
        try:
            dependencies = self.get_transitive_dependencies(service_name)
            for dep in dependencies:
                if not self.service_health.get(dep, True):
                    logger.warning(f"服务 {service_name} 的依赖 {dep} 不健康")
                    return False
            return True
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"检查依赖健康失败: {e}")
            return False
    
    def update_service_health(self, service_name: str, is_healthy: bool):
        """更新服务健康状态"""
        try:
            self.service_health[service_name] = is_healthy
            logger.debug(f"更新服务健康状态: {service_name} -> {is_healthy}")
            
            # 如果服务状态变为不健康，通知依赖它的服务
            if not is_healthy:
                dependents = self.get_service_dependents(service_name)
                for dependent in dependents:
                    logger.warning(f"服务 {dependent} 的依赖 {service_name} 变为不健康")
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"更新服务健康状态失败: {e}")
    
    def get_dependency_stats(self) -> Dict[str, Any]:
        """获取依赖统计信息"""
        try:
            stats = {
                'total_services': len(self.dependencies),
                'dependency_count': sum(len(deps) for deps in self.dependencies.values()),
                'service_health': self.service_health,
                'dependency_graph_size': len(self.dependency_graph),
                'last_update_time': self.last_update_time
            }
            logger.debug(f"依赖统计信息: {stats}")
            return stats
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取依赖统计信息失败: {e}")
            return {
                'total_services': 0,
                'dependency_count': 0,
                'service_health': {},
                'dependency_graph_size': 0,
                'last_update_time': 0
            }
    
    def clear(self):
        """清空依赖关系"""
        try:
            self.dependencies.clear()
            self.dependency_graph.clear()
            self.service_health.clear()
            self.last_update_time = datetime.now().timestamp()
            logger.info("清空依赖关系")
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"清空依赖关系失败: {e}")

# 全局依赖管理器实例
dependency_manager = ServiceDependencyManager()
