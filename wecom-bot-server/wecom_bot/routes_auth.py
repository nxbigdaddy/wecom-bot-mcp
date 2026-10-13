"""
用户认证相关的路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import jwt
import hashlib

from .database import get_db
from .models import User
from .config import settings
from .schemas import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1", tags=["authentication"])

# JWT 配置
SECRET_KEY = YOUR_SECRET or "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **username**: 用户名（必填）
    - **password**: 密码（必填）
    
    返回访问令牌和用户信息
    """
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not user.status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = YOUR_SECRET
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=YOUR_SECRET,
        username=user.username,
        role=user.role
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user(
    token: str = Depends(lambda: None),  # 从 header 获取 token
    db: Session = Depends(get_db)
):
    """获取当前登录用户信息"""
    # 这里应该解析 token 获取用户信息
    # 简化实现，返回示例数据
    return UserResponse(
        id=1,
        username="admin",
        email="admin@example.com",
        role="admin",
        status=True
    )


@router.post("/logout", summary="用户登出")
async def logout():
    """用户登出"""
    # JWT 是无状态的，客户端删除 token 即可
    return {"message": "登出成功"}


@router.post("/init-admin", summary="初始化管理员账号")
async def init_admin_account(db: Session = Depends(get_db)):
    """
    初始化默认管理员账号
    
    仅在首次启动时使用
    """
    # 检查是否已有管理员
    admin = db.query(User).filter(User.username == "admin").first()
    
    if admin:
        return {"message": "管理员账号已存在"}
    
    # 创建默认管理员
    admin_user = User(
        username="admin",
        email="admin@example.com",
        phone="",
        password_hash=hash_password("admin123"),
        role="admin",
        status=True
    )
    
    db.add(admin_user)
    db.commit()
    
    return {"message": "管理员账号已创建", "username": "admin", "password": "admin123"}
