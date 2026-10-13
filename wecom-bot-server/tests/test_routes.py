"""
API 路由测试
使用 FastAPI TestClient
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from wecom_bot.main import app
from wecom_bot.models import NewsArticleRequest


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_wecom_client():
    """模拟企业微信客户端"""
    with patch('wecom_bot.routes.WeComBotClient') as mock:
        mock_instance = AsyncMock()
        mock_instance.send_text = AsyncMock(return_value={"errcode": 0, "errmsg": "ok"})
        mock_instance.send_markdown = AsyncMock(return_value={"errcode": 0, "errmsg": "ok"})
        mock_instance.send_image = AsyncMock(return_value={"errcode": 0, "errmsg": "ok"})
        mock_instance.send_news = AsyncMock(return_value={"errcode": 0, "errmsg": "ok"})
        mock_instance.send_template_card = AsyncMock(return_value={"errcode": 0, "errmsg": "ok"})
        mock_instance.upload_file = AsyncMock(return_value={"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"})
        mock_instance.get_bot_info = AsyncMock(return_value={
            "webhook_key": "test...",
            "send_url": "test_url",
            "upload_url": "test_url",
            "status": "active"
        })
        mock.return_value = mock_instance
        yield mock_instance


class TestTextMessageAPI:
    """文本消息 API 测试"""
    
    def test_send_text_success(self, client, mock_wecom_client):
        """测试发送文本消息成功"""
        response = client.post(
            "/api/v1/text",
            json={
                "content": "Hello, World!",
                "mentioned_list": ["user1", "user2"],
                "mentioned_mobile_list": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Text message sent successfully" in data["message"]
        mock_wecom_client.send_text.assert_called_once()
    
    def test_send_text_missing_content(self, client):
        """测试缺少内容"""
        response = client.post(
            "/api/v1/text",
            json={"mentioned_list": []}
        )
        
        assert response.status_code == 422  # Validation error


class TestMarkdownMessageAPI:
    """Markdown 消息 API 测试"""
    
    def test_send_markdown_success(self, client, mock_wecom_client):
        """测试发送 Markdown 消息成功"""
        response = client.post(
            "/api/v1/markdown",
            json={"content": "# Hello\n\nThis is **bold** text."}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_wecom_client.send_markdown.assert_called_once()
    
    def test_send_markdown_empty_content(self, client):
        """测试空内容"""
        response = client.post(
            "/api/v1/markdown",
            json={"content": ""}
        )
        
        assert response.status_code == 200  # 空内容允许发送


class TestImageMessageAPI:
    """图片消息 API 测试"""
    
    def test_send_image_success(self, client, mock_wecom_client):
        """测试发送图片消息成功"""
        response = client.post(
            "/api/v1/image",
            json={
                "base64_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "md5": "d41d8cd98f00b204e9800998ecf8427e"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_wecom_client.send_image.assert_called_once()
    
    def test_send_image_invalid_md5(self, client):
        """测试无效 MD5"""
        response = client.post(
            "/api/v1/image",
            json={
                "base64_data": "test",
                "md5": "invalid-md5"
            }
        )
        
        assert response.status_code == 422


class TestNewsMessageAPI:
    """图文消息 API 测试"""
    
    def test_send_news_success(self, client, mock_wecom_client):
        """测试发送图文消息成功"""
        response = client.post(
            "/api/v1/news",
            json={
                "articles": [
                    {
                        "title": "Test Article",
                        "description": "Test Description",
                        "url": "https://example.com",
                        "picurl": "https://example.com/image.jpg"
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_wecom_client.send_news.assert_called_once()
    
    def test_send_news_multiple_articles(self, client, mock_wecom_client):
        """测试发送多篇图文"""
        response = client.post(
            "/api/v1/news",
            json={
                "articles": [
                    {"title": "Article 1", "url": "https://example.com/1"},
                    {"title": "Article 2", "url": "https://example.com/2"},
                    {"title": "Article 3", "url": "https://example.com/3"}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["article_count"] == 3


class TestTemplateCardAPI:
    """模板卡片 API 测试"""
    
    def test_send_template_card_with_url(self, client, mock_wecom_client):
        """测试发送带 URL 的卡片"""
        response = client.post(
            "/api/v1/template-card",
            json={
                "card_type": "text_notice",
                "main_title": "Card Title",
                "main_desc": "Card Description",
                "card_action_type": 1,
                "card_action_url": "https://example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_send_template_card_with_miniprogram(self, client, mock_wecom_client):
        """测试发送带小程序的卡片"""
        response = client.post(
            "/api/v1/template-card",
            json={
                "card_type": "news_notice",
                "main_title": "Card Title",
                "card_action_type": 2,
                "card_action_appid": "wx1234567890",
                "card_action_pagepath": "/pages/index"
            }
        )
        
        assert response.status_code == 200


class TestBotInfoAPI:
    """机器人信息 API 测试"""
    
    def test_get_bot_info(self, client, mock_wecom_client):
        """测试获取机器人信息"""
        response = client.get("/api/v1/bot-info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "webhook_key" in data["data"]


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "WeCom Bot Server"
