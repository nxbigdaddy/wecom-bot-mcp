# 快速入门指南

本指南将帮助你在 5 分钟内快速上手 WeCom Bot Server。

## 📦 第一步：安装

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/wecom-bot-server.git
cd wecom-bot-server
```

### 2. 安装依赖

```bash
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

## ⚙️ 第二步：配置

### 1. 复制环境变量文件

```bash
cp .env.example .env
```

### 2. 获取 Webhook Key

1. 打开企业微信，进入要添加机器人的群聊
2. 点击右上角菜单 → 添加群机器人
3. 新建机器人，填写名称
4. 复制 Webhook 地址中的 key 参数

例如：
```
Webhook 地址：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=693axxx6-7aoc-4bc4-97a0-0ec2sifa5aaa
Webhook Key: 693axxx6-7aoc-4bc4-97a0-0ec2sifa5aaa
```

### 3. 配置环境变量

编辑 `.env` 文件：

```env
WECOM_BOT_WEBHOOK_KEY=693axxx6-7aoc-4bc4-97a0-0ec2sifa5aaa
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

## 🚀 第三步：启动

### 方式一：使用启动脚本（推荐）

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### 方式二：手动启动

```bash
uvicorn wecom_bot.main:app --host 0.0.0.0 --port 8000 --reload
```

### 方式三：Docker 启动

```bash
docker-compose up -d
```

## ✅ 第四步：验证

### 1. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

你应该能看到 Swagger UI 界面。

### 2. 健康检查

```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "websocket_connections": 0
}
```

### 3. 发送第一条消息

#### 使用 cURL

```bash
curl -X POST http://localhost:8000/api/v1/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你好，这是第一条测试消息！"
  }'
```

#### 使用 Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/text",
    json={"content": "你好，这是第一条测试消息！"}
)

print(response.json())
```

#### 使用 JavaScript

```javascript
fetch('http://localhost:8000/api/v1/text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: '你好，这是第一条测试消息！'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

如果成功，你的企业微信群应该收到了消息！

## 🎯 第五步：尝试更多功能

### 1. 发送 Markdown 消息

```bash
curl -X POST http://localhost:8000/api/v1/markdown \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# 欢迎使用 WeCom Bot Server\n\n## 功能特性\n\n- ✅ 文本消息\n- ✅ Markdown 消息\n- ✅ 图片消息\n- ✅ 图文消息\n\n[查看文档](https://github.com/yourusername/wecom-bot-server)"
  }'
```

### 2. 发送图文消息

```bash
curl -X POST http://localhost:8000/api/v1/news \
  -H "Content-Type: application/json" \
  -d '{
    "articles": [
      {
        "title": "产品发布 | 新产品上线",
        "description": "我们很高兴地宣布新产品正式上线",
        "url": "https://example.com",
        "picurl": "https://example.com/image.jpg"
      }
    ]
  }'
```

### 3. 使用 WebSocket

创建 `test_ws.html`：

```html
<!DOCTYPE html>
<html>
<head>
  <title>WeCom Bot WebSocket Test</title>
</head>
<body>
  <h1>WeCom Bot WebSocket 测试</h1>
  <button onclick="sendText()">发送文本消息</button>
  <button onclick="sendMarkdown()">发送 Markdown 消息</button>
  
  <script>
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('WebSocket 已连接');
    };
    
    ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      console.log('收到响应:', response);
      alert(response.message);
    };
    
    function sendText() {
      ws.send(JSON.stringify({
        type: 'text',
        data: {
          content: '来自 WebSocket 的测试消息',
          mentioned_list: []
        }
      }));
    }
    
    function sendMarkdown() {
      ws.send(JSON.stringify({
        type: 'markdown',
        data: {
          content: '# Hello from WebSocket\n\n这是一条 **WebSocket** 消息'
        }
      }));
    }
  </script>
</body>
</html>
```

用浏览器打开 `test_ws.html`，点击按钮测试。

## 📊 第六步：运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行测试
pytest

# 查看测试覆盖率
pytest --cov=wecom_bot --cov-report=html

# 打开覆盖率报告
# Mac/Linux:
open htmlcov/index.html
# Windows:
start htmlcov\\index.html
```

## 🐳 第七步：Docker 部署

```bash
# 构建镜像
docker build -t wecom-bot-server .

# 运行容器
docker run -d -p 8000:8000 \
  -e WECOM_BOT_WEBHOOK_KEY=your-webhook-key \
  --name wecom-bot \
  wecom-bot-server

# 查看日志
docker logs -f wecom-bot

# 停止容器
docker stop wecom-bot
```

## 🔧 常见问题排查

### 1. 启动失败：端口被占用

**错误信息**：`Address already in use`

**解决方案**：更换端口

```bash
# 修改 .env 文件
PORT=8001

# 或命令行指定
uvicorn wecom_bot.main:app --port 8001
```

### 2. 消息发送失败：无效的 Webhook Key

**错误信息**：`errcode: 40003`

**解决方案**：
- 检查 `.env` 文件中的 Webhook Key 是否正确
- 确认没有多余的空格
- 重新创建企业微信机器人

### 3. 无法访问 API 文档

**解决方案**：
- 检查服务是否启动成功
- 确认防火墙允许 8000 端口
- 尝试访问 http://127.0.0.1:8000/docs

### 4. Docker 启动失败

**解决方案**：
```bash
# 检查 Docker 是否运行
docker ps

# 查看容器日志
docker logs wecom-bot

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📚 下一步

完成快速入门后，你可以：

1. 阅读 [完整 API 文档](API_DOCUMENTATION.md)
2. 查看 [README.md](README.md) 了解更多功能
3. 学习如何 [部署到生产环境](README.md#部署指南)
4. 查看 [示例代码](examples/) 目录

## 💡 提示

- 开发环境使用 `--reload` 参数可以自动重载代码
- 生产环境建议设置 `LOG_LEVEL=WARNING` 减少日志输出
- 使用 WebSocket 可以实现实时双向通信
- 消息发送有频率限制，注意不要频繁调用

## 🆘 获取帮助

如果遇到问题：

1. 查看 [常见问题](README.md#常见问题)
2. 查看项目 Issues
3. 提交新的 Issue

---

**祝你使用愉快！** 🎉
