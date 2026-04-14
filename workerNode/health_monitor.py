import asyncio
import psutil
from typing import Dict
from workerNode.worker_models import WorkerStatus
import logging
import datetime
from typing import Any

class HealthMonitor:
    def __init__(self):
        self.logger = logging.getLogger("HealthMonitor")
        self.health_checks = {}
        self.last_check_time = None

    async def perform_health_check(self) -> Dict[str, Any]:
        """执行健康检查"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'metrics': {}
        }

        # 系统资源检查
        health_status['checks']['system_resources'] = await self._check_system_resources()

        # 网络连接检查
        health_status['checks']['network'] = await self._check_network_connectivity()

        # 磁盘空间检查
        health_status['checks']['disk_space'] = await self._check_disk_space()

        # 进程状态检查
        health_status['checks']['process'] = await self._check_process_health()

        # 收集系统指标
        health_status['metrics'].update(await self._collect_system_metrics())

        # 确定整体状态
        if any(check['status'] != 'healthy' for check in health_status['checks'].values()):
            health_status['overall_status'] = 'unhealthy'

        self.last_check_time = datetime.now()
        return health_status

    async def _check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)

            check_result = {
                'status': 'healthy',
                'memory_usage_percent': memory.percent,
                'cpu_usage_percent': cpu_percent,
                'details': {}
            }

            # 内存检查
            if memory.percent > 90:
                check_result['status'] = 'unhealthy'
                check_result['details']['memory'] = '内存使用率过高'
            elif memory.percent > 80:
                check_result['status'] = 'warning'
                check_result['details']['memory'] = '内存使用率较高'

            # CPU检查
            if cpu_percent > 90:
                check_result['status'] = 'unhealthy'
                check_result['details']['cpu'] = 'CPU使用率过高'
            elif cpu_percent > 80:
                check_result['status'] = 'warning'
                check_result['details']['cpu'] = 'CPU使用率较高'

            return check_result

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    async def _check_network_connectivity(self) -> Dict[str, Any]:
        """检查网络连接性"""
        try:
            import socket
            # 测试连接到本地回环
            socket.create_connection(("127.0.0.1", 80), timeout=5)
            return {'status': 'healthy', 'details': '网络连接正常'}
        except:
            return {'status': 'unhealthy', 'details': '网络连接失败'}

    async def _check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        try:
            disk = psutil.disk_usage('/')
            check_result = {
                'status': 'healthy',
                'disk_usage_percent': disk.percent,
                'details': {}
            }

            if disk.percent > 95:
                check_result['status'] = 'unhealthy'
                check_result['details']['disk'] = '磁盘空间不足'
            elif disk.percent > 85:
                check_result['status'] = 'warning'
                check_result['details']['disk'] = '磁盘空间紧张'

            return check_result
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    async def _check_process_health(self) -> Dict[str, Any]:
        """检查进程健康状态"""
        try:
            process = psutil.Process()
            check_result = {
                'status': 'healthy',
                'process_id': process.pid,
                'memory_usage_mb': process.memory_info().rss / 1024 / 1024,
                'details': {}
            }

            # 检查进程是否响应
            if not process.is_running():
                check_result['status'] = 'unhealthy'
                check_result['details']['process'] = '进程未运行'

            return check_result
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    async def _collect_system_metrics(self) -> Dict[str, float]:
        """收集系统指标"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = psutil.getloadavg()

            return {
                'memory_used_mb': memory.used / 1024 / 1024,
                'memory_total_mb': memory.total / 1024 / 1024,
                'memory_percent': memory.percent,
                'disk_used_gb': disk.used / 1024 / 1024 / 1024,
                'disk_total_gb': disk.total / 1024 / 1024 / 1024,
                'disk_percent': disk.percent,
                'load_avg_1min': load_avg[0],
                'load_avg_5min': load_avg[1],
                'load_avg_15min': load_avg[2]
            }
        except:
            return {}