@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   电商AI系统 - Windows 一键启动脚本
echo ============================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: 检查虚拟环境
if not exist "%PROJECT_DIR%backend\.venv\Scripts\activate.bat" (
    echo [错误] 未找到后端虚拟环境。
    echo 请先运行 setup.bat 完成环境配置。
    pause
    exit /b 1
)

:: 检查前端依赖
if not exist "%PROJECT_DIR%frontend\node_modules" (
    echo [错误] 未找到前端 node_modules。
    echo 请先运行 setup.bat 完成环境配置。
    pause
    exit /b 1
)

:: 检查 .env
if not exist "%PROJECT_DIR%backend\.env" (
    echo [警告] 未找到 backend\.env 文件。
    echo 请先运行 setup.bat，或手动复制 backend\.env.example 为 backend\.env 并填入 DeepSeek API Key。
    pause
    exit /b 1
)

echo 正在启动后端服务...
echo   地址：http://127.0.0.1:8000
echo   API 文档：http://127.0.0.1:8000/docs
start "电商AI后端服务" cmd /k "cd /d "%PROJECT_DIR%backend" && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo 正在启动前端开发服务器...
echo   地址：http://localhost:5173
start "电商AI前端服务" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm run dev"

echo.
echo ============================================
echo   服务启动命令已发送
echo ============================================
echo.
echo 请稍候 3-5 秒，然后打开浏览器访问：
echo   前台页面：http://localhost:5173
echo   后台 API：http://127.0.0.1:8000/docs
echo.
echo 默认账号：
echo   商家管理员：merchant / 123456
echo   普通用户：   user / 123456
echo.
echo 提示：
echo   关闭弹出的两个命令行窗口即可停止服务。
echo.
pause
