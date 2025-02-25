@echo off
echo 正在启动文件管理系统服务器...

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装，请先安装Python！
    pause
    exit /b 1
)

:: 检查server.py是否存在
if not exist "%~dp0server.py" (
    echo 错误：未找到server.py文件！
    pause
    exit /b 1
)

:: 启动服务器
echo 正在启动服务器...
python "%~dp0server.py"

:: 如果服务器异常退出
if %errorlevel% neq 0 (
    echo 服务器启动失败！
    pause
)