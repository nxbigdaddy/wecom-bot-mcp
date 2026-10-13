"""
数据库模型定义
用户、员工、定时任务、发送记录等
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='user')  # admin, user, guest
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    tasks = relationship("ScheduledTask", back_populates="creator")
    message_history = relationship("MessageHistory", back_populates="sender")


class Employee(Base):
    """员工信息表"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)  # 工号
    name = Column(String(50), nullable=False, index=True)
    gender = Column(String(10))  # 男，女
    birthday = Column(Date, index=True)  # 生日
    department = Column(String(100), index=True)
    position = Column(String(100))
    hire_date = Column(Date)  # 入职日期
    email = Column(String(100))
    phone = Column(String(20))
    wecom_userid = Column(String(100), index=True)  # 企业微信用户 ID
    status = Column(Boolean, default=True)  # 在职/离职
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduledTask(Base):
    """定时任务表"""
    __tablename__ = 'scheduled_tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # 任务名称
    description = Column(Text)  # 任务描述
    task_type = Column(String(50), nullable=False)  # birthday, anniversary, custom
    message_type = Column(String(20), nullable=False)  # text, markdown, image, news, card
    schedule_type = Column(String(20), nullable=False)  # once, minute, hour, day, week, month, cron
    schedule = Column(String(100), nullable=False)  # 执行时间或 Cron 表达式
    weekday = Column(Integer)  # 星期几（week 类型使用）
    day = Column(Integer)  # 几号（month 类型使用）
    status = Column(Boolean, default=True)  # 启用/禁用
    content = Column(Text)  # 消息内容
    content_json = Column(JSON)  # 复杂消息内容（图文、卡片）
    recipient_type = Column(String(20), default='all')  # all, department, specific
    recipient_ids = Column(JSON)  # 接收者 ID 列表
    creator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = Column(DateTime)  # 上次执行时间
    next_run = Column(DateTime)  # 下次执行时间
    
    # 关联
    creator = relationship("User", back_populates="tasks")
    execution_history = relationship("TaskExecutionHistory", back_populates="task")


class TaskExecutionHistory(Base):
    """任务执行历史表"""
    __tablename__ = 'task_execution_history'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('scheduled_tasks.id'), nullable=False)
    scheduled_time = Column(DateTime)  # 计划执行时间
    actual_time = Column(DateTime, default=datetime.utcnow)  # 实际执行时间
    status = Column(Boolean)  # 执行成功/失败
    message = Column(Text)  # 执行结果消息
    recipients_count = Column(Integer)  # 接收者数量
    error_message = Column(Text)  # 错误信息
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    task = relationship("ScheduledTask", back_populates="execution_history")


class MessageHistory(Base):
    """消息发送历史表"""
    __tablename__ = 'message_history'
    
    id = Column(Integer, primary_key=True, index=True)
    message_type = Column(String(20), nullable=False)
    content = Column(Text)
    content_json = Column(JSON)
    recipients = Column(JSON)  # 接收者列表
    status = Column(Boolean, default=True)  # 发送成功/失败
    error_message = Column(Text)
    sender_id = Column(Integer, ForeignKey('users.id'))
    sent_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50), default='manual')  # manual, scheduled, api
    
    # 关联
    sender = relationship("User", back_populates="message_history")


class HRConfig(Base):
    """HR 系统配置表"""
    __tablename__ = 'hr_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    system_type = Column(String(50))  # dingtalk, wecom, feishu, beisen, knx, custom
    sync_mode = Column(String(20))  # api, csv, excel, database
    api_url = Column(String(500))
    api_token = YOUR_SECRET))
    db_type = Column(String(20))  # mysql, postgresql, sqlserver, oracle
    db_host = Column(String(100))
    db_port = Column(String(10))
    db_name = Column(String(100))
    db_user = Column(String(100))
    db_password = YOUR_PASSWORD))
    table_name = Column(String(100))
    sync_frequency = Column(String(20), default='daily')  # hourly, daily, weekly, monthly, manual
    last_sync = Column(DateTime)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SyncHistory(Base):
    """数据同步历史表"""
    __tablename__ = 'sync_history'
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50))  # API, CSV, Excel, Database
    added_count = Column(Integer, default=0)  # 新增数量
    updated_count = Column(Integer, default=0)  # 更新数量
    deleted_count = Column(Integer, default=0)  # 删除数量
    status = Column(Boolean, default=True)  # 同步成功/失败
    message = Column(Text)  # 同步结果详情
    created_at = Column(DateTime, default=datetime.utcnow)
