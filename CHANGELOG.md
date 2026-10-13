# 更新日志

本项目在公开发布前的开发历史未逐条迁移到本仓库；以下记录自首次公开发布起的版本变更。

## [1.0.0] - 2026-10-13

首次公开发布。

### 主要能力

- MCP 工具集：内置 send_text、send_markdown、send_image、send_news、send_template_card、upload_file 六个 MCP 工具，可被支持 MCP 的客户端直接调用。
- 群机器人消息发送：支持文本、Markdown、图片（Base64）、图文与模板卡片等多类型消息推送。
- 文件上传：支持把本地文件上传至平台换取 media_id，覆盖常用文档与图片类型。
- REST API 服务：基于 FastAPI 提供 /api/v1/text、/api/v1/markdown、/api/v1/image、/api/v1/news、/api/v1/template-card、/api/v1/upload-file 与 /api/v1/bot-info 等接口。
- WebSocket 双通道：在 REST 之外提供 /ws 通道，支持按 type 发送各类消息、以 request_id 关联响应以及心跳保活。
- 自动接口文档：内置 Swagger/OpenAPI 文档与健康检查接口。
- 类型安全校验：使用 Pydantic 模型校验请求参数与运行配置。
- 登录认证：提供登录页面、密码加密存储、JWT 认证、前端路由守卫与会话管理。
- 定时任务调度：支持创建与管理定时任务并记录执行历史，可用于定时群发等场景。
- HR 数据集成：支持员工档案维护、HR 数据同步配置与同步历史记录，可用于生日祝福、入职周年等自动关怀。
- 消息历史：持久化消息发送记录，前端可查询、搜索、筛选并导出 CSV。
- Web 管理后台：Vue 3 + Element Plus 前端，含控制台、发送消息、发送历史、定时任务、资源管理、HR 集成、用户管理、配置与系统设置页面。
- 多数据库支持：通过 DATABASE_TYPE 在 SQLite、MySQL 与 PostgreSQL 之间切换，使用 SQLAlchemy 模型与 Alembic 迁移。
- 多种部署方式：提供 Dockerfile、Docker Compose 与 Nginx 配置，并支持容器化与无服务器部署。
- 测试覆盖：包含客户端、配置、模型与路由的 pytest 用例，并配置覆盖率统计。

### 已知限制

- 发送历史页面的「重发」功能尚未实现，当前仅提示开发中（BUGFIX_REPORT.md）。
- 前端图片 MD5 使用简化哈希函数替代，并非标准 MD5（BUGFIX_REPORT.md）。
- 接口文档中将 Python SDK 与 Node.js SDK 标注为「待实现」（API_DOCUMENTATION.md）。
- 多机器人支持、配置导入导出、国际化与主题切换等在后台文档中列为待完善项（FULL_BACKEND_COMPLETE.md）。
- 定时任务向员工投递消息依赖员工记录中的 wecom_userid 正确绑定，否则无法发送（SCHEDULER_HR_FEATURES.md）。
- 消息发送受平台频率限制，需自行控制调用频率（QUICKSTART.md）。
- 部署方式见 README，凭据请自行配置。

### 许可证

- 见 [LICENSE](LICENSE)。
