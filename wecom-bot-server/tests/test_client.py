"""
客户端测试
使用 mock 服务器模拟企业微信 API
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from httpx import Response

from wecom_bot.client import WeComBotClient
from wecom_bot.exceptions import WeComAPIException, FileUploadException
from wecom_bot.models import NewsArticleRequest


class MockResponse:
    """模拟 HTTP 响应"""
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
    
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")


@pytest.fixture
def mock_success_response():
    """模拟成功响应"""
    return MockResponse(200, {"errcode": 0, "errmsg": "ok"})


@pytest.fixture
def mock_error_response():
    """模拟错误响应"""
    return MockResponse(200, {"errcode": 40001, "errmsg": "invalid token"})


@pytest.fixture
def client():
    """创建客户端实例"""
    return WeComBotClient(webhook_key="test-key")


class TestWeComBotClient:
    """企业微信客户端测试"""
    
    @pytest.mark.asyncio
    async def test_send_text_success(self, client, mock_success_response):
        """测试发送文本消息成功"""
        with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_success_response
            
            result = await client.send_text(
                content="Hello, World!",
                mentioned_list=["user1"],
                mentioned_mobile_list=[]
            )
            
            assert result["errcode"] == 0
            assert result["errmsg"] == "ok"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_text_failure(self, client, mock_error_response):
        """测试发送文本消息失败"""
        with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_error_response
            
            with pytest.raises(WeComAPIException) as exc_info:
                await client.send_text(content="Hello")
            
            assert exc_info.value.error_code == 40001
            assert "invalid token" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_markdown_success(self, client, mock_success_response):
        """测试发送 Markdown 消息成功"""
        with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_success_response
            
            result = await client.send_markdown(content="# Hello")
            
            assert result["errcode"] == 0
            call_args = mock_request.call_args
            assert call_args[1]["json"]["msgtype"] == "markdown"
    
    @pytest.mark.asyncio
    async def test_send_image_success(self, client, mock_success_response):
        """测试发送图片消息成功"""
        with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_success_response
            
            result = await client.send_image(
                base64_data="test_base64",
                md5="d41d8cd98f00b204e9800998ecf8427e"
            )
            
            assert result["errcode"] == 0
            call_args = mock_request.call_args
            assert call_args[1]["json"]["msgtype"] == "image"
    
    @pytest.mark.asyncio
    async def test_send_news_success(self, client, mock_success_response):
        """测试发送图文消息成功"""
        with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_success_response
            
            articles = [
                NewsArticleRequest(
                    title="Test Article",
                    url="https://example.com"
                )
            ]
            
            result = await client.send_news(articles=articles)
            
            assert result["errcode"] == 0
            call_args = mock_request.call_args
            assert call_args[1]["json"]["msgtype"] == "news"
            assert len(call_args[1]["json"]["news"]["articles"]) == 1
    
    @pytest.mark.asyncio
    async def test_send_template_card_success(self, client, mock_success_response):
        """测试发送模板卡片成功"""
        with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_success_response
            
            result = await client.send_template_card(
                card_type="text_notice",
                main_title="Title",
                main_desc="Description",
                card_action_type=1,
                card_action_url="https://example.com"
            )
            
            assert result["errcode"] == 0
            call_args = mock_request.call_args
            assert call_args[1]["json"]["msgtype"] == "template_card"
    
    @pytest.mark.asyncio
    async def test_get_bot_info(self, client):
        """测试获取机器人信息"""
        info = await client.get_bot_info()
        
        assert "webhook_key" in info
        assert "send_url" in info
        assert "upload_url" in info
        assert info["status"] == "active"
        assert "test-key" in info["webhook_key"]


class TestFileUpload:
    """文件上传测试"""
    
    @pytest.mark.asyncio
    async def test_upload_file_not_found(self, client):
        """测试文件不存在"""
        with pytest.raises(FileUploadException) as exc_info:
            await client.upload_file("/nonexistent/file.txt")
        
        assert "File not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, client, tmp_path, mock_success_response):
        """测试文件上传成功"""
        # 创建临时文件
        temp_file = tmp_path / "test.txt"
        temp_file.write_text("Test content")
        
        with patch('httpx.AsyncClient.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_success_response
            mock_success_response._json_data = {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"}
            
            result = await client.upload_file(str(temp_file))
            
            assert result["errcode"] == 0
            assert result.get("media_id") == "test_media_id"
