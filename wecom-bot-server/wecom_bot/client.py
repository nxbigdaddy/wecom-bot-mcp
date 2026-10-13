"""
企业微信机器人客户端
负责与企业微信 API 交互
"""
import httpx
import aiofiles
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config import settings
from .exceptions import WeComAPIException, FileUploadException
from .schemas import NewsArticleRequest


class WeComBotClient:
    """企业微信机器人客户端"""
    
    def __init__(self, webhook_key: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            webhook_key: Webhook Key，如果不传则使用配置文件的值
        """
        self.webhook_key = webhook_key or settings.wecom_bot_webhook_key
        self.base_url = settings.wecom_bot_base_url
        self.send_url = f"{self.base_url}/send?key={self.webhook_key}"
        self.upload_url = f"{self.base_url}/upload_media?key={self.webhook_key}"
    
    async def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            url: 请求 URL
            **kwargs: 其他参数
            
        Returns:
            响应数据
            
        Raises:
            WeComAPIException: API 调用失败时抛出
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                result = response.json()
                
                # 检查错误码
                errcode = result.get('errcode', 0)
                if errcode != 0:
                    errmsg = result.get('errmsg', 'Unknown error')
                    raise WeComAPIException(
                        message=f"WeCom API error: {errmsg}",
                        error_code=errcode,
                        errmsg=errmsg
                    )
                
                return result
            except httpx.HTTPError as e:
                raise WeComAPIException(
                    message=f"HTTP request failed: {str(e)}",
                    error_code=-1
                )
            except httpx.TimeoutException as e:
                raise WeComAPIException(
                    message=f"Request timeout: {str(e)}",
                    error_code=-2
                )
    
    async def send_text(
        self,
        content: str,
        mentioned_list: Optional[List[str]] = None,
        mentioned_mobile_list: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            content: 文本内容
            mentioned_list: 需要@的用户 ID 列表
            mentioned_mobile_list: 需要@的手机号列表
            
        Returns:
            API 响应数据
        """
        payload = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or [],
                "mentioned_mobile_list": mentioned_mobile_list or []
            }
        }
        
        return await self._request("POST", self.send_url, json=payload)
    
    async def send_markdown(self, content: str) -> Dict[str, Any]:
        """
        发送 Markdown 消息
        
        Args:
            content: Markdown 内容
            
        Returns:
            API 响应数据
        """
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        return await self._request("POST", self.send_url, json=payload)
    
    async def send_image(self, base64_data: str, md5: str) -> Dict[str, Any]:
        """
        发送图片消息
        
        Args:
            base64_data: Base64 编码的图片数据
            md5: 图片的 MD5 哈希值
            
        Returns:
            API 响应数据
        """
        payload = {
            "msgtype": "image",
            "image": {
                "base64": base64_data,
                "md5": md5
            }
        }
        
        return await self._request("POST", self.send_url, json=payload)
    
    async def send_news(self, articles: List[NewsArticleRequest]) -> Dict[str, Any]:
        """
        发送图文消息
        
        Args:
            articles: 图文文章列表
            
        Returns:
            API 响应数据
        """
        articles_data = [
            {
                "title": article.title,
                "description": article.description,
                "url": article.url,
                "picurl": article.picurl
            }
            for article in articles
        ]
        
        payload = {
            "msgtype": "news",
            "news": {
                "articles": articles_data
            }
        }
        
        return await self._request("POST", self.send_url, json=payload)
    
    async def send_template_card(
        self,
        card_type: str,
        main_title: str,
        main_desc: str,
        card_action_type: int,
        card_action_url: str = "",
        card_action_appid: str = "",
        card_action_pagepath: str = ""
    ) -> Dict[str, Any]:
        """
        发送模板卡片消息
        
        Args:
            card_type: 卡片类型
            main_title: 主标题
            main_desc: 主描述
            card_action_type: 卡片动作类型
            card_action_url: 动作 URL
            card_action_appid: 小程序 AppID
            card_action_pagepath: 小程序页面路径
            
        Returns:
            API 响应数据
        """
        card_action = {
            "type": card_action_type
        }
        
        if card_action_type == 1:  # OPEN_URL
            if card_action_url:
                card_action["url"] = card_action_url
        elif card_action_type == 2:  # OPEN_MINI_PROGRAM
            if card_action_appid:
                card_action["appid"] = card_action_appid
            if card_action_pagepath:
                card_action["pagepath"] = card_action_pagepath
        
        payload = {
            "msgtype": "template_card",
            "template_card": {
                "card_type": card_type,
                "main_title": {
                    "title": main_title,
                    "desc": main_desc
                },
                "card_action": card_action
            }
        }
        
        return await self._request("POST", self.send_url, json=payload)
    
    async def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        上传文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            API 响应数据，包含 media_id
            
        Raises:
            FileUploadException: 文件上传失败时抛出
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileUploadException(f"File not found: {file_path}")
        
        # 检查文件扩展名
        if path.suffix.lower() not in settings.allowed_file_extensions:
            raise FileUploadException(
                f"File type not allowed. Allowed types: {settings.allowed_file_extensions}"
            )
        
        # 检查文件大小
        file_size = path.stat().st_size
        if file_size > settings.max_file_size:
            raise FileUploadException(
                f"File size exceeds limit ({file_size} > {settings.max_file_size})"
            )
        
        try:
            # 使用 multipart/form-data 上传
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            files = {
                'media': (path.name, file_content, 'application/octet-stream')
            }
            
            result = await self._request(
                "POST",
                f"{self.upload_url}&type=file",
                files=files
            )
            
            return result
        except FileNotFoundError:
            raise FileUploadException(f"File not found: {file_path}")
        except Exception as e:
            raise FileUploadException(f"Upload failed: {str(e)}")
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """
        获取机器人信息（用于测试连接）
        
        Returns:
            包含 Webhook 信息的字典
        """
        return {
            "webhook_key": self.webhook_key[:8] + "..." if len(self.webhook_key) > 8 else self.webhook_key,
            "send_url": self.send_url,
            "upload_url": self.upload_url,
            "status": "active"
        }
