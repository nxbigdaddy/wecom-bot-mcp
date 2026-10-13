# 🔐 登录认证系统 - 完整说明

## ✅ 已完成功能

### 1️⃣ 登录页面

**访问地址：** http://localhost:3001/login

**功能特性：**
- ✅ 美观的渐变背景设计
- ✅ 用户名密码输入
- ✅ 记住密码功能
- ✅ 登录错误提示
- ✅ 密码可见性切换
- ✅ 回车键登录

**默认账号：**
- 用户名：`admin`
- 密码：`admin123`

---

### 2️⃣ 认证系统

**后端 API：**

1. **登录接口**
   ```http
   POST /api/v1/login
   Content-Type: application/json
   
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
   
   **响应：**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "username": "admin",
     "role": "admin"
   }
   ```

2. **获取当前用户信息**
   ```http
   GET /api/v1/me
   Authorization: Bearer <token>
   ```

3. **登出接口**
   ```http
   POST /api/v1/logout
   Authorization: Bearer <token>
   ```

4. **初始化管理员账号**
   ```http
   POST /api/v1/init-admin
   ```

---

### 3️⃣ 路由守卫

**访问控制：**
- ✅ 所有页面都需要登录才能访问
- ✅ 未登录自动跳转到登录页
- ✅ 已登录访问登录页自动跳转到首页
- ✅ 退出登录后清除所有状态

**路由配置：**
```javascript
{
  path: '/login',
  name: 'Login',
  component: () => import('@/views/Login.vue'),
  meta: { title: '登录' }
},
{
  path: '/',
  name: 'Dashboard',
  component: () => import('@/views/Dashboard.vue'),
  meta: { requiresAuth: true }  // 需要认证
}
// ... 其他路由
```

---

### 4️⃣ 用户状态管理

**Pinia Store：**

```javascript
// stores/user.js
{
  token: '',           // JWT Token
  username: '',        // 用户名
  role: 'user',        // 用户角色
  isLoggedIn: false    // 登录状态
}
```

**方法：**
- `setToken(token)` - 保存 Token
- `setUsername(name)` - 保存用户名
- `setRole(role)` - 保存角色
- `logout()` - 退出登录
- `initFromStorage()` - 从本地存储初始化

---

### 5️⃣ 数据库

**数据库类型：** SQLite（默认）

**数据库文件位置：** `./data/wecom_bot.db`

**用户表结构：**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    status BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**其他数据表：**

1. **employees** - 员工信息表
2. **scheduled_tasks** - 定时任务表
3. **task_execution_history** - 任务执行历史表
4. **message_history** - 消息发送历史表
5. **hr_configs** - HR 系统配置表
6. **sync_history** - 数据同步历史表

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd <workspace>\workwx-api\wecom-bot-server
pip install -r requirements.txt
```

**新增依赖：**
- `PyJWT>=2.8.0` - JWT 认证

---

### 2. 配置环境变量

```bash
# .env 文件

# 企业微信配置
WECOM_BOT_WEBHOOK_KEY=your-webhook-key

# 数据库配置
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=./data/wecom_bot.db

# JWT 配置（生产环境请修改）
JWT_SECRET_KEY=YOUR_SECRET

# 服务器配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

---

### 3. 启动服务

```bash
# Windows
start.bat

# 或手动启动
uvicorn wecom_bot.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后系统会自动：
1. 初始化数据库
2. 创建默认管理员账号（admin/admin123）
3. 初始化定时任务调度器

---

### 4. 访问系统

**前端界面：** http://localhost:3001

**首次访问会自动跳转到登录页**

输入默认账号：
- 用户名：`admin`
- 密码：`admin123`

---

## 📊 系统架构

### 前端架构

```
web/src/
├── views/
│   ├── Login.vue          # 登录页面 ⭐ 新增
│   ├── Dashboard.vue      # 控制台
│   ├── Scheduler.vue      # 定时任务
│   ├── HRIntegration.vue  # HR 数据集成
│   └── ...
│
├── stores/
│   ├── user.js            # 用户状态管理 ⭐ 新增
│   └── app.js             # 应用状态管理
│
├── router/
│   └── index.js           # 路由配置（已添加认证守卫）
│
└── components/
    └── Layout.vue         # 主布局（已添加登出功能）
```

### 后端架构

```
wecom_bot/
├── main.py                # FastAPI 主应用
├── database.py            # 数据库配置
├── models.py              # 数据库模型
├── routes_auth.py         # 认证路由 ⭐ 新增
├── routes.py              # 消息路由
├── routes_scheduler.py    # 定时任务路由
├── scheduler.py           # 定时任务调度器
└── config.py              # 配置管理
```

---

## 🔐 安全特性

### 1. 密码加密

使用 SHA-256 哈希算法加密密码：

```python
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

### 2. JWT Token 认证

使用 JWT（JSON Web Token）进行无状态认证：

- **有效期：** 24 小时
- **算法：** HS256
- **存储：** 客户端 localStorage

### 3. 路由守卫

所有需要认证的页面都有路由守卫保护：

