import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import config_manager

class Logger:
    def __init__(self, name: str = 'smart-microservice-test'):
        self.name = name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        # 获取日志配置
        log_config = config_manager.get_log_config()
        log_level = getattr(logging, log_config['level'], logging.INFO)
        log_file = log_config['file']
        
        # 创建日志目录
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志记录器
        logger = logging.getLogger(self.name)
        logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 创建文件处理器
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(log_level)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 设置日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger

    def debug(self, message: str):
        """记录调试级别的日志"""
        self.logger.debug(message)

    def info(self, message: str):
        """记录信息级别的日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """记录警告级别的日志"""
        self.logger.warning(message)

    def error(self, message: str):
        """记录错误级别的日志"""
        self.logger.error(message)

    def critical(self, message: str):
        """记录严重级别的日志"""
        self.logger.critical(message)

# 创建全局日志实例
logger = Logger()
