"""
配置测试
"""
import pytest
from wecom_bot.config import Settings


def test_settings_creation():
    """测试配置创建"""
    settings = Settings(
        wecom_bot_webhook_key="test-key-12345"
    )
    
    assert settings.wecom_bot_webhook_key == "test-key-12345"
    assert settings.wecom_bot_base_url == "https://qyapi.weixin.qq.com/cgi-bin/webhook"
    assert settings.port == 8000


def test_settings_urls():
    """测试 URL 生成"""
    settings = Settings(
        wecom_bot_webhook_key="test-key"
    )
    
    assert settings.webhook_send_url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key"
    assert settings.webhook_upload_url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=test-key"


def test_settings_validation():
    """测试配置验证"""
    # 测试缺少必需的字段
    with pytest.raises(Exception):
        Settings()
