#!/bin/bash

# 启动脚本
set -e

echo "========================================"
echo "WeCom Bot Server 启动脚本"
echo "========================================"

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

echo "Python 版本：$python_version"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ -z "$WECOM_BOT_WEBHOOK_KEY" ]; then
    echo "警告：WECOM_BOT_WEBHOOK_KEY 环境变量未设置"
    echo "请从 .env 文件加载或手动设置"
    
    if [ -f ".env" ]; then
        echo "从 .env 文件加载配置..."
        export $(cat .env | grep -v '^#' | xargs)
    fi
fi

# 启动服务
echo "启动服务..."
echo "访问 API 文档：http://localhost:8000/docs"
echo "健康检查：http://localhost:8000/health"
echo ""

uvicorn wecom_bot.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload
