# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: 环境变量配置（无需在请求中传递）
- **数据格式**: JSON
- **字符编码**: UTF-8

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| -1 | HTTP 请求失败 |
| -2 | 请求超时 |
| 40001 | 无效的 token |
| 40002 | 参数错误 |
| 40003 | 无效的 webhook key |
| 40004 | 消息类型不支持 |
| 40005 | 消息内容过长 |
| 40006 | 频率限制 |

## 请求示例

### 1. 文本消息

```bash
curl -X POST http://localhost:8000/api/v1/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "这是一条测试消息",
    "mentioned_list": ["user1", "user2"],
    "mentioned_mobile_list": ["13800138000"]
  }'
```

### 2. Markdown 消息

```bash
curl -X POST http://localhost:8000/api/v1/markdown \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# 这是一条测试消息\n\n## 重要通知\n\n请**注意**以下事项：\n\n- 事项 1\n- 事项 2\n- 事项 3\n\n[查看详情](https://example.com)"
  }'
```

### 3. 图片消息

```bash
# 先计算图片的 MD5
md5sum image.png

# 发送图片
curl -X POST http://localhost:8000/api/v1/image \
  -H "Content-Type: application/json" \
  -d '{
    "base64_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "md5": "d41d8cd98f00b204e9800998ecf8427e"
  }'
```

### 4. 图文消息

```bash
curl -X POST http://localhost:8000/api/v1/news \
  -H "Content-Type: application/json" \
  -d '{
    "articles": [
      {
        "title": "产品发布 | 我们发布了新产品",
        "description": "详细介绍我们的最新产品功能和特性",
        "url": "https://example.com/product-launch",
        "picurl": "https://example.com/images/product.jpg"
      },
      {
        "title": "技术分享 | 架构设计最佳实践",
        "description": "分享我们在架构设计方面的经验和最佳实践",
        "url": "https://example.com/tech-sharing",
        "picurl": "https://example.com/images/tech.jpg"
      }
    ]
  }'
```

### 5. 模板卡片消息

```bash
# 类型 1：打开 URL
curl -X POST http://localhost:8000/api/v1/template-card \
  -H "Content-Type: application/json" \
  -d '{
    "card_type": "text_notice",
    "main_title": "会议通知",
    "main_desc": "明天上午 10 点召开项目启动会",
    "card_action_type": 1,
    "card_action_url": "https://example.com/meeting"
  }'

# 类型 2：打开小程序
curl -X POST http://localhost:8000/api/v1/template-card \
  -H "Content-Type: application/json" \
  -d '{
    "card_type": "news_notice",
    "main_title": "打卡任务",
    "main_desc": "完成今日打卡任务",
    "card_action_type": 2,
    "card_action_appid": "wx1234567890",
    "card_action_pagepath": "/pages/checkin/index"
  }'
```

### 6. 文件上传

```bash
curl -X POST "http://localhost:8000/api/v1/upload-file?file_path=/path/to/file.txt"
```

## WebSocket 示例

### JavaScript 完整示例

```javascript
class WeComBotClient {
  constructor(url = 'ws://localhost:8000/ws') {
    this.url = url;
    this.ws = null;
    this.reconnectInterval = 5000;
    this.heartbeatInterval = null;
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('Connected to WeCom Bot Server');
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      console.log('Received:', response);
      this.handleMessage(response);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Disconnected, reconnecting...');
      this.stopHeartbeat();
      setTimeout(() => this.connect(), this.reconnectInterval);
    };
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, 30000);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  sendText(content, mentionedList = []) {
    this.send({
      type: 'text',
      data: {
        content,
        mentioned_list: mentionedList
      }
    });
  }

  sendMarkdown(content) {
    this.send({
      type: 'markdown',
      data: { content }
    });
  }

  sendImage(base64Data, md5) {
    this.send({
      type: 'image',
      data: {
        base64_data: base64Data,
        md5: md5
      }
    });
  }

  sendNews(articles) {
    this.send({
      type: 'news',
      data: { articles }
    });
  }

  sendTemplateCard(config) {
    this.send({
      type: 'template_card',
      data: config
    });
  }

  handleMessage(response) {
    // 处理响应
    if (response.type === 'pong') {
      console.log('Heartbeat OK');
      return;
    }

    if (response.success) {
      console.log('Message sent successfully:', response.message);
    } else {
      console.error('Message failed:', response.message);
    }
  }

  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// 使用示例
const client = new WeComBotClient();
client.connect();

// 发送文本消息
setTimeout(() => {
  client.sendText('Hello from WebSocket!', ['user1']);
}, 1000);

// 发送 Markdown 消息
setTimeout(() => {
  client.sendMarkdown('# Hello\n\nThis is **bold** text.');
}, 2000);
```

