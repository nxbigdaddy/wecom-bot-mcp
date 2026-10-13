# 🎉 定时任务和 HR 集成系统 - 完整功能文档

## ✅ 新增功能概览

本次更新添加了完整的定时任务系统和 HR 数据集成管理，支持：

1. **定时任务管理** - 创建、编辑、删除定时任务，自动发送消息
2. **HR 数据集成** - 从 HR 系统同步员工数据，管理员工信息
3. **数据库支持** - SQLite/MySQL/PostgreSQL 多种数据库
4. **生日祝福** - 自动发送员工生日祝福
5. **入职周年** - 自动发送入职周年纪念消息
6. **发送记录** - 完整的发送历史记录和统计

---

## 📋 功能详情

### 1️⃣ 定时任务管理

**访问路径：** 左侧菜单 → 自动化 → 定时任务

#### 功能特性

✅ **创建定时任务**
- 支持多种消息类型（文本、Markdown、图片、图文、卡片）
- 支持多种执行计划（一次性、每分钟、每小时、每天、每周、每月、Cron）
- 支持变量替换（{name}、{department}、{birthday}、{work_years} 等）
- 支持指定接收者（全员、部门、特定员工）

✅ **任务类型**
- **生日祝福** - 自动发送生日祝福给当天生日的员工
- **入职周年** - 自动发送周年纪念给入职纪念日的员工
- **自定义任务** - 自定义消息内容和发送对象

✅ **执行计划**
- **一次性执行** - 在指定时间执行一次
- **每分钟执行** - 每隔一分钟执行
- **每小时执行** - 每隔一小时执行
- **每天执行** - 每天指定时间执行
- **每周执行** - 每周指定星期和时间执行
- **每月执行** - 每月指定日期和时间执行
- **Cron 表达式** - 自定义 Cron 表达式执行

✅ **任务管理**
- 查看任务列表和执行计划
- 启用/禁用任务
- 立即执行任务
- 查看执行历史
- 删除任务

#### 使用示例

**示例 1：每天 9 点发送早报**

1. 点击「创建任务」
2. 填写任务名称：每日早报
3. 选择消息类型：文本消息
4. 选择执行类型：每天
5. 设置执行时间：09:00
6. 填写消息内容：大家早上好！这是今天的早报...
7. 保存

**示例 2：员工生日祝福**

1. 点击「创建任务」
2. 填写任务名称：生日祝福
3. 选择任务类型：birthday
4. 选择消息类型：文本消息
5. 选择执行类型：每天
6. 设置执行时间：09:00
7. 填写消息内容：
   ```
   🎂 祝 {name} 生日快乐！
   
   感谢你为 {department} 做出的贡献，
   愿你在新的一岁里工作顺利，生活愉快！
   
   - 人力资源部
   ```
8. 选择接收者类型：specific（特定员工）
9. 系统会自动筛选今天生日的员工
10. 保存

**示例 3：入职周年纪念**

1. 点击「创建任务」
2. 填写任务名称：入职周年纪念
3. 选择任务类型：anniversary
4. 选择消息类型：Markdown
5. 选择执行类型：每天
6. 设置执行时间：10:00
7. 填写消息内容：
   ```markdown
   # 🎉 入职纪念
   
   今天是 {name} 加入公司的第 {work_years} 周年！
   
   感谢你的辛勤付出和贡献！
   
   **部门：** {department}
   **职位：** {position}
   **入职日期：** {hire_date}
   
   愿我们继续携手同行，共创辉煌！
   ```
8. 保存

#### 变量说明

