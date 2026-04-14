from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import asyncio
from workerNode.worker_models import WorkerConfig, WorkerStatus, ExecutionTask, TaskResult, TaskStatus
from workerNode.resource_manager import ResourceManager
from workerNode.task_executor import TaskExecutor
from workerNode.health_monitor import HealthMonitor
import logging
from datetime import datetime
import os

class WorkerNode:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.app = FastAPI(title=f"Test Worker {config.worker_id}")
        self.status = WorkerStatus.STARTING
        self.resource_manager = ResourceManager(config)
        self.test_executor = TaskExecutor(config.work_dir)
        self.health_monitor = HealthMonitor()
        self.current_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, TaskResult] = {}

        self._setup_api_routes()
        self._setup_background_tasks()

        self.logger = logging.getLogger(f"WorkerNode-{config.worker_id}")
        logging.basicConfig(level=getattr(logging, config.log_level))

    def _setup_api_routes(self):
        """设置API路由"""

        @self.app.get("/")
        async def root():
            return {"message": f"Test Worker {self.config.worker_id} is running"}

        @self.app.get("/health")
        async def health_check():
            health_status = await self.health_monitor.perform_health_check()
            return {
                "worker_id": self.config.worker_id,
                "status": self.status.value,
                "health": health_status,
                "current_tasks": len(self.current_tasks),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/info")
        async def get_worker_info():
            current_usage = await self.resource_manager.get_current_usage()
            capabilities = self.resource_manager.get_worker_capabilities()

            return {
                "worker_id": self.config.worker_id,
                "host": self.config.host,
                "port": self.config.port,
                "status": self.status.value,
                "capabilities": capabilities,
                "resource_usage": current_usage,
                "current_tasks": len(self.current_tasks),
                "max_tasks": self.config.max_workers,
                "last_heartbeat": datetime.now().isoformat()
            }

        @self.app.post("/execute")
        async def execute_task(task: ExecutionTask, background_tasks: BackgroundTasks):
            # 检查工作节点状态
            if self.status != WorkerStatus.READY:
                raise HTTPException(status_code=503, detail="Worker is not ready")

            # 检查资源可用性
            task_requirements = task.metadata.get('resource_requirements', {
                'memory_mb': 100,
                'cpu_percent': 10
            })

            if not await self.resource_manager.check_resource_availability(task_requirements):
                raise HTTPException(status_code=429, detail="Insufficient resources")

            # 分配资源
            self.resource_manager.allocate_resources(task.task_id, task_requirements)

            # 在后台执行任务
            background_tasks.add_task(self._execute_task_background, task)

            return {
                "task_id": task.task_id,
                "status": "accepted",
                "message": "Task is being executed in background",
                "worker_id": self.config.worker_id
            }

        @self.app.get("/tasks/{task_id}")
        async def get_task_status(task_id: str):
            if task_id in self.task_results:
                return self.task_results[task_id]
            elif task_id in self.current_tasks:
                return {"task_id": task_id, "status": "running"}
            else:
                raise HTTPException(status_code=404, detail="Task not found")

        @self.app.delete("/tasks/{task_id}")
        async def cancel_task(task_id: str):
            if task_id in self.current_tasks:
                self.current_tasks[task_id].cancel()
                return {"message": f"Task {task_id} cancellation requested"}
            else:
                raise HTTPException(status_code=404, detail="Task not found")

        @self.app.post("/drain")
        async def drain_worker():
            """开始排水模式（不再接受新任务）"""
            self.status = WorkerStatus.DRAINING
            return {"message": "Worker is draining, no new tasks will be accepted"}

        @self.app.post("/stop")
        async def stop_worker():
            """停止工作节点"""
            self.status = WorkerStatus.STOPPING
            # 取消所有正在执行的任务
            for task_id, task in self.current_tasks.items():
                task.cancel()
            return {"message": "Worker is stopping"}

    def _setup_background_tasks(self):
        """设置后台任务"""

        @self.app.on_event("startup")
        async def startup_event():
            self.status = WorkerStatus.READY
            self.logger.info(f"Worker {self.config.worker_id} started on {self.config.host}:{self.config.port}")

            # 启动心跳任务
            asyncio.create_task(self._heartbeat_task())

            # 启动资源监控任务
            asyncio.create_task(self._resource_monitoring_task())

        @self.app.on_event("shutdown")
        async def shutdown_event():
            self.status = WorkerStatus.STOPPING
            self.logger.info("Worker is shutting down")

            # 关闭执行器
            await self.test_executor.close()

            # 等待所有任务完成或超时
            await asyncio.sleep(5)

    async def _execute_task_background(self, task: ExecutionTask):
        """在后台执行任务"""
        self.logger.info(f"Starting background execution of task {task.task_id}")

        try:
            # 创建执行任务
            task_future = asyncio.create_task(self.test_executor.execute_task(task))
            self.current_tasks[task.task_id] = task_future

            # 等待任务完成
            result = await task_future

            # 存储结果
            self.task_results[task.task_id] = result

            # 清理资源
            self.resource_manager.release_resources(task.task_id)
            self.current_tasks.pop(task.task_id, None)

            self.logger.info(f"Background task {task.task_id} completed with status: {result.status}")

        except asyncio.CancelledError:
            self.logger.info(f"Task {task.task_id} was cancelled")
            # 创建取消结果
            cancel_result = TaskResult(
                task_id=task.task_id,
                test_id=task.test_id,
                status=TaskStatus.CANCELLED,
                duration=0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message="Task was cancelled"
            )
            self.task_results[task.task_id] = cancel_result
            self.resource_manager.release_resources(task.task_id)

        except Exception as e:
            self.logger.error(f"Background task {task.task_id} failed: {e}")
            error_result = TaskResult(
                task_id=task.task_id,
                test_id=task.test_id,
                status=TaskStatus.FAILED,
                duration=0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=str(e)
            )
            self.task_results[task.task_id] = error_result
            self.resource_manager.release_resources(task.task_id)

        finally:
            self.current_tasks.pop(task.task_id, None)

    async def _heartbeat_task(self):
        """心跳任务 - 定期向主节点发送心跳"""
        while self.status != WorkerStatus.STOPPING:
            try:
                if self.status == WorkerStatus.READY:
                    # 向主节点发送心跳
                    worker_info = await self._get_worker_info()

                    # 这里应该发送HTTP请求到主节点
                    # await self._send_heartbeat_to_master(worker_info)

                    self.logger.debug("Heartbeat sent to master")

                await asyncio.sleep(self.config.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"Heartbeat task error: {e}")
                await asyncio.sleep(5)  # 错误后等待5秒

    async def _resource_monitoring_task(self):
        """资源监控任务"""
        while self.status != WorkerStatus.STOPPING:
            try:
                # 更新资源使用情况
                await self.resource_manager.get_current_usage()

                # 检查资源使用情况，必要时进入排水模式
                current_usage = self.resource_manager.current_usage
                if (current_usage.get('memory_percent', 0) > 90 or
                        current_usage.get('cpu_percent', 0) > 90):
                    self.status = WorkerStatus.DRAINING
                    self.logger.warning("High resource usage, entering drain mode")

                await asyncio.sleep(10)  # 每10秒检查一次

            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(10)

    async def _get_worker_info(self):
        """获取工作节点信息"""
        current_usage = await self.resource_manager.get_current_usage()
        capabilities = self.resource_manager.get_worker_capabilities()

        return {
            "worker_id": self.config.worker_id,
            "host": self.config.host,
            "port": self.config.port,
            "status": self.status.value,
            "capabilities": capabilities,
            "resource_usage": current_usage,
            "current_tasks": len(self.current_tasks),
            "max_tasks": self.config.max_workers,
            "last_heartbeat": datetime.now().isoformat()
        }

    def run(self):
        """运行工作节点"""
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level.lower()
        )


# 启动脚本
if __name__ == "__main__":
    # 从环境变量或配置文件读取配置
    config = WorkerConfig(
        worker_id=os.getenv('WORKER_ID', f'worker-{socket.gethostname()}'),
        host=os.getenv('WORKER_HOST', '0.0.0.0'),
        port=int(os.getenv('WORKER_PORT', '8080')),
        max_workers=int(os.getenv('MAX_WORKERS', '10')),
        master_url=os.getenv('MASTER_URL', 'http://localhost:8000')
    )

    # 创建工作目录
    os.makedirs(config.work_dir, exist_ok=True)

    # 创建并运行工作节点
    worker = WorkerNode(config)
    worker.run()