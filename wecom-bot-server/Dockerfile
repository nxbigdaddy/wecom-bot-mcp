# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 运行时镜像
FROM python:3.11-slim

WORKDIR /app

# 创建非 root 用户
RUN useradd -m -u 1000 wecombot && \
    mkdir -p /app/data && \
    chown -R wecombot:wecombot /app

# 从 builder 阶段复制依赖
COPY --from=builder /root/.local /home/wecombot/.local

# 复制应用代码
COPY --chown=wecombot:wecombot . .

# 设置环境变量
ENV PATH=/home/wecombot/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 切换到非 root 用户
USER wecombot

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["uvicorn", "wecom_bot.main:app", "--host", "0.0.0.0", "--port", "8000"]