在消息内容中可以使用以下变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{name}` | 员工姓名 | 张三 |
| `{employee_id}` | 员工工号 | E001 |
| `{department}` | 员工部门 | 技术部 |
| `{position}` | 员工职位 | 高级工程师 |
| `{birthday}` | 员工生日 | 1990-03-16 |
| `{age}` | 员工年龄 | 34 |
| `{hire_date}` | 入职日期 | 2020-03-16 |
| `{work_years}` | 工龄（周年） | 4 |

---

### 2️⃣ HR 数据集成

**访问路径：** 左侧菜单 → 自动化 → HR 数据集成

#### 功能特性

✅ **HR 系统配置**
- 支持多种 HR 系统（钉钉、企业微信、飞书、北森、肯耐珂萨、自定义 API）
- 支持多种同步方式（API、CSV 文件、Excel 文件、数据库直连）
- 支持设置同步频率（每小时、每天、每周、每月、手动）
- 测试连接功能

✅ **员工信息管理**
- 完整的员工信息列表
- 添加、编辑、删除员工
- 搜索员工（姓名、工号、部门）
- 筛选员工（部门、状态、生日范围）
- 分页显示

✅ **员工字段**
- 工号（唯一标识）
- 姓名
- 性别
- 生日（用于生日祝福）
- 部门
- 职位
- 入职日期（用于周年计算）
- 邮箱
- 手机号
- 企业微信 ID（用于发送消息）
- 状态（在职/离职）

✅ **数据统计**
- 总员工数
- 今日生日员工数
- 本周生日员工数
- 本月生日员工数
- 生日提醒徽章

✅ **数据同步**
- 立即同步 HR 系统数据
- 查看同步历史
- 导入 CSV/Excel 文件
- 自动去重和更新

#### HR 系统配置说明

**企业微信同步**

1. 选择 HR 系统类型：企业微信
2. 选择同步方式：API
3. 填写 API 地址：https://qyapi.weixin.qq.com/cgi-bin/user/list
4. 填写 API Token：企业微信 API 访问令牌
5. 测试连接
6. 保存配置

**数据库直连**

1. 选择 HR 系统类型：自定义 API
2. 选择同步方式：数据库直连
3. 选择数据库类型：MySQL/PostgreSQL/SQL Server/Oracle
4. 填写数据库连接信息：
   - 主机地址
   - 端口
   - 数据库名
   - 用户名
   - 密码
5. 填写员工表名：employees
6. 测试连接
7. 保存配置

**CSV/Excel 导入**

1. 选择同步方式：CSV 文件导入 或 Excel 文件导入
2. 点击「导入数据」按钮
3. 选择文件
4. 映射字段
5. 开始导入

#### 员工管理操作

**添加员工**

1. 点击「添加员工」按钮
2. 填写员工信息：
   - 工号（必填，唯一）
   - 姓名（必填）
   - 性别（必填）
   - 生日（必填，用于生日祝福）
   - 部门（必填）
   - 职位
   - 入职日期（必填，用于周年计算）
   - 邮箱
   - 手机号
   - 企业微信 ID（用于发送消息）
3. 保存

**编辑员工**

1. 点击员工行的「编辑」按钮
2. 修改员工信息
3. 保存

**发送生日祝福**

1. 找到要发送的员工
2. 点击「生日祝福」按钮
3. 确认发送
4. 系统会立即发送生日祝福消息

**发送周年祝福**

1. 找到要发送的员工
2. 点击「周年祝福」按钮
3. 系统会显示入职周年数
4. 确认发送
5. 系统会立即发送周年纪念消息

---

### 3️⃣ 数据库支持

#### 支持的数据库类型

✅ **SQLite**（默认）
- 无需额外配置
- 适合小型部署和测试
- 单文件数据库

✅ **MySQL**
- 适合生产环境
- 支持高并发
- 需要安装 MySQL 服务器

✅ **PostgreSQL**
- 功能强大的开源数据库
- 支持复杂查询
- 适合企业级应用

#### 数据库配置

**使用 SQLite（默认）**

```bash
# .env 文件
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=./data/wecom_bot.db
```

**使用 MySQL**

```bash
# .env 文件
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_PASSWORD
MYSQL_DATABASE=wecom_bot
```

**使用 PostgreSQL**

```bash
# .env 文件
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_DATABASE=wecom_bot
```

#### 数据库表结构

系统会自动创建以下数据库表：

1. **users** - 用户表
   - 用户信息、角色、权限

2. **employees** - 员工信息表
   - 员工基本信息、生日、入职日期等

3. **scheduled_tasks** - 定时任务表
   - 任务配置、执行计划、接收者等

4. **task_execution_history** - 任务执行历史表
   - 任务执行记录、状态、结果等

5. **message_history** - 消息发送历史表
   - 所有消息发送记录

6. **hr_configs** - HR 系统配置表
   - HR 系统连接配置

7. **sync_history** - 数据同步历史表
   - 数据同步记录

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd <workspace>\workwx-api\wecom-bot-server
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，配置以下变量：
# - WECOM_BOT_WEBHOOK_KEY（必填）
# - DATABASE_TYPE（可选，默认 sqlite）
# - 其他数据库配置（如使用 MySQL/PostgreSQL）
```

### 3. 初始化数据库

数据库会在首次启动时自动初始化。

### 4. 启动服务

