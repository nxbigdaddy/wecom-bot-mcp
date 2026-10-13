"""
REST API 路由定义
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import hashlib
import base64

from .client import WeComBotClient
from .schemas import (
    TextMessageRequest, TextMessageResponse,
    MarkdownMessageRequest, MarkdownMessageResponse,
    ImageMessageRequest, ImageMessageResponse,
    NewsMessageRequest, NewsMessageResponse,
    TemplateCardMessageRequest, TemplateCardMessageResponse,
    FileUploadResponse, ErrorResponse
)
from .exceptions import WeComAPIException, FileUploadException, create_http_exception
from .config import settings

router = APIRouter(prefix="/api/v1", tags=["messages"])


def get_client() -> WeComBotClient:
    """获取客户端实例"""
    return WeComBotClient()


@router.post("/text", response_model=TextMessageResponse, summary="发送文本消息")
async def send_text(request: TextMessageRequest):
    """
    发送文本消息到企业微信群
    
    - **content**: 文本内容（必填，最大 4096 字符）
    - **mentioned_list**: 需要@的用户 ID 列表（可选）
    - **mentioned_mobile_list**: 需要@的手机号列表（可选）
    
    示例：
    ```json
    {
        "content": "这是一条测试消息",
        "mentioned_list": ["user1", "user2"],
        "mentioned_mobile_list": ["13800138000"]
    }
    ```
    """
    try:
        client = get_client()
        await client.send_text(
            content=request.content,
            mentioned_list=request.mentioned_list,
            mentioned_mobile_list=request.mentioned_mobile_list
        )
        return TextMessageResponse(
            success=True,
            message="Text message sent successfully",
            data={"content": request.content}
        )
    except WeComAPIException as e:
        return TextMessageResponse(
            success=False,
            message=f"Failed to send text message: {e.message}",
            error_code=e.error_code
        )


@router.post("/markdown", response_model=MarkdownMessageResponse, summary="发送 Markdown 消息")
async def send_markdown(request: MarkdownMessageRequest):
    """
    发送 Markdown 消息到企业微信群
    
    - **content**: Markdown 内容（必填，最大 4096 字符）
    
    支持的 Markdown 语法：
    - 标题：`# 一级标题`
    - 粗体：`**粗体**`
    - 斜体：`*斜体*`
    - 链接：`[文本](链接)`
    - 代码：`` `代码` ``
    - 引用：`> 引用`
    - 列表：`- 列表项`
    """
    try:
        client = get_client()
        await client.send_markdown(content=request.content)
        return MarkdownMessageResponse(
            success=True,
            message="Markdown message sent successfully",
            data={"content": request.content}
        )
    except WeComAPIException as e:
        return MarkdownMessageResponse(
            success=False,
            message=f"Failed to send markdown message: {e.message}",
            error_code=e.error_code
        )


@router.post("/image", response_model=ImageMessageResponse, summary="发送图片消息")
async def send_image(request: ImageMessageRequest):
    """
    发送图片消息到企业微信群
    
    - **base64_data**: Base64 编码的图片数据（必填）
    - **md5**: 图片的 MD5 哈希值（必填，32 位十六进制）
    
    示例：
    ```json
    {
        "base64_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "md5": "d41d8cd98f00b204e9800998ecf8427e"
    }
    ```
    """
    try:
        client = get_client()
        await client.send_image(
            base64_data=request.base64_data,
            md5=request.md5
        )
        return ImageMessageResponse(
            success=True,
            message="Image message sent successfully",
            data={"md5": request.md5}
        )
    except WeComAPIException as e:
        return ImageMessageResponse(
            success=False,
            message=f"Failed to send image message: {e.message}",
            error_code=e.error_code
        )


@router.post("/news", response_model=NewsMessageResponse, summary="发送图文消息")
async def send_news(request: NewsMessageRequest):
    """
    发送图文消息到企业微信群
    
    - **articles**: 图文文章列表（必填，最多 10 篇）
        - **title**: 文章标题（必填，最大 128 字符）
        - **description**: 文章描述（可选，最大 512 字符）
        - **url**: 文章链接（必填）
        - **picurl**: 图片链接（可选）
    
    示例：
    ```json
    {
        "articles": [
            {
                "title": "标题 1",
                "description": "描述 1",
                "url": "https://example.com/1",
                "picurl": "https://example.com/image1.jpg"
            }
        ]
    }
    ```
    """
    try:
        client = get_client()
        await client.send_news(articles=request.articles)
        return NewsMessageResponse(
            success=True,
            message="News message sent successfully",
            data={"article_count": len(request.articles)}
        )
    except WeComAPIException as e:
        return NewsMessageResponse(
            success=False,
            message=f"Failed to send news message: {e.message}",
            error_code=e.error_code
        )


@router.post("/template-card", response_model=TemplateCardMessageResponse, summary="发送模板卡片消息")
async def send_template_card(request: TemplateCardMessageRequest):
    """
    发送模板卡片消息到企业微信群
    
    - **card_type**: 卡片类型（必填，如 text_notice, news_notice）
    - **main_title**: 主标题（必填，最大 128 字符）
    - **main_desc**: 主描述（可选，最大 512 字符）
    - **card_action_type**: 卡片动作类型（必填，1=打开 URL，2=打开小程序）
    - **card_action_url**: 动作 URL（可选，当类型为 1 时）
    - **card_action_appid**: 小程序 AppID（可选，当类型为 2 时）
    - **card_action_pagepath**: 小程序页面路径（可选，当类型为 2 时）
    
    示例：
    ```json
    {
        "card_type": "text_notice",
        "main_title": "卡片标题",
        "main_desc": "卡片描述",
        "card_action_type": 1,
        "card_action_url": "https://example.com"
    }
    ```
    """
    try:
        client = get_client()
        await client.send_template_card(
            card_type=request.card_type,
            main_title=request.main_title,
            main_desc=request.main_desc,
            card_action_type=request.card_action_type,
            card_action_url=request.card_action_url,
            card_action_appid=request.card_action_appid,
            card_action_pagepath=request.card_action_pagepath
        )
        return TemplateCardMessageResponse(
            success=True,
            message="Template card message sent successfully",
            data={"card_type": request.card_type}
        )
    except WeComAPIException as e:
        return TemplateCardMessageResponse(
            success=False,
            message=f"Failed to send template card message: {e.message}",
            error_code=e.error_code
        )


@router.post("/upload-file", response_model=FileUploadResponse, summary="上传文件")
async def upload_file(file_path: str):
    """
    上传文件到企业微信
    
    - **file_path**: 文件路径（必填）
    
    支持的文件类型：
    - 文档：.txt, .log, .pdf, .doc, .docx, .xls, .xlsx
    - 图片：.jpg, .jpeg, .png, .gif
    
    文件大小限制：20MB
    
    示例：
    ```json
    {
        "file_path": "/path/to/your/file.txt"
    }
    ```
    """
    try:
        client = get_client()
        result = await client.upload_file(file_path=file_path)
        return FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            data={"media_id": result.get("media_id", "")}
        )
    except FileUploadException as e:
        return FileUploadResponse(
            success=False,
            message=f"Failed to upload file: {e.message}",
            error_code=e.error_code
        )
    except WeComAPIException as e:
        return FileUploadResponse(
            success=False,
            message=f"Failed to upload file: {e.message}",
            error_code=e.error_code
        )


@router.get("/bot-info", summary="获取机器人信息")
async def get_bot_info():
    """
    获取当前机器人的配置信息
    
    返回：
    - webhook_key: Webhook Key（脱敏显示）
    - send_url: 消息发送地址
    - upload_url: 文件上传地址
    - status: 状态
    """
    client = get_client()
    info = await client.get_bot_info()
    return {
        "success": True,
        "data": info
    }
