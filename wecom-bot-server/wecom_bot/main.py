"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from .config import settings
from .routes import router
from .routes_scheduler import router as scheduler_router
from .routes_auth import router as auth_router
from .websocket import websocket_handler, ws_manager
from .exceptions import WeComBotException
from .database import init_db, get_db
from .scheduler import init_scheduler
from .client import WeComBotClient

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI 应用实例
    """
    # 启动时执行
    logger.info("WeCom Bot Server is starting...")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Webhook Key: {settings.wecom_bot_webhook_key[:8]}...")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败：{e}")
    
    # 初始化管理员账号
    try:
        from sqlalchemy.orm import Session
        from .models import User
        from .database import SessionLocal
        import hashlib
        
        db = SessionLocal()
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            # 创建默认管理员
            admin_user = User(
                username="admin",
                email="admin@example.com",
                phone="",
                password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
                role="admin",
                status=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("✅ 默认管理员账号已创建 (admin/admin123)")
        else:
            logger.info("✅ 管理员账号已存在")
        
        db.close()
    except Exception as e:
        logger.error(f"❌ 管理员账号初始化失败：{e}")
    
    # 初始化定时任务调度器
    try:
        from functools import partial
        db_session_func = partial(get_db)
        wecom_client = WeComBotClient()
        init_scheduler(db_session_func, wecom_client)
        logger.info("✅ 定时任务调度器初始化成功")
    except Exception as e:
        logger.error(f"❌ 调度器初始化失败：{e}")
    
    yield
    
    # 关闭时执行
    logger.info("WeCom Bot Server is shutting down...")
    logger.info(f"Active WebSocket connections: {ws_manager.get_connection_count()}")


# 创建 FastAPI 应用
app = FastAPI(
    title="WeCom Bot Server",
    description="""
## 企业微信机器人服务器

支持通过 REST API 和 WebSocket 发送各种类型的消息到企业微信群。

### 功能特性

- ✅ **文本消息** - 发送文本消息，支持@成员
- ✅ **Markdown 消息** - 发送格式化 Markdown 消息
- ✅ **图片消息** - 发送 Base64 编码的图片
- ✅ **图文消息** - 发送图文卡片消息
- ✅ **模板卡片** - 发送交互式卡片消息
- ✅ **文件上传** - 上传文件到企业微信
- ✅ **WebSocket** - 支持实时双向通信
- ✅ **REST API** - 完整的 RESTful 接口

### 快速开始

1. 设置环境变量 `WECOM_BOT_WEBHOOK_KEY`
2. 启动服务：`uvicorn wecom_bot.main:app --host 0.0.0.0 --port 8000`
3. 访问 API 文档：http://localhost:8000/docs

### 认证

所有请求都需要在环境变量中配置 Webhook Key。
    """,
    version="1.0.0",
    contact={
        "name": "WeCom Bot Server",
        "url": "https://github.com/yourusername/wecom-bot-server",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response


# 全局异常处理
@app.exception_handler(WeComBotException)
async def wecom_exception_handler(request: Request, exc: WeComBotException):
    """处理企业微信机器人异常"""
    logger.error(f"WeComBotException: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.log_level == "DEBUG" else None
        }
    )


# 注册路由
app.include_router(router)
app.include_router(scheduler_router)
app.include_router(auth_router)


# WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 连接端点
    
    连接到 WebSocket: ws://localhost:8000/ws
    """
    await websocket_handler(websocket)


# 健康检查端点
@app.get("/health", tags=["health"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "websocket_connections": ws_manager.get_connection_count()
    }


# 根路径
@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "name": "WeCom Bot Server",
        "version": "1.0.0",
        "description": "企业微信机器人服务器",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws"
    }


def create_app():
    """创建应用实例（用于生产部署）"""
    return app
