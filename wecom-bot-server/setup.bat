@echo off
chcp 65001 >nul
echo ====================================
echo   企业微信机器人配置工具
echo ====================================
echo.

:input_key
set /p WEBHOOK_KEY=请输入企业微信机器人 Webhook Key: 
if "%WEBHOOK_KEY%"=="" (
    echo 错误：Webhook Key 不能为空！
    echo.
    goto input_key
)

echo.
echo 正在配置...
echo.

REM 创建或更新 .env 文件
(
echo # 企业微信机器人配置
echo WECOM_BOT_WEBHOOK_KEY=%WEBHOOK_KEY%
echo.
echo # 服务器配置
echo HOST=0.0.0.0
echo PORT=8000
echo LOG_LEVEL=INFO
) > .env

echo ✓ 配置文件已保存到 .env
echo.
echo ====================================
echo   配置完成！
echo ====================================
echo.
echo 下一步：
echo 1. 启动后端服务：python -m uvicorn wecom_bot.main:app --reload
echo 2. 启动前端服务：cd web ^&^& npm run dev
echo 3. 访问：http://localhost:3000
echo.
pause
