"""
数据库配置和连接管理
支持 SQLite、MySQL、PostgreSQL
"""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# 数据库类型
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
DATABASE_URL = os.getenv('DATABASE_URL', '')

# SQLite 配置
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', './data/wecom_bot.db')

# MySQL 配置
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = YOUR_PASSWORD'MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'wecom_bot')

# PostgreSQL 配置
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = YOUR_PASSWORD'POSTGRES_PASSWORD', '')
POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE', 'wecom_bot')


def get_database_url() -> str:
    """获取数据库连接 URL"""
    if DATABASE_TYPE == 'mysql':
        return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    elif DATABASE_TYPE == 'postgresql':
        return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    else:  # sqlite
        return f"sqlite:///{SQLITE_DB_PATH}"


# 创建数据库引擎
engine = create_engine(
    get_database_url(),
    echo=False,  # 生产环境关闭 SQL 日志
    pool_pre_ping=True,  # 连接前 ping 测试
    pool_size=10,  # 连接池大小
    max_overflow=20  # 最大溢出连接数
)

# 创建 Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Session:
    """获取数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    # 导入所有模型以确保它们被注册到 Base
    from .models import User, Employee, ScheduledTask, TaskExecutionHistory, MessageHistory, HRConfig
    
    # 创建表
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库初始化成功 ({DATABASE_TYPE})")


if __name__ == "__main__":
    # 测试数据库连接
    try:
        with engine.connect() as conn:
            print(f"✅ 数据库连接成功：{DATABASE_TYPE}")
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
