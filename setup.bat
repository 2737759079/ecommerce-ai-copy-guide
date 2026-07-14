@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   电商AI系统 - Windows 环境配置脚本
echo ============================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.12 或更高版本。
    echo 下载地址：https://www.python.org/downloads/
    echo 安装时请务必勾选 "Add Python to PATH"。
    pause
    exit /b 1
)
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PY_VERSION=%%a
echo [OK] 检测到 Python %PY_VERSION%

:: 检查 Node.js / npm
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js LTS 版本。
    echo 下载地址：https://nodejs.org/
    echo 安装时请务必勾选 "Add to PATH"。
    pause
    exit /b 1
)
for /f %%a in ('node --version') do set NODE_VERSION=%%a
for /f %%a in ('npm --version') do set NPM_VERSION=%%a
echo [OK] 检测到 Node.js %NODE_VERSION%, npm %NPM_VERSION%

echo.
echo --------------------------------------------
echo  1. 配置后端 Python 虚拟环境与依赖
echo --------------------------------------------

set "VENV_DIR=%PROJECT_DIR%backend\.venv"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo 正在创建虚拟环境：%VENV_DIR%
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败。
        pause
        exit /b 1
    )
    echo [OK] 虚拟环境创建完成
) else (
    echo [OK] 虚拟环境已存在
)

echo 正在安装 / 更新后端依赖...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%PROJECT_DIR%backend\requirements.txt"
if errorlevel 1 (
    echo [错误] 安装后端依赖失败。
    pause
    exit /b 1
)
echo [OK] 后端依赖安装完成

:: 生成 .env（如果不存在）
if not exist "%PROJECT_DIR%backend\.env" (
    copy "%PROJECT_DIR%backend\.env.example" "%PROJECT_DIR%backend\.env" >nul
    echo [OK] 已生成 backend\.env 文件
) else (
    echo [OK] backend\.env 文件已存在，已跳过生成
)

echo.
echo --------------------------------------------
echo  2. 配置前端 Node 依赖
echo --------------------------------------------

cd /d "%PROJECT_DIR%frontend"
if not exist "node_modules" (
    echo 正在安装前端依赖，请稍候...
    call npm install
    if errorlevel 1 (
        echo [错误] 安装前端依赖失败。
        pause
        exit /b 1
    )
    echo [OK] 前端依赖安装完成
) else (
    echo [OK] 前端依赖已存在，执行 npm install 确保完整...
    call npm install
    echo [OK] 前端依赖检查完成
)

cd /d "%PROJECT_DIR%"

echo.
echo --------------------------------------------
echo  3. 初始化数据库与示例数据
echo --------------------------------------------

call "%VENV_DIR%\Scripts\activate.bat"
python "%PROJECT_DIR%backend\scripts\init_data.py"
if errorlevel 1 (
    echo [错误] 初始化数据失败。
    pause
    exit /b 1
)
echo [OK] 数据初始化完成

echo.
echo --------------------------------------------
echo  4. 创建上传文件目录
echo --------------------------------------------
if not exist "%PROJECT_DIR%backend\uploads" mkdir "%PROJECT_DIR%backend\uploads"
if not exist "%PROJECT_DIR%backend\uploads\images" mkdir "%PROJECT_DIR%backend\uploads\images"
if not exist "%PROJECT_DIR%backend\uploads\videos" mkdir "%PROJECT_DIR%backend\uploads\videos"
if not exist "%PROJECT_DIR%backend\uploads\avatars" mkdir "%PROJECT_DIR%backend\uploads\avatars"
if not exist "%PROJECT_DIR%backend\uploads\reviews\images" mkdir "%PROJECT_DIR%backend\uploads\reviews\images"
if not exist "%PROJECT_DIR%backend\uploads\reviews\videos" mkdir "%PROJECT_DIR%backend\uploads\reviews\videos"
echo [OK] 上传目录创建完成

echo.
echo ============================================
echo   环境配置完成！
echo ============================================
echo.
echo 默认账号：
echo   商家管理员：merchant / 123456
echo   普通用户：   user / 123456
echo.
echo 重要提示：
echo   请打开 backend\.env 文件，将 DEEPSEEK_API_KEY
echo   替换为您自己的 DeepSeek API Key，否则 AI 功能无法使用。
echo.
echo 配置完成后，双击运行 start.bat 即可启动系统。
echo.
pause
