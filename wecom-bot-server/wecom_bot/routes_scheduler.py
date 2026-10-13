"""
定时任务和 HR 集成相关的路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date
import csv
import io
import pandas as pd

from .database import get_db, SessionLocal
from .models import ScheduledTask, Employee, HRConfig, SyncHistory, TaskExecutionHistory, User
from .scheduler import get_scheduler
from .schemas import (
    ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskResponse,
    TaskExecutionHistoryResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    HRConfigCreate, HRConfigUpdate, HRConfigResponse,
    SyncHistoryResponse,
    SuccessResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/v1", tags=["scheduler", "hr"])


@router.get("/tasks", response_model=List[ScheduledTaskResponse], summary="获取定时任务列表")
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[bool] = None,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取所有定时任务"""
    query = db.query(ScheduledTask)
    
    if status_filter is not None:
        query = query.filter(ScheduledTask.status == status_filter)
    
    if task_type:
        query = query.filter(ScheduledTask.task_type == task_type)
    
    tasks = query.order_by(ScheduledTask.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=ScheduledTaskResponse, summary="获取任务详情")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取指定任务详情"""
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/tasks", response_model=ScheduledTaskResponse, status_code=status.HTTP_201_CREATED, summary="创建定时任务")
async def create_task(task: ScheduledTaskCreate, db: Session = Depends(get_db)):
    """创建新的定时任务"""
    # 计算下次执行时间
    next_run = calculate_next_run(task)
    
    db_task = ScheduledTask(
        **task.model_dump(),
        next_run=next_run
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 添加到调度器
    scheduler = get_scheduler()
    if scheduler:
        scheduler.add_task(db_task)
    
    return db_task


@router.put("/tasks/{task_id}", response_model=ScheduledTaskResponse, summary="更新定时任务")
async def update_task(task_id: int, task: ScheduledTaskUpdate, db: Session = Depends(get_db)):
    """更新指定任务"""
    db_task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新字段
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    # 重新计算下次执行时间
    if any(key in ['schedule_type', 'schedule', 'weekday', 'day'] for key in update_data):
        db_task.next_run = calculate_next_run(db_task)
    
    db.commit()
    db.refresh(db_task)
    
    # 更新调度器
    scheduler = get_scheduler()
    if scheduler:
        scheduler.add_task(db_task)
    
    return db_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除定时任务")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除指定任务"""
    db_task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 从调度器移除
    scheduler = get_scheduler()
    if scheduler:
        scheduler.remove_task(task_id)
    
    db.delete(db_task)
    db.commit()
    
    return None


@router.post("/tasks/{task_id}/run", summary="立即执行任务")
async def run_task_now(task_id: int, db: Session = Depends(get_db)):
    """立即执行指定任务"""
    db_task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if not db_task.status:
        raise HTTPException(status_code=400, detail="任务已禁用")
    
    # TODO: 异步执行任务
    # 这里应该调用调度器的 execute_task 方法
    # 由于是异步的，需要适当处理
    
    return {"message": "任务执行中", "task_id": task_id}


@router.get("/tasks/{task_id}/history", summary="获取任务执行历史")
async def get_task_history(
    task_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取任务执行历史记录"""
    history = db.query(TaskExecutionHistory).filter(
        TaskExecutionHistory.task_id == task_id
    ).order_by(
        TaskExecutionHistory.actual_time.desc()
    ).offset(skip).limit(limit).all()
    
    return history


# ==================== 员工管理相关 ====================

@router.get("/employees", response_model=List[EmployeeResponse], summary="获取员工列表")
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    department: Optional[str] = None,
    status_filter: Optional[bool] = None,
    birthday_start: Optional[date] = None,
    birthday_end: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取员工列表，支持搜索和筛选"""
    query = db.query(Employee)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                Employee.name.like(f"%{search}%"),
                Employee.employee_id.like(f"%{search}%"),
                Employee.department.like(f"%{search}%")
            )
        )
    
    # 部门筛选
    if department:
        query = query.filter(Employee.department == department)
    
    # 状态筛选
    if status_filter is not None:
        query = query.filter(Employee.status == status_filter)
    
    # 生日范围筛选
    if birthday_start and birthday_end:
        query = query.filter(
            and_(
                Employee.birthday >= birthday_start,
                Employee.birthday <= birthday_end
            )
        )
    
    employees = query.order_by(Employee.employee_id).offset(skip).limit(limit).all()
    return employees


