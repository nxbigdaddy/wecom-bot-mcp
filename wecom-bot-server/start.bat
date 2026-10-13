@echo off
chcp 65001 >nul
echo ====================================
echo   企业微信机器人服务器 - 启动
echo ====================================
echo.

REM 检查 .env 文件是否存在
if not exist ".env" (
    echo [警告] 未找到 .env 配置文件！
    echo.
    echo 请选择操作：
    echo 1. 立即配置 Webhook Key
    echo 2. 跳过配置直接启动
    echo.
    set /p choice="请输入选项 (1/2): "
    
    if "%choice%"=="1" (
        call setup.bat
    ) else if "%choice%"=="2" (
        echo.
        echo [提示] 启动后可能无法正常发送消息
        echo.
    ) else (
        echo 无效选项，直接启动...
    )
) else (
    echo [信息] 检测到配置文件 .env
    echo.
    REM 读取 Webhook Key（不显示）
    for /f "tokens=2 delims==" %%a in ('findstr /R "^WECOM_BOT_WEBHOOK_KEY=" .env') do set WEBHOOK_KEY=%%a
    if not defined WEBHOOK_KEY (
        echo [警告] .env 文件中未配置 WECOM_BOT_WEBHOOK_KEY
        echo.
    ) else (
        echo [信息] Webhook Key 已配置：!WEBHOOK_KEY:~0,8!...
        echo.
    )
)

echo ====================================
echo   正在启动后端服务...
echo ====================================
echo.
echo 访问 API 文档：http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn wecom_bot.main:app --reload
