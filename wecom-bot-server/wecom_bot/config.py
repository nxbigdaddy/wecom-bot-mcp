"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 企业微信机器人配置
    wecom_bot_webhook_key: str
    wecom_bot_base_url: str = "https://qyapi.weixin.qq.com/cgi-bin/webhook"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    # WebSocket 配置
    websocket_heartbeat_interval: int = 30  # 心跳间隔（秒）
    
    # JWT 配置
    jwt_secret_key: str = "your-secret-key-change-in-production"
    
    # 请求限制配置
    max_message_length: int = 4096  # 最大消息长度
    max_mentioned_count: int = 100  # 最大@人数
    max_news_articles: int = 10  # 最大图文数量
    
    # 文件上传配置
    max_file_size: int = 20 * 1024 * 1024  # 20MB
    allowed_file_extensions: set = {".txt", ".log", ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def webhook_send_url(self) -> str:
        """获取消息发送 URL"""
        return f"{self.wecom_bot_base_url}/send?key={self.wecom_bot_webhook_key}"
    
    @property
    def webhook_upload_url(self) -> str:
        """获取文件上传 URL"""
        return f"{self.wecom_bot_base_url}/upload_media?key={self.wecom_bot_webhook_key}"


# 全局配置实例
settings = Settings()
