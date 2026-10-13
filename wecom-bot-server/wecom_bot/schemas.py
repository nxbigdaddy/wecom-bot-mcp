"""
Pydantic 模型定义
用于 API 请求/响应验证
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============ 消息相关模型 ============

class TextMessageRequest(BaseModel):
    """文本消息请求"""
    content: str = Field(..., max_length=4096, description="文本内容")
    mentioned_list: Optional[List[str]] = Field(None, description="@的用户 ID 列表")
    mentioned_mobile_list: Optional[List[str]] = Field(None, description="@的手机号列表")


class TextMessageResponse(BaseModel):
    """文本消息响应"""
    success: bool
    message: str
    error_code: Optional[int] = None


class MarkdownMessageRequest(BaseModel):
    """Markdown 消息请求"""
    content: str = Field(..., description="Markdown 格式内容")


class MarkdownMessageResponse(BaseModel):
    """Markdown 消息响应"""
    success: bool
    message: str
    error_code: Optional[int] = None


class ImageMessageRequest(BaseModel):
    """图片消息请求"""
    base64: str = Field(..., description="图片 base64 编码")
    md5: str = Field(..., description="图片 md5 值")


class ImageMessageResponse(BaseModel):
    """图片消息响应"""
    success: bool
    message: str
    error_code: Optional[int] = None


class NewsArticleRequest(BaseModel):
    """图文文章模型"""
    title: str = Field(..., description="文章标题")
    description: Optional[str] = Field(None, description="文章描述")
    url: str = Field(..., description="文章链接")
    picurl: Optional[str] = Field(None, description="图片链接")


class NewsMessageRequest(BaseModel):
    """图文消息请求"""
    articles: List[NewsArticleRequest] = Field(..., description="文章列表")


class NewsMessageResponse(BaseModel):
    """图文消息响应"""
    success: bool
    message: str
    error_code: Optional[int] = None


class TemplateCardMessageRequest(BaseModel):
    """模板卡片消息请求"""
    card_type: str = Field(..., description="卡片类型")
    card_json: Dict[str, Any] = Field(..., description="卡片内容 JSON")


class TemplateCardMessageResponse(BaseModel):
    """模板卡片消息响应"""
    success: bool
    message: str
    error_code: Optional[int] = None


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    success: bool
    message: str
    media_id: Optional[str] = None
    error_code: Optional[int] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    message: str
    error_code: Optional[int] = None


# ============ 认证相关模型 ============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6, max_length=20)


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: Optional[str]
    role: str
    status: bool
    
    class Config:
        from_attributes = True


# ============ 定时任务相关模型 ============

class ScheduledTaskCreate(BaseModel):
    """创建定时任务请求"""
    name: str
    description: Optional[str] = None
    task_type: str
    message_type: str
    schedule_type: str
    schedule: str
    weekday: Optional[int] = None
    day: Optional[int] = None
    content: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    recipient_type: str = "all"
    recipient_ids: Optional[List[str]] = None


class ScheduledTaskUpdate(BaseModel):
    """更新定时任务请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    message_type: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule: Optional[str] = None
    weekday: Optional[int] = None
    day: Optional[int] = None
    content: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    recipient_type: Optional[str] = None
    recipient_ids: Optional[List[str]] = None
    status: Optional[bool] = None


class ScheduledTaskResponse(BaseModel):
    """定时任务响应"""
    id: int
    name: str
    description: Optional[str]
    task_type: str
    message_type: str
    schedule_type: str
    schedule: str
    weekday: Optional[int]
    day: Optional[int]
    status: bool
    content: Optional[str]
    content_json: Optional[Dict[str, Any]]
    recipient_type: str
    recipient_ids: Optional[List[str]]
    creator_id: int
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    
    class Config:
        from_attributes = True


class TaskExecutionHistoryResponse(BaseModel):
    """任务执行历史响应"""
    id: int
    task_id: int
    scheduled_time: Optional[datetime]
    actual_time: datetime
    status: bool
    message: Optional[str]
    recipients_count: int
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 员工相关模型 ============

class EmployeeCreate(BaseModel):
    """创建员工请求"""
    employee_id: str
    name: str
    gender: Optional[str] = None
    birthday: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    wecom_userid: Optional[str] = None


class EmployeeUpdate(BaseModel):
    """更新员工请求"""
    name: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    wecom_userid: Optional[str] = None
    status: Optional[bool] = None


class EmployeeResponse(BaseModel):
    """员工响应"""
    id: int
    employee_id: str
    name: str
    gender: Optional[str]
    birthday: Optional[str]
    department: Optional[str]
    position: Optional[str]
    hire_date: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    wecom_userid: Optional[str]
    status: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ HR 配置相关模型 ============

class HRConfigCreate(BaseModel):
    """创建 HR 配置请求"""
    system_type: str
    sync_mode: str
    api_url: Optional[str] = None
    api_token: YOUR_SECRET] = None
    db_type: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[str] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: YOUR_PASSWORD] = None
    table_name: Optional[str] = None
    sync_frequency: str = "daily"


class HRConfigUpdate(BaseModel):
    """更新 HR 配置请求"""
    system_type: Optional[str] = None
    sync_mode: Optional[str] = None
    api_url: Optional[str] = None
    api_token: YOUR_SECRET] = None
    db_type: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[str] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: YOUR_PASSWORD] = None
    table_name: Optional[str] = None
    sync_frequency: Optional[str] = None
    status: Optional[bool] = None


class HRConfigResponse(BaseModel):
    """HR 配置响应"""
    id: int
    system_type: str
    sync_mode: str
    api_url: Optional[str]
    api_token: YOUR_SECRET]
    db_type: Optional[str]
    db_host: Optional[str]
    db_port: Optional[str]
    db_name: Optional[str]
    db_user: Optional[str]
    db_password: YOUR_PASSWORD]
    table_name: Optional[str]
    sync_frequency: str
    last_sync: Optional[datetime]
    status: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SyncHistoryResponse(BaseModel):
    """同步历史响应"""
    id: int
    source: str
    added_count: int
    updated_count: int
    deleted_count: int
    status: bool
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 通用响应模型 ============

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    success: bool = True
    data: List[Any]
    total: int
    page: int
    page_size: int
