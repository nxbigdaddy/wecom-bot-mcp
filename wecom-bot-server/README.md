# WeCom Bot Server

企业微信机器人服务器 - 基于 Python FastAPI 实现，支持 REST API 和 WebSocket 双模式通信。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 目录

- [功能特性](#-功能特性)
- [快速开始](#-快速开始)
- [API 接口说明](#-api-接口说明)
- [WebSocket 使用](#-websocket-使用)
- [部署指南](#-部署指南)
- [配置说明](#-配置说明)
- [测试](#-测试)
- [示例代码](#-示例代码)
- [常见问题](#-常见问题)

## ✨ 功能特性

### 核心功能

- ✅ **文本消息** - 发送文本消息，支持@群成员
- ✅ **Markdown 消息** - 发送格式化的 Markdown 消息
- ✅ **图片消息** - 发送 Base64 编码的图片
- ✅ **图文消息** - 发送图文卡片消息（支持多篇）
- ✅ **模板卡片** - 发送交互式卡片消息（支持 URL 和小程序）
- ✅ **文件上传** - 上传文件到企业微信服务器

### 技术特性

- 🚀 **高性能** - 基于 FastAPI 和 uvicorn，异步非阻塞
- 🔌 **双模式** - 同时支持 REST API 和 WebSocket
- 📝 **自动文档** - 内置 Swagger/OpenAPI 文档
- 🔒 **类型安全** - 完整的 Pydantic 数据验证
- 🐳 **容器化** - Docker 和 Docker Compose 支持
- ☁️ **Serverless** - 支持 Vercel、AWS Lambda 部署
- 🧪 **测试覆盖** - 完整的单元测试和集成测试

## 🚀 快速开始

### 1. 环境要求

- Python 3.11 或更高版本
- 企业微信群机器人 Webhook URL

### 2. 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/wecom-bot-server.git
cd wecom-bot-server

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

复制环境变量配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 Webhook Key：

```env
WECOM_BOT_WEBHOOK_KEY=your-webhook-key-here
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

**如何获取 Webhook Key？**

1. 在企业微信群中添加机器人
2. 点击机器人设置，查看 Webhook 地址
3. 复制 `key=` 后面的部分，例如：
   - Webhook 地址：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=693axxx6-7aoc-4bc4-97a0-0ec2sifa5aaa`
   - Webhook Key：`693axxx6-7aoc-4bc4-97a0-0ec2sifa5aaa`

### 4. 启动服务

#### 方式一：使用启动脚本

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

#### 方式二：直接启动

```bash
uvicorn wecom_bot.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方式三：Docker 启动

```bash
# 使用 Docker Compose
docker-compose up -d

# 或使用 Docker
docker build -t wecom-bot-server .
docker run -d -p 8000:8000 \
  -e WECOM_BOT_WEBHOOK_KEY=your-key \
  wecom-bot-server
```

### 5. 访问服务

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **根路径**: http://localhost:8000/

## 📖 API 接口说明

### 1. 发送文本消息

**POST** `/api/v1/text`

```json
{
  "content": "这是一条测试消息",
  "mentioned_list": ["user1", "user2"],
  "mentioned_mobile_list": ["13800138000"]
}
```

**响应：**
```json
{
  "success": true,
  "message": "Text message sent successfully",
  "data": {
    "content": "这是一条测试消息"
  }
}
```

### 2. 发送 Markdown 消息

**POST** `/api/v1/markdown`

```json
{
  "content": "# 这是一条测试消息\n\n**重要**：请查看 [文档](https://example.com)"
}
```

支持的 Markdown 语法：
- 标题：`# 一级标题`
- 粗体：`**粗体**`
- 斜体：`*斜体*`
- 链接：`[文本](链接)`
- 代码：`` `代码` ``
- 引用：`> 引用`
- 列表：`- 列表项`

### 3. 发送图片消息

**POST** `/api/v1/image`

```json
{
  "base64_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "md5": "d41d8cd98f00b204e9800998ecf8427e"
}
```

**计算 MD5：**
```python
import hashlib
with open('image.png', 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()
```

### 4. 发送图文消息

**POST** `/api/v1/news`

```json
{
  "articles": [
    {
      "title": "标题 1",
      "description": "描述 1",
      "url": "https://example.com/1",
      "picurl": "https://example.com/image1.jpg"
    },
    {
      "title": "标题 2",
      "description": "描述 2",
      "url": "https://example.com/2"
    }
  ]
}
```

最多支持 10 篇图文。

### 5. 发送模板卡片消息

**POST** `/api/v1/template-card`

```json
{
  "card_type": "text_notice",
  "main_title": "卡片标题",
  "main_desc": "卡片描述",
  "card_action_type": 1,
  "card_action_url": "https://example.com"
}
```

**卡片动作类型：**
- `1` - 打开 URL
- `2` - 打开小程序

### 6. 上传文件

**POST** `/api/v1/upload-file`

```json
{
  "file_path": "/path/to/your/file.txt"
}
```

支持的文件类型：
- 文档：.txt, .log, .pdf, .doc, .docx, .xls, .xlsx
- 图片：.jpg, .jpeg, .png, .gif

文件大小限制：20MB

### 7. 获取机器人信息

**GET** `/api/v1/bot-info`

```json
{
  "success": true,
  "data": {
    "webhook_key": "693axx...",
    "send_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...",
    "upload_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=...",
    "status": "active"
  }
}
```

## 🔌 WebSocket 使用

### 连接 WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to WeCom Bot Server');
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('Response:', response);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### 发送消息

#### 发送文本消息

```javascript
ws.send(JSON.stringify({
  "type": "text",
  "data": {
    "content": "这是一条测试消息",
    "mentioned_list": ["user1", "user2"]
  },
  "request_id": "unique-request-id-123"
}));
```

#### 发送 Markdown 消息

```javascript
ws.send(JSON.stringify({
  "type": "markdown",
  "data": {
    "content": "# Hello\n\nThis is **bold** text."
  }
}));
```

#### 发送图片消息

```javascript
ws.send(JSON.stringify({
  "type": "image",
  "data": {
    "base64_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "md5": "d41d8cd98f00b204e9800998ecf8427e"
  }
}));
```

#### 发送图文消息

```javascript
ws.send(JSON.stringify({
  "type": "news",
  "data": {
    "articles": [
      {
        "title": "Article 1",
        "description": "Description 1",
        "url": "https://example.com/1",
        "picurl": "https://example.com/image1.jpg"
      }
    ]
  }
}));
```

#### 发送模板卡片

```javascript
ws.send(JSON.stringify({
  "type": "template_card",
  "data": {
    "card_type": "text_notice",
    "main_title": "Card Title",
    "main_desc": "Card Description",
    "card_action_type": 1,
    "card_action_url": "https://example.com"
  }
}));
```

#### 心跳检测

```javascript
// 发送 ping
ws.send(JSON.stringify({
  "type": "ping"
}));

// 接收 pong
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.type === 'pong') {
    console.log('Heartbeat OK');
  }
};
```

### 响应格式

所有响应都包含以下字段：

```json
{
  "success": true,
  "message": "Message sent successfully",
  "request_id": "unique-request-id-123",
  "data": {
    // 响应数据
  }
}
```

## 🌐 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t wecom-bot-server .

# 运行容器
docker run -d -p 8000:8000 \
  -e WECOM_BOT_WEBHOOK_KEY=your-webhook-key \
  -e LOG_LEVEL=INFO \
  --name wecom-bot \
  wecom-bot-server
```

### Docker Compose 部署

```bash
# 设置环境变量
export WECOM_BOT_WEBHOOK_KEY=your-webhook-key

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Vercel 部署

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

在 Vercel 平台设置环境变量 `WECOM_BOT_WEBHOOK_KEY`。

### AWS Lambda 部署

```bash
# 安装 AWS SAM CLI
pip install aws-sam-cli

# 构建
sam build

# 部署
sam deploy --guided
```

### 生产环境建议

1. **使用反向代理**：使用 Nginx 或 Apache 作为反向代理
2. **配置 HTTPS**：使用 Let's Encrypt 免费证书
3. **限制 CORS**：在生产环境中限制允许的域名
4. **日志管理**：配置日志轮转和集中管理
5. **监控告警**：集成 Prometheus + Grafana 监控
6. **负载均衡**：多实例部署时使用负载均衡

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `WECOM_BOT_WEBHOOK_KEY` | 企业微信机器人 Webhook Key | - | ✅ |
| `HOST` | 监听地址 | `0.0.0.0` | ❌ |
| `PORT` | 监听端口 | `8000` | ❌ |
| `LOG_LEVEL` | 日志级别 | `INFO` | ❌ |
| `WEBSOCKET_HEARTBEAT_INTERVAL` | WebSocket 心跳间隔（秒） | `30` | ❌ |
| `MAX_MESSAGE_LENGTH` | 最大消息长度 | `4096` | ❌ |
| `MAX_FILE_SIZE` | 最大文件大小（字节） | `20971520` (20MB) | ❌ |

### 配置文件位置

- 开发环境：`.env`
- 生产环境：环境变量或配置中心

## 🧪 测试

### 运行测试

```bash
# 安装测试依赖
pip install -r requirements.txt

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_client.py -v

# 查看测试覆盖率
pytest --cov=wecom_bot --cov-report=html

# 打开覆盖率报告
open htmlcov/index.html  # Mac/Linux
start htmlcov\\index.html  # Windows
```

### 测试示例

```python
# tests/test_example.py
import pytest
from wecom_bot.client import WeComBotClient

@pytest.mark.asyncio
async def test_send_text():
    client = WeComBotClient(webhook_key="test-key")
    result = await client.send_text(content="Test")
    assert result["errcode"] == 0
```

## 💡 示例代码

### Python 示例

```python
import httpx

# 发送文本消息
response = httpx.post(
    "http://localhost:8000/api/v1/text",
    json={
        "content": "Hello from Python!",
        "mentioned_list": ["user1"]
    }
)
print(response.json())
```

### JavaScript 示例

```javascript
// 使用 Fetch API
fetch('http://localhost:8000/api/v1/markdown', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: '# Hello from JavaScript!'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

### cURL 示例

```bash
# 发送文本消息
curl -X POST http://localhost:8000/api/v1/text \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from cURL!"}'

# 发送 Markdown 消息
curl -X POST http://localhost:8000/api/v1/markdown \
  -H "Content-Type: application/json" \
  -d '{"content":"# Hello\n\n**Bold text**"}'

# 健康检查
curl http://localhost:8000/health
```

## ❓ 常见问题

### 1. 消息发送失败，返回错误码 40003

**原因**：Webhook Key 无效或过期

**解决**：
- 检查 Webhook Key 是否正确
- 重新创建企业微信群机器人
- 确认可信 IP 已配置

### 2. WebSocket 连接断开

**原因**：网络问题或心跳超时

**解决**：
- 实现自动重连机制
- 定期发送 ping 消息
- 检查防火墙设置

### 3. 文件上传失败

**原因**：文件过大或类型不支持

**解决**：
- 检查文件大小（最大 20MB）
- 确认文件类型在允许列表中
- 检查文件路径是否正确

### 4. 性能优化建议

- 使用连接池（httpx.AsyncClient）
- 启用 Gzip 压缩
- 使用 Redis 缓存 access_token
- 部署多个实例 + 负载均衡

### 5. 如何@所有人？

在文本消息中使用：

```json
{
  "content": "@所有人 重要通知",
  "mentioned_list": ["@all"]
}
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

- 项目地址：https://github.com/yourusername/wecom-bot-server
- 问题反馈：https://github.com/yourusername/wecom-bot-server/issues

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能 Python Web 框架
- [企业微信 API](https://developer.work.weixin.qq.com/document/path/91770) - 企业微信官方 API 文档
- [uvicorn](https://www.uvicorn.org/) - ASGI 服务器

---

**Made with ❤️ by Your Name**
