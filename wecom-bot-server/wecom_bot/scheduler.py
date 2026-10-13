"""
定时任务调度器
使用 APScheduler 进行任务调度
"""

import asyncio
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import ScheduledTask, Employee, TaskExecutionHistory
from .client import WeComBotClient


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self, db_session_func, wecom_client: WeComBotClient):
        self.scheduler = AsyncIOScheduler()
        self.db_session_func = db_session_func
        self.wecom_client = wecom_client
        self.running = False
    
    def start(self):
        """启动调度器"""
        if not self.running:
            self.scheduler.start()
            self.running = True
            print("✅ 定时任务调度器已启动")
    
    def shutdown(self, wait=True):
        """关闭调度器"""
        if self.running:
            self.scheduler.shutdown(wait=wait)
            self.running = False
            print("🛑 定时任务调度器已关闭")
    
    def load_tasks(self):
        """从数据库加载所有启用的任务"""
        db = next(self.db_session_func())
        try:
            tasks = db.query(ScheduledTask).filter(
                and_(
                    ScheduledTask.status == True,
                    ScheduledTask.next_run != None
                )
            ).all()
            
            for task in tasks:
                self.add_task(task)
            
            print(f"📋 已加载 {len(tasks)} 个定时任务")
        finally:
            db.close()
    
    def add_task(self, task: ScheduledTask):
        """添加定时任务到调度器"""
        trigger = self.create_trigger(task)
        
        if trigger:
            job_id = f"task_{task.id}"
            
            # 如果任务已存在，先移除
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # 添加新任务
            self.scheduler.add_job(
                self.execute_task,
                trigger=trigger,
                id=job_id,
                args=[task.id],
                replace_existing=True,
                next_run_time=task.next_run
            )
            
            print(f"⏰ 任务已添加：{task.name} (下次执行：{task.next_run})")
    
    def create_trigger(self, task: ScheduledTask):
        """根据任务配置创建触发器"""
        schedule_type = task.schedule_type
        
        if schedule_type == 'once':
            # 一次性执行
            try:
                run_date = datetime.strptime(task.schedule, '%Y-%m-%d %H:%M:%S')
                return DateTrigger(run_date=run_date)
            except Exception as e:
                print(f"❌ 创建一次性触发器失败：{e}")
                return None
        
        elif schedule_type == 'minute':
            # 每分钟
            try:
                return IntervalTrigger(minutes=1)
            except Exception as e:
                print(f"❌ 创建分钟触发器失败：{e}")
                return None
        
        elif schedule_type == 'hour':
            # 每小时
            try:
                return IntervalTrigger(hours=1)
            except Exception as e:
                print(f"❌ 创建小时触发器失败：{e}")
                return None
        
        elif schedule_type == 'day':
            # 每天
            try:
                hour, minute = map(int, task.schedule.split(':'))
                return CronTrigger(hour=hour, minute=minute)
            except Exception as e:
                print(f"❌ 创建日触发器失败：{e}")
                return None
        
        elif schedule_type == 'week':
            # 每周
            try:
                hour, minute = map(int, task.schedule.split(':'))
                return CronTrigger(day_of_week=task.weekday, hour=hour, minute=minute)
            except Exception as e:
                print(f"❌ 创建周触发器失败：{e}")
                return None
        
        elif schedule_type == 'month':
            # 每月
            try:
                hour, minute = map(int, task.schedule.split(':'))
                return CronTrigger(day=task.day, hour=hour, minute=minute)
            except Exception as e:
                print(f"❌ 创建月触发器失败：{e}")
                return None
        
        elif schedule_type == 'cron':
            # Cron 表达式
            try:
                # 解析 Cron 表达式：分 时 日 月 星期
                minute, hour, day, month, weekday = task.schedule.split()
                return CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=weekday
                )
            except Exception as e:
                print(f"❌ 创建 Cron 触发器失败：{e}")
                return None
        
        return None
    
    async def execute_task(self, task_id: int):
        """执行定时任务"""
        db = next(self.db_session_func())
        try:
            task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
            
            if not task or not task.status:
                print(f"⚠️ 任务不存在或已禁用：{task_id}")
                return
            
            print(f"🚀 开始执行任务：{task.name}")
            
            # 获取接收者
            recipients = self.get_recipients(db, task)
            
            if not recipients:
                print(f"⚠️ 没有接收者：{task.name}")
                return
            
            # 发送消息
            success_count = 0
            error_message = None
            
            try:
                for recipient in recipients:
                    await self.send_message(task, recipient)
                    success_count += 1
                
                status = True
                message = f"发送成功，共 {success_count} 人"
                
            except Exception as e:
                status = False
                error_message = str(e)
                message = f"发送失败：{e}"
            
            # 记录执行历史
            history = TaskExecutionHistory(
                task_id=task_id,
                scheduled_time=task.next_run,
                actual_time=datetime.utcnow(),
                status=status,
                message=message,
                recipients_count=success_count,
                error_message=error_message
            )
            db.add(history)
            
            # 更新任务最后执行时间
            task.last_run = datetime.utcnow()
            task.next_run = self.calculate_next_run(task)
            
            db.commit()
            
            print(f"✅ 任务执行完成：{task.name}, 成功：{success_count}/{len(recipients)}")
            
        except Exception as e:
            print(f"❌ 任务执行失败：{task_id}, 错误：{e}")
            db.rollback()
        finally:
            db.close()
    
    def get_recipients(self, db: Session, task: ScheduledTask):
        """获取任务接收者"""
        if task.recipient_type == 'all':
            # 所有在职员工
            recipients = db.query(Employee).filter(
                and_(
                    Employee.status == True,
                    Employee.wecom_userid != None
                )
            ).all()
        
        elif task.recipient_type == 'department':
            # 指定部门的员工
            dept_ids = task.recipient_ids or []
            recipients = db.query(Employee).filter(
                and_(
                    Employee.status == True,
                    Employee.department.in_(dept_ids),
                    Employee.wecom_userid != None
                )
            ).all()
        
        elif task.recipient_type == 'specific':
            # 指定员工
            user_ids = task.recipient_ids or []
            recipients = db.query(Employee).filter(
                and_(
                    Employee.status == True,
                    Employee.wecom_userid.in_(user_ids)
                )
            ).all()
        
        else:
            recipients = []
        
        return recipients
    
    async def send_message(self, task: ScheduledTask, employee: Employee):
        """发送消息给员工"""
        # 替换消息内容中的变量
        content = self.replace_variables(task.content, employee)
        
        if task.message_type == 'text':
            await self.wecom_client.send_text(
                content=content,
                mentioned_mobile_list=[employee.phone] if employee.phone else None
            )
        
        elif task.message_type == 'markdown':
            await self.wecom_client.send_markdown(content=content)
        
        elif task.message_type == 'news':
            # 图文消息
            articles = task.content_json.get('articles', [])
            if articles:
                await self.wecom_client.send_news(articles=articles)
        
        elif task.message_type == 'card':
            # 卡片消息
            card_data = task.content_json or {}
            await self.wecom_client.send_textcard(
                title=card_data.get('mainTitle', ''),
                description=card_data.get('mainDesc', ''),
                url=card_data.get('url', '#')
            )
    
    def replace_variables(self, content: str, employee: Employee) -> str:
        """替换消息内容中的变量"""
        if not content:
            return content
        
        # 计算年龄
        age = self.calculate_age(employee.birthday) if employee.birthday else 0
        
        # 计算工龄
        work_years = self.calculate_work_years(employee.hire_date) if employee.hire_date else 0
        
        # 替换变量
        replacements = {
            '{name}': employee.name,
            '{employee_id}': employee.employee_id,
            '{department}': employee.department,
            '{position}': employee.position,
            '{birthday}': employee.birthday.strftime('%Y-%m-%d') if employee.birthday else '',
            '{age}': str(age),
            '{hire_date}': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
            '{work_years}': str(work_years)
        }
        
        result = content
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        return result
    
    def calculate_age(self, birthday) -> int:
        """计算年龄"""
        if not birthday:
            return 0
        
        today = datetime.today()
        age = today.year - birthday.year
        
        # 检查是否已经过了生日
        if (today.month, today.day) < (birthday.month, birthday.day):
            age -= 1
        
        return age
    
    def calculate_work_years(self, hire_date) -> int:
        """计算工龄"""
        if not hire_date:
            return 0
        
        today = datetime.today()
        years = today.year - hire_date.year
        
        # 检查是否已经过了入职纪念日
        if (today.month, today.day) < (hire_date.month, hire_date.day):
            years -= 1
        
        return max(0, years)
    
    def calculate_next_run(self, task: ScheduledTask) -> Optional[datetime]:
        """计算下次执行时间"""
        job = self.scheduler.get_job(f"task_{task.id}")
        if job and job.next_run_time:
            return job.next_run_time
        return None
    
    def remove_task(self, task_id: int):
        """移除定时任务"""
        job_id = f"task_{task_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            print(f"🗑️ 任务已移除：{task_id}")
    
    def get_job(self, task_id: int):
        """获取任务信息"""
        job_id = f"task_{task_id}"
        return self.scheduler.get_job(job_id)


# 全局调度器实例
scheduler: Optional[TaskScheduler] = None


def get_scheduler() -> Optional[TaskScheduler]:
    """获取调度器实例"""
    return scheduler


def init_scheduler(db_session_func, wecom_client: WeComBotClient):
    """初始化调度器"""
    global scheduler
    scheduler = TaskScheduler(db_session_func, wecom_client)
    scheduler.load_tasks()
    scheduler.start()
    return scheduler
