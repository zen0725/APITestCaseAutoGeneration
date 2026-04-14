from typing import Dict, List, Any, Optional
import json
import os
import tempfile
import uuid
from datetime import datetime
from logger import logger
from error_handler import error_handler

class TestDataManager:
    """测试数据管理"""
    
    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = data_dir
        self.test_data: Dict[str, Dict[str, Any]] = {}
        self.temporary_data: Dict[str, str] = {}
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            logger.debug(f"确保数据目录存在: {self.data_dir}")
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"创建数据目录失败: {e}")
    
    def generate_test_data(self, service_name: str, endpoint: str, method: str, data_template: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试数据"""
        try:
            data_key = f"{service_name}_{method}_{endpoint}".replace('/', '_')
            
            # 生成唯一标识符
            unique_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # 替换模板中的变量
            test_data = self._replace_template_variables(data_template, unique_id, timestamp)
            
            # 存储测试数据
            self.test_data[data_key] = test_data
            logger.debug(f"为 {service_name} {method} {endpoint} 生成测试数据")
            
            return test_data
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"生成测试数据失败: {e}")
            return data_template
    
    def _replace_template_variables(self, data: Any, unique_id: str, timestamp: str) -> Any:
        """替换模板中的变量"""
        if isinstance(data, dict):
            return {k: self._replace_template_variables(v, unique_id, timestamp) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_template_variables(item, unique_id, timestamp) for item in data]
        elif isinstance(data, str):
            return data.replace("{unique_id}", unique_id).replace("{timestamp}", timestamp)
        else:
            return data
    
    def store_test_data(self, test_id: str, data: Dict[str, Any]) -> str:
        """存储测试数据到文件"""
        try:
            filename = os.path.join(self.data_dir, f"{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"存储测试数据到文件: {filename}")
            return filename
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"存储测试数据失败: {e}")
            return ""
    
    def load_test_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """从文件加载测试数据"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                logger.debug(f"从文件加载测试数据: {file_path}")
                return data
            else:
                logger.warning(f"测试数据文件不存在: {file_path}")
                return None
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"加载测试数据失败: {e}")
            return None
    
    def create_temporary_data(self, data: Dict[str, Any]) -> str:
        """创建临时测试数据"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f, indent=2)
                temp_filename = f.name
            
            data_id = str(uuid.uuid4())
            self.temporary_data[data_id] = temp_filename
            logger.debug(f"创建临时测试数据: {temp_filename}")
            return data_id
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"创建临时测试数据失败: {e}")
            return ""
    
    def get_temporary_data(self, data_id: str) -> Optional[Dict[str, Any]]:
        """获取临时测试数据"""
        try:
            if data_id in self.temporary_data:
                temp_filename = self.temporary_data[data_id]
                if os.path.exists(temp_filename):
                    with open(temp_filename, 'r') as f:
                        data = json.load(f)
                    logger.debug(f"获取临时测试数据: {data_id}")
                    return data
                else:
                    logger.warning(f"临时测试数据文件不存在: {temp_filename}")
                    return None
            else:
                logger.warning(f"临时测试数据ID不存在: {data_id}")
                return None
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取临时测试数据失败: {e}")
            return None
    
    def cleanup_temporary_data(self, data_id: str):
        """清理临时测试数据"""
        try:
            if data_id in self.temporary_data:
                temp_filename = self.temporary_data[data_id]
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    logger.debug(f"清理临时测试数据: {temp_filename}")
                del self.temporary_data[data_id]
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"清理临时测试数据失败: {e}")
    
    def cleanup_all_temporary_data(self):
        """清理所有临时测试数据"""
        try:
            for data_id, temp_filename in list(self.temporary_data.items()):
                self.cleanup_temporary_data(data_id)
            logger.info("清理所有临时测试数据")
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"清理所有临时测试数据失败: {e}")
    
    def get_data_stats(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        try:
            stats = {
                'test_data_count': len(self.test_data),
                'temporary_data_count': len(self.temporary_data),
                'data_dir': self.data_dir,
                'data_dir_size': self._get_directory_size(self.data_dir)
            }
            logger.debug(f"数据统计信息: {stats}")
            return stats
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取数据统计信息失败: {e}")
            return {
                'test_data_count': 0,
                'temporary_data_count': 0,
                'data_dir': self.data_dir,
                'data_dir_size': 0
            }
    
    def _get_directory_size(self, path: str) -> int:
        """获取目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            error_info = error_handler.handle_error(e)
            logger.error(f"获取目录大小失败: {e}")
        return total_size

# 全局测试数据管理器实例
test_data_manager = TestDataManager()
