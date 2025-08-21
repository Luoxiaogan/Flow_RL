@echo off
REM InternBootcamp Reward Server 启动脚本 (Windows)

echo ===========================================
echo 启动 InternBootcamp Reward Server
echo ===========================================

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 检查Python环境
echo 检查Python环境...
python --version

REM 检查config.yaml是否存在
set CONFIG_FILE=..\config.yaml
if exist "%CONFIG_FILE%" (
    echo √ 找到配置文件: %CONFIG_FILE%
) else (
    echo × 配置文件不存在: %CONFIG_FILE%
    echo   请确保config.yaml存在于上级目录
    pause
    exit /b 1
)

REM 设置环境变量
set PYTHONPATH=%SCRIPT_DIR%..;%SCRIPT_DIR%..\..;%PYTHONPATH%
echo PYTHONPATH设置为: %PYTHONPATH%

REM 启动服务器
echo.
echo 启动服务器...
echo 使用配置文件: %CONFIG_FILE%
echo.
echo 按Ctrl+C停止服务器
echo.

python internbootcamp_reward_server.py

pause