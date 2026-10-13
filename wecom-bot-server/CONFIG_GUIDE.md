# 企业微信机器人配置指南

## 📝 配置说明

### 1. 获取企业微信机器人 Webhook Key

#### 步骤 1：在企业微信中添加机器人

1. 打开企业微信
2. 进入要添加机器人的群聊
3. 点击右上角的「...」或「设置」
4. 选择「群机器人」
5. 点击「添加机器人」
6. 输入机器人名称（如：通知助手）
7. 点击「添加」

#### 步骤 2：复制 Webhook Key

添加成功后，你会看到一个 Webhook 地址：
```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY
```

其中 `YOUR_WEBHOOK_KEY` 就是你的机器人密钥（一串 UUID 格式的字符串）

例如：`5b76c8a6-1234-5678-9abc-def012345678`

### 2. 配置后端服务

#### 方式一：使用 .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```bash
cd <workspace>\workwx-api\wecom-bot-server
```

创建文件 `.env`，内容如下：

```env
# 企业微信机器人配置（必填）
WECOM_BOT_WEBHOOK_KEY=5b76c8a6-1234-5678-9abc-def012345678

# 服务器配置（可选）
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

**注意：** 将 `5b76c8a6-1234-5678-9abc-def012345678` 替换为你自己的 Webhook Key

#### 方式二：使用环境变量

**Windows PowerShell:**
```powershell
$env:WECOM_BOT_WEBHOOK_KEY="5b76c8a6-1234-5678-9abc-def012345678"
```

**Linux/Mac:**
```bash
export WECOM_BOT_WEBHOOK_KEY="5b76c8a6-1234-5678-9abc-def012345678"
```

#### 方式三：启动时指定

```bash
# Windows PowerShell
$env:WECOM_BOT_WEBHOOK_KEY="your-key"; python -m uvicorn wecom_bot.main:app --reload

# Linux/Mac
WECOM_BOT_WEBHOOK_KEY="your-key" python -m uvicorn wecom_bot.main:app --reload
```

### 3. 验证配置

启动后端服务后，访问健康检查接口：

```bash
curl http://localhost:8000/health
```

或者访问 API 文档：
```
http://localhost:8000/docs
```

查看 `/api/v1/bot-info` 接口，应该显示你的机器人信息。

### 4. 测试机器人

#### 方法一：使用 API 文档测试

1. 访问 http://localhost:8000/docs
2. 找到 `/api/v1/text` 接口
3. 点击「Try it out」
4. 输入请求内容：
```json
{
  "content": "测试消息",
  "mentioned_list": []
}
```
5. 点击「Execute」
6. 查看企业微信群是否收到消息

#### 方法二：使用 Web 管理后台

1. 启动前端：`npm run dev`
2. 访问 http://localhost:3001
3. 点击「发送消息」
4. 选择「文本消息」
5. 输入「测试消息」
6. 点击「立即发送」
7. 查看企业微信群是否收到消息

#### 方法三：使用 curl 命令

```bash
curl -X POST http://localhost:8000/api/v1/text \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"测试消息\",\"mentioned_list\":[]}"
```

## 🔧 配置参数说明

### 必填配置

| 参数 | 说明 | 示例 |
|------|------|------|
| `WECOM_BOT_WEBHOOK_KEY` | 企业微信机器人密钥 | `5b76c8a6-1234-5678-9abc-def012345678` |

### 可选配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `HOST` | 服务器监听地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### 高级配置（通常不需要修改）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `WECOM_BOT_BASE_URL` | 企业微信 API 地址 | `https://qyapi.weixin.qq.com/cgi-bin/webhook` |

## 📱 企业微信机器人功能

### 支持的消息类型

1. **文本消息** - 纯文本内容，支持@成员
2. **Markdown 消息** - 支持 Markdown 格式
3. **图片消息** - 发送图片
4. **图文消息** - 发送图文链接
5. **文件消息** - 发送文件

### @成员功能

在文本消息中，可以@特定成员：

```json
{
  "content": "请 @张三 确认一下",
  "mentioned_list": ["zhangsan"],
  "mentioned_mobile_list": ["13800138000"]
}
```

- `mentioned_list`: 成员账号列表
- `mentioned_mobile_list`: 成员手机号列表
- 使用 `@all` 可以@所有人

## 🐛 常见问题

### Q1: 消息发送失败，提示 key 无效

**原因：** Webhook Key 配置错误

**解决方法：**
1. 检查 `.env` 文件中的 `WECOM_BOT_WEBHOOK_KEY` 是否正确
2. 确认 Webhook Key 是从企业微信复制的完整字符串
3. 重启后端服务

### Q2: 机器人没有响应

**原因：** 机器人可能被禁用或删除

**解决方法：**
1. 在企业微信中检查机器人状态
2. 重新添加机器人并获取新的 Webhook Key
3. 更新配置文件

### Q3: 文件上传失败

**原因：** 文件大小超限或格式不支持

**解决方法：**
1. 检查文件大小（最大 20MB）
2. 确认文件格式在允许列表中
3. 查看后端日志获取详细错误信息

### Q4: 如何修改配置？

**方法：**
1. 编辑 `.env` 文件
2. 重启后端服务（配置才会生效）
3. 或者修改环境变量后重启

## 🔐 安全建议

1. **不要泄露 Webhook Key**
   - 不要将 `.env` 文件提交到 Git
   - 不要在公开场合分享 Webhook Key
   - 定期更换 Webhook Key

2. **限制机器人权限**
   - 只在必要的群聊中添加机器人
   - 定期审查机器人发送的消息

3. **使用环境变量**
   - 生产环境使用环境变量而非 `.env` 文件
   - 使用密钥管理服务（如 AWS Secrets Manager）

## 📊 配置检查清单

- [ ] 已从企业微信获取 Webhook Key
- [ ] 已创建 `.env` 文件
- [ ] 已将 Webhook Key 填入 `.env`
- [ ] 已重启后端服务
- [ ] 已测试消息发送功能
- [ ] 已验证机器人收到消息

---

**配置完成后，你就可以正常使用 Web 管理后台发送消息了！** 🎉