@router.get("/employees/{employee_id}", response_model=EmployeeResponse, summary="获取员工详情")
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """获取指定员工详情"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    return employee


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, summary="添加员工")
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """添加新员工"""
    # 检查工号是否已存在
    existing = db.query(Employee).filter(
        Employee.employee_id == employee.employee_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="工号已存在")
    
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return db_employee


@router.put("/employees/{employee_id}", response_model=EmployeeResponse, summary="更新员工信息")
async def update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """更新员工信息"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    update_data = employee.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    
    return db_employee


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除员工")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """删除员工"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    db.delete(db_employee)
    db.commit()
    
    return None


@router.get("/employees/birthday/today", response_model=List[EmployeeResponse], summary="获取今日生日员工")
async def get_today_birthday_employees(db: Session = Depends(get_db)):
    """获取今天生日的员工"""
    today = datetime.today().strftime('%m-%d')
    
    employees = db.query(Employee).filter(
        and_(
            Employee.status == True,
            db.func.strftime('%m-%d', Employee.birthday) == today
        )
    ).all()
    
    return employees


@router.get("/employees/birthday/week", response_model=List[EmployeeResponse], summary="获取本周生日员工")
async def get_week_birthday_employees(db: Session = Depends(get_db)):
    """获取本周生日的员工"""
    # 简化实现，实际应该计算本周的日期范围
    today = datetime.today()
    employees = db.query(Employee).filter(
        and_(
            Employee.status == True,
            Employee.birthday != None
        )
    ).all()
    
    # 过滤本周生日
    week_birthdays = []
    for emp in employees:
        if emp.birthday:
            # TODO: 实现本周判断逻辑
            pass
    
    return week_birthdays[:10]  # 临时返回


@router.get("/employees/anniversary/upcoming", response_model=List[EmployeeResponse], summary="获取即将入职周年员工")
async def get_upcoming_anniversary_employees(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """获取即将入职周年的员工"""
    # TODO: 实现即将入职周年的判断逻辑
    return []


# ==================== HR 配置相关 ====================

@router.get("/hr-config", response_model=Optional[HRConfigResponse], summary="获取 HR 配置")
async def get_hr_config(db: Session = Depends(get_db)):
    """获取 HR 系统配置"""
    config = db.query(HRConfig).first()
    return config


@router.post("/hr-config", response_model=HRConfigResponse, summary="保存 HR 配置")
async def save_hr_config(config: HRConfigCreate, db: Session = Depends(get_db)):
    """保存 HR 系统配置"""
    db_config = db.query(HRConfig).first()
    
    if db_config:
        # 更新
        update_data = config.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_config, key, value)
    else:
        # 创建
        db_config = HRConfig(**config.model_dump())
        db.add(db_config)
    
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.post("/hr-config/sync", summary="立即同步 HR 数据")
async def sync_hr_data(db: Session = Depends(get_db)):
    """立即同步 HR 系统数据"""
    # TODO: 实现 HR 数据同步逻辑
    return {"message": "同步中...", "status": "processing"}


@router.get("/hr-config/sync-history", summary="获取同步历史")
async def get_sync_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取 HR 数据同步历史"""
    history = db.query(SyncHistory).order_by(
        SyncHistory.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return history


# ==================== 辅助函数 ====================

from sqlalchemy import or_


def calculate_next_run(task) -> Optional[datetime]:
    """计算下次执行时间"""
    # 简化实现，实际应该根据 schedule_type 计算
    from datetime import timedelta
    
    if task.schedule_type == 'once':
        try:
            return datetime.strptime(task.schedule, '%Y-%m-%d %H:%M:%S')
        except:
            return None
    
    elif task.schedule_type == 'minute':
        return datetime.utcnow() + timedelta(minutes=1)
    
    elif task.schedule_type == 'hour':
        return datetime.utcnow() + timedelta(hours=1)
    
    elif task.schedule_type == 'day':
        # 明天的指定时间
        try:
            hour, minute = map(int, task.schedule.split(':'))
            tomorrow = datetime.utcnow().replace(hour=hour, minute=minute, second=0) + timedelta(days=1)
            return tomorrow
        except:
            return None
    
    # TODO: 完善其他类型的计算
    return None
