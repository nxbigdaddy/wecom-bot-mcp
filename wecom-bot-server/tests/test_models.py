"""
模型测试
"""
import pytest
from pydantic import ValidationError
from wecom_bot.models import (
    TextMessageRequest, MarkdownMessageRequest, ImageMessageRequest,
    NewsArticleRequest, NewsMessageRequest, TemplateCardMessageRequest,
    CardActionType
)


class TestTextMessageRequest:
    """文本消息请求测试"""
    
    def test_valid_request(self):
        """测试有效的请求"""
        request = TextMessageRequest(
            content="Hello, World!",
            mentioned_list=["user1", "user2"],
            mentioned_mobile_list=["13800138000"]
        )
        
        assert request.content == "Hello, World!"
        assert len(request.mentioned_list) == 2
        assert len(request.mentioned_mobile_list) == 1
    
    def test_minimal_request(self):
        """测试最小请求"""
        request = TextMessageRequest(content="Hello")
        
        assert request.content == "Hello"
        assert request.mentioned_list == []
        assert request.mentioned_mobile_list == []
    
    def test_content_too_long(self):
        """测试内容过长"""
        with pytest.raises(ValidationError):
            TextMessageRequest(content="x" * 5000)
    
    def test_too_many_mentioned(self):
        """测试@人数过多"""
        with pytest.raises(ValidationError):
            TextMessageRequest(
                content="Hello",
                mentioned_list=[f"user{i}" for i in range(101)]
            )


class TestMarkdownMessageRequest:
    """Markdown 消息请求测试"""
    
    def test_valid_request(self):
        """测试有效的请求"""
        request = MarkdownMessageRequest(
            content="# Hello\n\nThis is **bold** text."
        )
        
        assert "# Hello" in request.content
    
    def test_empty_content(self):
        """测试空内容"""
        request = MarkdownMessageRequest(content="")
        assert request.content == ""


class TestImageMessageRequest:
    """图片消息请求测试"""
    
    def test_valid_request(self):
        """测试有效的请求"""
        request = ImageMessageRequest(
            base64_data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            md5="d41d8cd98f00b204e9800998ecf8427e"
        )
        
        assert "iVBORw0" in request.base64_data
        assert len(request.md5) == 32
    
    def test_invalid_md5_format(self):
        """测试无效的 MD5 格式"""
        with pytest.raises(ValidationError):
            ImageMessageRequest(
                base64_data="test",
                md5="invalid-md5"
            )


class TestNewsArticleRequest:
    """图文文章请求测试"""
    
    def test_valid_request(self):
        """测试有效的请求"""
        request = NewsArticleRequest(
            title="Test Article",
            description="Test Description",
            url="https://example.com",
            picurl="https://example.com/image.jpg"
        )
        
        assert request.title == "Test Article"
        assert request.url == "https://example.com"
    
    def test_required_fields(self):
        """测试必需字段"""
        # 缺少 url 应该失败
        with pytest.raises(ValidationError):
            NewsArticleRequest(
                title="Test",
                description="Test"
            )


class TestNewsMessageRequest:
    """图文消息请求测试"""
    
    def test_valid_request(self):
        """测试有效的请求"""
        request = NewsMessageRequest(
            articles=[
                NewsArticleRequest(
                    title="Article 1",
                    url="https://example.com/1"
                ),
                NewsArticleRequest(
                    title="Article 2",
                    url="https://example.com/2"
                )
            ]
        )
        
        assert len(request.articles) == 2
    
    def test_too_many_articles(self):
        """测试文章数量过多"""
        with pytest.raises(ValidationError):
            NewsMessageRequest(
                articles=[
                    NewsArticleRequest(title=f"Article {i}", url=f"https://example.com/{i}")
                    for i in range(11)
                ]
            )


class TestTemplateCardMessageRequest:
    """模板卡片消息请求测试"""
    
    def test_valid_request_with_url(self):
        """测试带 URL 的有效请求"""
        request = TemplateCardMessageRequest(
            card_type="text_notice",
            main_title="Card Title",
            main_desc="Card Description",
            card_action_type=CardActionType.OPEN_URL,
            card_action_url="https://example.com"
        )
        
        assert request.card_type == "text_notice"
        assert request.card_action_type == 1
    
    def test_valid_request_with_miniprogram(self):
        """测试带小程序的有效请求"""
        request = TemplateCardMessageRequest(
            card_type="news_notice",
            main_title="Card Title",
            card_action_type=CardActionType.OPEN_MINI_PROGRAM,
            card_action_appid="wx1234567890",
            card_action_pagepath="/pages/index"
        )
        
        assert request.card_action_type == 2
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        with pytest.raises(ValidationError):
            TemplateCardMessageRequest(
                main_title="Title"
                # 缺少 card_type 和 card_action_type
            )