### Python 示例（使用 websockets 库）

```python
import asyncio
import websockets
import json

async def main():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # 发送文本消息
        await websocket.send(json.dumps({
            "type": "text",
            "data": {
                "content": "Hello from Python!",
                "mentioned_list": ["user1"]
            }
        }))
        
        # 接收响应
        response = await websocket.recv()
        print(f"Response: {response}")
        
        # 发送 Markdown 消息
        await websocket.send(json.dumps({
            "type": "markdown",
            "data": {
                "content": "# Hello from Python!\n\n**WebSocket** is awesome."
            }
        }))
        
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.run(main())
```

## SDK 示例

### Python SDK（待实现）

```python
from wecom_bot_sdk import WeComBot

# 初始化客户端
client = WeComBot(base_url='http://localhost:8000')

# 发送文本消息
result = client.send_text(
    content='Hello!',
    mentioned_list=['user1']
)
print(result)

# 发送 Markdown 消息
result = client.send_markdown(
    content='# Hello\n\n**Bold** text'
)
print(result)

# 发送图文消息
result = client.send_news([
    {
        'title': 'Title 1',
        'url': 'https://example.com/1',
        'picurl': 'https://example.com/img1.jpg'
    }
])
print(result)
```

### Node.js SDK（待实现）

```javascript
const { WeComBot } = require('wecom-bot-sdk');

const client = new WeComBot({
  baseUrl: 'http://localhost:8000'
});

// 发送文本消息
const result = await client.sendText({
  content: 'Hello!',
  mentionedList: ['user1']
});
console.log(result);

// 发送 Markdown 消息
const markdownResult = await client.sendMarkdown({
  content: '# Hello\n\n**Bold** text'
});
console.log(markdownResult);
```

## 最佳实践

### 1. 错误处理

```python
import httpx

def send_message_with_retry(content, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = httpx.post(
                "http://localhost:8000/api/v1/text",
                json={"content": content},
                timeout=10.0
            )
            result = response.json()
            
            if result.get("success"):
                return result
            
            # 根据错误码决定是否重试
            error_code = result.get("error_code", 0)
            if error_code in [40001, 40003]:  # token 错误，不重试
                raise Exception(f"Authentication failed: {result.get('message')}")
                
        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
    
    raise Exception("Max retries exceeded")
```

### 2. 批量发送

```python
import asyncio
import httpx

async def batch_send_messages(messages):
    async with httpx.AsyncClient() as client:
        tasks = []
        for message in messages:
            task = client.post(
                "http://localhost:8000/api/v1/text",
                json={"content": message}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append({"success": False, "error": str(response)})
            else:
                results.append(response.json())
        
        return results

# 使用
messages = [f"Message {i}" for i in range(10)]
results = asyncio.run(batch_send_messages(messages))
```

### 3. 限流处理

```python
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=20, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        now = datetime.now()
        # 移除超出时间窗口的请求
        self.requests = [
            req for req in self.requests
            if now - req < timedelta(seconds=self.time_window)
        ]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0]).seconds
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)

# 使用
limiter = RateLimiter(max_requests=20, time_window=60)

async def send_with_rate_limit(content):
    await limiter.acquire()
    return await send_message(content)
```

---

**文档版本**: 1.0.0  
**最后更新**: 2026-03-16
