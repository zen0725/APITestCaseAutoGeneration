from typing import Dict, Any, Optional
from enum import Enum
from logger import logger

class ErrorCode(Enum):
    """错误代码枚举"""
    # 服务发现相关错误
    SERVICE_DISCOVERY_FAILED = "SERVICE_DISCOVERY_FAILED"
    SERVICE_UNHEALTHY = "SERVICE_UNHEALTHY"
    CONTRACT_FETCH_FAILED = "CONTRACT_FETCH_FAILED"
    
    # 测试生成相关错误
    TEST_GENERATION_FAILED = "TEST_GENERATION_FAILED"
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    CONTRACT_PARSE_ERROR = "CONTRACT_PARSE_ERROR"
    
    # 测试执行相关错误
    TEST_EXECUTION_FAILED = "TEST_EXECUTION_FAILED"
    HTTP_REQUEST_ERROR = "HTTP_REQUEST_ERROR"
    ASSERTION_ERROR = "ASSERTION_ERROR"
    
    # 系统相关错误
    CONFIG_ERROR = "CONFIG_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class SmartTestError(Exception):
    """智能测试系统异常基类"""
    def __init__(self, error_code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{error_code.value}] {message}")

class ServiceDiscoveryError(SmartTestError):
    """服务发现异常"""
    pass

class TestGenerationError(SmartTestError):
    """测试生成异常"""
    pass

class TestExecutionError(SmartTestError):
    """测试执行异常"""
    pass

class SystemError(SmartTestError):
    """系统异常"""
    pass

class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def handle_error(error: Exception) -> Dict[str, Any]:
        """处理异常，返回标准化的错误信息"""
        if isinstance(error, SmartTestError):
            # 处理已知的智能测试系统异常
            error_info = {
                'error_code': error.error_code.value,
                'message': error.message,
                'details': error.details
            }
            
            # 根据错误类型记录不同级别的日志
            if error.error_code in [ErrorCode.SERVICE_DISCOVERY_FAILED, ErrorCode.TEST_EXECUTION_FAILED]:
                logger.error(f"[{error.error_code.value}] {error.message} - 详情: {error.details}")
            else:
                logger.warning(f"[{error.error_code.value}] {error.message} - 详情: {error.details}")
                
        else:
            # 处理未知异常
            error_info = {
                'error_code': ErrorCode.UNKNOWN_ERROR.value,
                'message': str(error),
                'details': {}
            }
            logger.error(f"[UNKNOWN_ERROR] {str(error)}")
        
        return error_info
    
    @staticmethod
    def handle_service_discovery_error(message: str, details: Optional[Dict[str, Any]] = None):
        """处理服务发现错误"""
        error = ServiceDiscoveryError(
            ErrorCode.SERVICE_DISCOVERY_FAILED,
            message,
            details
        )
        return ErrorHandler.handle_error(error)
    
    @staticmethod
    def handle_test_generation_error(message: str, details: Optional[Dict[str, Any]] = None):
        """处理测试生成错误"""
        error = TestGenerationError(
            ErrorCode.TEST_GENERATION_FAILED,
            message,
            details
        )
        return ErrorHandler.handle_error(error)
    
    @staticmethod
    def handle_test_execution_error(message: str, details: Optional[Dict[str, Any]] = None):
        """处理测试执行错误"""
        error = TestExecutionError(
            ErrorCode.TEST_EXECUTION_FAILED,
            message,
            details
        )
        return ErrorHandler.handle_error(error)
    
    @staticmethod
    def handle_system_error(message: str, details: Optional[Dict[str, Any]] = None):
        """处理系统错误"""
        error = SystemError(
            ErrorCode.SYSTEM_ERROR,
            message,
            details
        )
        return ErrorHandler.handle_error(error)
    
    @staticmethod
    def wrap_async_error(func):
        """异步函数错误包装装饰器"""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_info = ErrorHandler.handle_error(e)
                # 可以在这里添加额外的错误处理逻辑
                # 例如：发送错误通知、记录错误指标等
                raise
        return wrapper
    
    @staticmethod
    def wrap_sync_error(func):
        """同步函数错误包装装饰器"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = ErrorHandler.handle_error(e)
                # 可以在这里添加额外的错误处理逻辑
                # 例如：发送错误通知、记录错误指标等
                raise
        return wrapper

# 全局错误处理器实例
error_handler = ErrorHandler()