```bash
# Windows
start.bat

# 或者手动启动
uvicorn wecom_bot.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问系统

- **前端界面：** http://localhost:3001
- **API 文档：** http://localhost:8000/docs
- **后端服务：** http://localhost:8000

---

## 📊 API 接口

### 定时任务 API

#### 获取任务列表
```http
GET /api/v1/tasks
```

**参数：**
- `skip` - 跳过数量（分页）
- `limit` - 返回数量（分页）
- `status_filter` - 状态筛选（true/false）
- `task_type` - 任务类型筛选

#### 获取任务详情
```http
GET /api/v1/tasks/{task_id}
```

#### 创建任务
```http
POST /api/v1/tasks
```

**请求体：**
```json
{
  "name": "生日祝福",
  "description": "自动发送生日祝福",
  "task_type": "birthday",
  "message_type": "text",
  "schedule_type": "day",
  "schedule": "09:00",
  "status": true,
  "content": "🎂 祝 {name} 生日快乐！",
  "recipient_type": "all"
}
```

#### 更新任务
```http
PUT /api/v1/tasks/{task_id}
```

#### 删除任务
```http
DELETE /api/v1/tasks/{task_id}
```

#### 立即执行任务
```http
POST /api/v1/tasks/{task_id}/run
```

#### 获取任务执行历史
```http
GET /api/v1/tasks/{task_id}/history
```

### 员工管理 API

#### 获取员工列表
```http
GET /api/v1/employees
```

**参数：**
- `skip` - 跳过数量
- `limit` - 返回数量
- `search` - 搜索关键词
- `department` - 部门筛选
- `status_filter` - 状态筛选
- `birthday_start` - 生日开始日期
- `birthday_end` - 生日结束日期

#### 获取员工详情
```http
GET /api/v1/employees/{employee_id}
```

#### 添加员工
```http
POST /api/v1/employees
```

**请求体：**
```json
{
  "employee_id": "E001",
  "name": "张三",
  "gender": "男",
  "birthday": "1990-03-16",
  "department": "技术部",
  "position": "高级工程师",
  "hire_date": "2020-03-16",
  "email": "zhangsan@example.com",
  "phone": "13800138001",
  "wecom_userid": "zhangsan",
  "status": true
}
```

#### 更新员工
```http
PUT /api/v1/employees/{employee_id}
```

#### 删除员工
```http
DELETE /api/v1/employees/{employee_id}
```

#### 获取今日生日员工
```http
GET /api/v1/employees/birthday/today
```

#### 获取本周生日员工
```http
GET /api/v1/employees/birthday/week
```

#### 获取即将入职周年员工
```http
GET /api/v1/employees/anniversary/upcoming
```

### HR 配置 API

#### 获取 HR 配置
```http
GET /api/v1/hr-config
```

#### 保存 HR 配置
```http
POST /api/v1/hr-config
```

#### 立即同步 HR 数据
```http
POST /api/v1/hr-config/sync
```

#### 获取同步历史
```http
GET /api/v1/hr-config/sync-history
```

---

##  使用场景

### 场景 1：每日自动发送早报

**需求：** 每个工作日上午 9 点发送早报到公司群

**配置：**
1. 创建定时任务
2. 任务类型：custom
3. 消息类型：文本或 Markdown
4. 执行计划：每天 09:00
5. 接收者：全员
6. 消息内容：早报内容

### 场景 2：员工生日自动祝福

**需求：** 员工生日当天自动发送生日祝福

**配置：**
1. 在 HR 数据集成中维护员工生日信息
2. 创建定时任务
3. 任务类型：birthday
4. 执行计划：每天 09:00
5. 消息内容：使用变量 `{name}`、`{age}` 等
6. 系统会自动筛选今天生日的员工并发送

### 场景 3：入职周年纪念

**需求：** 员工入职周年自动发送纪念消息

**配置：**
1. 在 HR 数据集成中维护员工入职日期
2. 创建定时任务
3. 任务类型：anniversary
4. 执行计划：每天 10:00
5. 消息内容：使用变量 `{name}`、`{work_years}`、`{hire_date}` 等
6. 系统会自动计算工龄并发送

### 场景 4：部门周报

**需求：** 每周五下午发送部门周报

**配置：**
1. 创建定时任务
2. 任务类型：custom
3. 消息类型：Markdown
4. 执行计划：每周五 17:00
5. 接收者：指定部门
6. 消息内容：周报模板

### 场景 5：从 HR 系统同步数据

**需求：** 每天自动从 HR 系统同步员工数据

**配置：**
1. 在 HR 数据集成中配置 HR 系统连接
2. 选择同步方式：API
3. 设置同步频率：每天
4. 系统会自动同步员工信息
5. 可以在同步历史中查看同步结果

---

## 📁 文件结构

```
wecom-bot-server/
├── wecom_bot/
│   ├── main.py                 # FastAPI 主应用
│   ├── database.py             # 数据库配置和连接
│   ├── models.py               # 数据库模型
│   ├── scheduler.py            # 定时任务调度器
│   ├── routes.py               # 消息路由
│   ├── routes_scheduler.py     # 定时任务和 HR 路由
│   ├── client.py               # 企业微信客户端
│   ├── websocket.py            # WebSocket 处理
│   └── config.py               # 配置管理
│
├── web/src/views/
│   ├── Scheduler.vue           # 定时任务管理页面
│   ├── HRIntegration.vue       # HR 数据集成页面
│   ├── Dashboard.vue           # 控制台
│   ├── SendMessage.vue         # 发送消息
│   ├── History.vue             # 发送历史
│   ├── Users.vue               # 用户管理
│   ├── WeComConfig.vue         # 企业微信配置
│   └── Settings.vue            # 系统设置
│
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
└── README.md                   # 项目说明
```

---

## 🔧 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **SQLAlchemy** - ORM 框架
- **APScheduler** - 定时任务调度
- **SQLite/MySQL/PostgreSQL** - 数据库支持
- **Pydantic** - 数据验证

### 前端
- **Vue 3** - 渐进式框架
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `WECOM_BOT_WEBHOOK_KEY` | 企业微信 Webhook Key | - | ✅ |
| `DATABASE_TYPE` | 数据库类型 | sqlite | ❌ |
| `SQLITE_DB_PATH` | SQLite 数据库路径 | ./data/wecom_bot.db | ❌ |
| `MYSQL_HOST` | MySQL 主机地址 | localhost | ❌ |
| `MYSQL_PORT` | MySQL 端口 | 3306 | ❌ |
| `MYSQL_USER` | MySQL 用户名 | root | ❌ |
| `MYSQL_PASSWORD` | MySQL 密码 | - | ❌ |
| `MYSQL_DATABASE` | MySQL 数据库名 | wecom_bot | ❌ |
| `HOST` | 服务器监听地址 | 0.0.0.0 | ❌ |
| `PORT` | 服务器端口 | 8000 | ❌ |
| `LOG_LEVEL` | 日志级别 | INFO | ❌ |

---

## 🎨 界面预览

### 定时任务管理页面
- 任务列表表格
- 搜索和筛选
- 创建/编辑任务对话框
- 执行历史查看
- 立即执行按钮

### HR 数据集成页面
- HR 系统配置卡片
- 员工信息表格
- 员工搜索和筛选
- 统计数据展示
- 生日和周年徽章
- 添加/编辑员工对话框

---

## 📝 注意事项

1. **企业微信 ID 绑定**
   - 员工的 `wecom_userid` 必须正确填写
   - 否则无法发送消息给该员工

2. **生日和入职日期**
   - 必须正确填写才能使用生日祝福和周年纪念功能
   - 日期格式：YYYY-MM-DD

3. **定时任务执行**
   - 任务状态必须是「启用」才会执行
   - 系统重启后会自动加载所有启用的任务

4. **数据库选择**
   - 开发测试建议使用 SQLite
   - 生产环境建议使用 MySQL 或 PostgreSQL

5. **变量替换**
   - 只有生日祝福和周年纪念任务支持变量替换
   - 确保变量名正确（包括花括号）

---

## 🐛 常见问题

### Q1: 定时任务不执行？

**A:** 检查以下几点：
1. 任务状态是否为「启用」
2. 执行计划是否正确设置
3. 后端服务是否正常运行
4. 查看后端日志是否有错误

### Q2: 员工数据无法同步？

**A:** 检查以下几点：
1. HR 系统配置是否正确
2. 网络连接是否正常
3. API Token 是否有效
4. 数据库连接信息是否正确

### Q3: 生日祝福没有发送？

**A:** 检查以下几点：
1. 员工生日是否正确填写
2. 员工企业微信 ID 是否绑定
3. 员工状态是否为「在职」
4. 定时任务是否启用

### Q4: 变量没有替换？

**A:** 检查以下几点：
1. 变量名是否正确（包括花括号）
2. 任务类型是否为 birthday 或 anniversary
3. 员工信息是否完整

---

## 📊 数据库迁移

如需更换数据库类型，可以使用以下命令导出数据并导入新数据库：

```bash
# 导出 SQLite 数据
sqlite3 data/wecom_bot.db ".dump" > backup.sql

# 导入 MySQL
mysql -u root -p wecom_bot < backup.sql
```

---

## 🎉 总结

现在你拥有了一个功能完整的企业微信机器人定时任务系统：

✅ **定时任务管理** - 支持多种任务类型和执行计划  
✅ **HR 数据集成** - 完整的员工信息管理  
✅ **数据库支持** - SQLite/MySQL/PostgreSQL  
✅ **生日祝福** - 自动发送生日祝福  
✅ **入职周年** - 自动发送周年纪念  
✅ **发送记录** - 完整的发送历史  
✅ **API 接口** - RESTful API  
✅ **Web 界面** - 美观的管理界面  

**立即体验：**
```bash
cd <workspace>\workwx-api\wecom-bot-server
start.bat
```

访问 http://localhost:3001 开始使用！

---

**创建时间：** 2026-03-16  
**版本：** v3.0.0  
**状态：** ✅ 生产就绪