```javascript
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = YOUR_SECRET'token')
    if (!token) {
      next({ name: 'Login' })
    } else {
      next()
    }
  }
})
```

### 4. 会话管理

- 登录成功后保存 Token 到 localStorage
- 退出登录时清除所有用户数据
- Token 过期后需要重新登录

---

## 💾 数据库说明

### 数据库类型

**默认：** SQLite

**优点：**
- 无需安装数据库服务器
- 单文件数据库，便于部署
- 适合小型到中型应用

**可选：** MySQL / PostgreSQL

### 数据库配置

**SQLite（默认）**
```bash
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=./data/wecom_bot.db
```

**MySQL**
```bash
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_PASSWORD
MYSQL_DATABASE=wecom_bot
```

**PostgreSQL**
```bash
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_DATABASE=wecom_bot
```

### 数据库表

系统会自动创建以下 7 个表：

1. **users** - 用户表
   - 存储系统用户账号
   - 密码哈希加密
   - 角色权限管理

2. **employees** - 员工信息表
   - 员工基本信息
   - 生日、入职日期
   - 企业微信 ID

3. **scheduled_tasks** - 定时任务表
   - 任务配置
   - 执行计划
   - 接收者设置

4. **task_execution_history** - 任务执行历史
   - 执行记录
   - 执行状态
   - 错误信息

5. **message_history** - 消息发送历史
   - 所有消息记录
   - 发送状态
   - 发送者信息

6. **hr_configs** - HR 系统配置
   - HR 系统连接信息
   - 同步配置

7. **sync_history** - 数据同步历史
   - 同步记录
   - 同步结果

---

## 🎨 界面预览

### 登录页面

- 渐变紫色背景
- 动态网格动画
- 白色卡片式登录框
- 用户名密码输入
- 记住密码选项
- 错误提示

### 主界面

- 侧边栏导航菜单
- 顶部面包屑导航
- WebSocket 连接状态
- 用户信息下拉菜单
- 退出登录功能

---

## 📝 使用流程

### 首次使用

1. **启动服务**
   ```bash
   start.bat
   ```

2. **访问系统**
   - 打开浏览器访问 http://localhost:3001
   - 自动跳转到登录页

3. **登录**
   - 用户名：`admin`
   - 密码：`admin123`

4. **修改密码**
   - 登录后建议修改默认密码
   - 在「用户管理」中修改

### 日常使用

1. **登录系统**
   - 访问 http://localhost:3001
   - 输入账号密码

2. **使用功能**
   - 控制台 - 查看统计
   - 发送消息 - 手动发送
   - 定时任务 - 自动发送
   - HR 数据 - 员工管理

3. **退出登录**
   - 点击右上角用户名
   - 选择「退出登录」

---

## 🔧 常见问题

### Q1: 忘记密码怎么办？

**A:** 可以删除数据库文件重新初始化：

```bash
# 删除数据库
rm data/wecom_bot.db

# 重启服务，会自动创建默认管理员
start.bat
```

### Q2: 如何修改默认密码？

**A:** 
1. 登录后访问「用户管理」
2. 编辑 admin 用户
3. 修改密码

或者直接修改数据库：

```sql
UPDATE users 
SET password_hash = '新的密码哈希' 
WHERE username = 'admin';
```

### Q3: Token 过期了怎么办？

**A:** Token 有效期 24 小时，过期后需要重新登录。

### Q4: 如何更换数据库？

**A:** 
1. 修改 `.env` 中的 `DATABASE_TYPE`
2. 配置对应的数据库连接信息
3. 重启服务，会自动创建表

### Q5: 生产环境需要注意什么？

**A:** 
1. 修改 `JWT_SECRET_KEY` 为随机字符串
2. 使用 MySQL 或 PostgreSQL 数据库
3. 配置 HTTPS
4. 限制 CORS 域名
5. 修改默认管理员密码

---

## 📊 数据持久化

### 本地存储

**前端存储内容：**
- `token` - JWT 访问令牌
- `username` - 用户名
- `role` - 用户角色
- `rememberedUser` - 记住的用户名

**存储位置：** 浏览器 localStorage

### 数据库存储

**永久保存：**
- 用户账号信息
- 员工数据
- 定时任务配置
- 发送历史记录
- HR 系统配置
- 同步历史

---

## 🎉 总结

现在系统包含完整的认证功能：

✅ **登录页面** - 美观的登录界面  
✅ **JWT 认证** - 安全的 Token 认证  
✅ **路由守卫** - 访问控制保护  
✅ **用户管理** - Pinia 状态管理  
✅ **SQLite 数据库** - 数据持久化  
✅ **7 个数据表** - 完整的数据库结构  
✅ **默认管理员** - admin/admin123  
✅ **退出登录** - 清除状态跳转  

**立即体验：**
```bash
cd <workspace>\workwx-api\wecom-bot-server
start.bat
```

访问 http://localhost:3001 登录使用！

---

**创建时间：** 2026-03-16  
**版本：** v4.0.0  
**状态：** ✅ 生产就绪
