"""
WebSocket 处理器
支持实时双向通信
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect, status
import uuid

from .client import WeComBotClient
from .schemas import (
    TextMessageRequest, MarkdownMessageRequest, ImageMessageRequest,
    NewsMessageRequest, TemplateCardMessageRequest
)
from .exceptions import WeComAPIException, WeComBotException
from .config import settings

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, connection_id: str) -> bool:
        """
        接受 WebSocket 连接
        
        Args:
            websocket: WebSocket 对象
            connection_id: 连接 ID
            
        Returns:
            是否连接成功
        """
        try:
            await websocket.accept()
            async with self._lock:
                self.active_connections[connection_id] = websocket
            logger.info(f"WebSocket connected: {connection_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to accept WebSocket connection: {e}")
            return False
    
    async def disconnect(self, connection_id: str):
        """
        断开 WebSocket 连接
        
        Args:
            connection_id: 连接 ID
        """
        async with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: dict) -> bool:
        """
        发送消息到指定连接
        
        Args:
            connection_id: 连接 ID
            message: 消息字典
            
        Returns:
            是否发送成功
        """
        if connection_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            return False
    
    async def broadcast(self, message: dict):
        """
        广播消息到所有连接
        
        Args:
            message: 消息字典
        """
        async with self._lock:
            connections = list(self.active_connections.values())
        
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)


# 全局 WebSocket 管理器
ws_manager = WebSocketManager()


class WSMessageHandler:
    """WebSocket 消息处理器"""
    
    def __init__(self, connection_id: str, websocket: WebSocket):
        self.connection_id = connection_id
        self.websocket = websocket
        self.client = WeComBotClient()
    
    async def handle_message(self, message: dict) -> dict:
        """
        处理接收到的消息
        
        Args:
            message: 消息字典
            
        Returns:
            响应字典
        """
        msg_type = message.get("type", "")
        data = message.get("data", {})
        request_id = message.get("request_id", str(uuid.uuid4()))
        
        try:
            if msg_type == "text":
                return await self._handle_text(data, request_id)
            elif msg_type == "markdown":
                return await self._handle_markdown(data, request_id)
            elif msg_type == "image":
                return await self._handle_image(data, request_id)
            elif msg_type == "news":
                return await self._handle_news(data, request_id)
            elif msg_type == "template_card":
                return await self._handle_template_card(data, request_id)
            elif msg_type == "ping":
                return {"success": True, "message": "pong", "request_id": request_id}
            else:
                return {
                    "success": False,
                    "message": f"Unknown message type: {msg_type}",
                    "request_id": request_id
                }
        except WeComAPIException as e:
            logger.error(f"WeCom API error: {e.message}")
            return {
                "success": False,
                "message": e.message,
                "error_code": e.error_code,
                "request_id": request_id
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "message": str(e),
                "request_id": request_id
            }
    
    async def _handle_text(self, data: dict, request_id: str) -> dict:
        """处理文本消息"""
        content = data.get("content", "")
        mentioned_list = data.get("mentioned_list", [])
        mentioned_mobile_list = data.get("mentioned_mobile_list", [])
        
        if not content:
            raise WeComBotException("Content is required")
        
        await self.client.send_text(
            content=content,
            mentioned_list=mentioned_list,
            mentioned_mobile_list=mentioned_mobile_list
        )
        
        return {
            "success": True,
            "message": "Text message sent successfully",
            "request_id": request_id,
            "data": {"content": content}
        }
    
    async def _handle_markdown(self, data: dict, request_id: str) -> dict:
        """处理 Markdown 消息"""
        content = data.get("content", "")
        
        if not content:
            raise WeComBotException("Content is required")
        
        await self.client.send_markdown(content=content)
        
        return {
            "success": True,
            "message": "Markdown message sent successfully",
            "request_id": request_id,
            "data": {"content": content}
        }
    
    async def _handle_image(self, data: dict, request_id: str) -> dict:
        """处理图片消息"""
        base64_data = data.get("base64_data", "")
        md5 = data.get("md5", "")
        
        if not base64_data or not md5:
            raise WeComBotException("base64_data and md5 are required")
        
        await self.client.send_image(base64_data=base64_data, md5=md5)
        
        return {
            "success": True,
            "message": "Image message sent successfully",
            "request_id": request_id,
            "data": {"md5": md5}
        }
    
    async def _handle_news(self, data: dict, request_id: str) -> dict:
        """处理图文消息"""
        articles_data = data.get("articles", [])
        
        if not articles_data:
            raise WeComBotException("articles are required")
        
        articles = [
            {
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "picurl": a.get("picurl", "")
            }
            for a in articles_data
        ]
        
        # 转换为 NewsArticleRequest 对象
        from .models import NewsArticleRequest
        articles_request = [NewsArticleRequest(**article) for article in articles if article.get("title") and article.get("url")]
        
        await self.client.send_news(articles=articles_request)
        
        return {
            "success": True,
            "message": "News message sent successfully",
            "request_id": request_id,
            "data": {"article_count": len(articles_request)}
        }
    
    async def _handle_template_card(self, data: dict, request_id: str) -> dict:
        """处理模板卡片消息"""
        card_type = data.get("card_type", "")
        main_title = data.get("main_title", "")
        main_desc = data.get("main_desc", "")
        card_action_type = data.get("card_action_type", 1)
        card_action_url = data.get("card_action_url", "")
        card_action_appid = data.get("card_action_appid", "")
        card_action_pagepath = data.get("card_action_pagepath", "")
        
        if not card_type or not main_title:
            raise WeComBotException("card_type and main_title are required")
        
        await self.client.send_template_card(
            card_type=card_type,
            main_title=main_title,
            main_desc=main_desc,
            card_action_type=card_action_type,
            card_action_url=card_action_url,
            card_action_appid=card_action_appid,
            card_action_pagepath=card_action_pagepath
        )
        
        return {
            "success": True,
            "message": "Template card message sent successfully",
            "request_id": request_id,
            "data": {"card_type": card_type}
        }


async def websocket_handler(websocket: WebSocket):
    """
    WebSocket 连接处理器
    
    Args:
        websocket: WebSocket 对象
    """
    connection_id = str(uuid.uuid4())
    
    # 连接
    if not await ws_manager.connect(websocket, connection_id):
        return
    
    # 发送欢迎消息
    await ws_manager.send_message(connection_id, {
        "success": True,
        "message": "Connected to WeCom Bot Server",
        "connection_id": connection_id
    })
    
    handler = WSMessageHandler(connection_id, websocket)
    
    try:
        while True:
            # 接收消息
            try:
                data = await websocket.receive_json()
            except json.JSONDecodeError:
                await ws_manager.send_message(connection_id, {
                    "success": False,
                    "message": "Invalid JSON format"
                })
                continue
            
            # 处理消息
            response = await handler.handle_message(data)
            
            # 发送响应
            await ws_manager.send_message(connection_id, response)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection_id)


async def heartbeat_checker(websocket: WebSocket, connection_id: str):
    """
    心跳检测
    
    Args:
        websocket: WebSocket 对象
        connection_id: 连接 ID
    """
    try:
        while True:
            await asyncio.sleep(settings.websocket_heartbeat_interval)
            try:
                await websocket.send_json({
                    "type": "ping",
                    "data": {"timestamp": asyncio.get_event_loop().time()}
                })
            except Exception:
                break
    except asyncio.CancelledError:
        pass
