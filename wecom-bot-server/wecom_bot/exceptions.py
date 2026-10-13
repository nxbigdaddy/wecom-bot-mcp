"""
异常处理模块
"""
from fastapi import HTTPException, status


class WeComBotException(Exception):
    """企业微信机器人基础异常"""
    
    def __init__(self, message: str, error_code: int = 0):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class WeComAPIException(WeComBotException):
    """企业微信 API 调用异常"""
    
    def __init__(self, message: str, error_code: int = 0, errmsg: str = ""):
        self.errmsg = errmsg
        super().__init__(message, error_code)


class ValidationException(WeComBotException):
    """参数验证异常"""
    
    def __init__(self, message: str):
        super().__init__(message, error_code=400)


class FileUploadException(WeComBotException):
    """文件上传异常"""
    
    def __init__(self, message: str):
        super().__init__(message, error_code=500)


def create_http_exception(detail: str, status_code: int = 400) -> HTTPException:
    """创建 HTTP 异常"""
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"X-Error-Code": str(status_code)}
    )
