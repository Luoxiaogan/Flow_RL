@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM API代理启动脚本 - Windows版本
REM 支持速率限制和进度显示

REM 清除代理设置，避免干扰
set "http_proxy="
set "https_proxy="
set "all_proxy="
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "ALL_PROXY="

REM 设置NO_PROXY来排除localhost
set "NO_PROXY=localhost,127.0.0.1,0.0.0.0,*.local"
set "no_proxy=localhost,127.0.0.1,0.0.0.0,*.local"

echo [OK] 已设置NO_PROXY='%NO_PROXY%'
echo      localhost请求将绕过所有代理

REM 设置Python无缓冲输出，确保实时看到print内容
set PYTHONUNBUFFERED=1

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
REM 移除尾部的反斜杠
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
REM 获取项目根目录（上一级目录）
for %%I in ("%SCRIPT_DIR%") do set "PROJECT_ROOT=%%~dpI"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM 检查配置文件
set "CONFIG_FILE=%PROJECT_ROOT%\config.yaml"
if not exist "%CONFIG_FILE%" (
    echo [ERROR] 配置文件不存在: %CONFIG_FILE%
    pause
    exit /b 1
)

echo ==========================================
echo     启动 MetaGPT API 代理服务
echo ==========================================

REM 从配置文件读取配置（使用Python解析YAML）
for /f "tokens=*" %%i in ('python -c "import yaml; c=yaml.safe_load(open(r'%CONFIG_FILE%', encoding='utf-8')); print(c['services']['metagpt_api_proxy']['port'])" 2^>nul') do set PORT=%%i
if "%PORT%"=="" set PORT=5009

for /f "tokens=*" %%i in ('python -c "import yaml; c=yaml.safe_load(open(r'%CONFIG_FILE%', encoding='utf-8')); print(str(c['services']['metagpt_api_proxy'].get('debug', False)).lower())" 2^>nul') do set DEBUG=%%i
if "%DEBUG%"=="" set DEBUG=false

for /f "tokens=*" %%i in ('python -c "import yaml; c=yaml.safe_load(open(r'%CONFIG_FILE%', encoding='utf-8')); print(c['services']['metagpt_api_proxy'].get('rate_per_second', 1.0))" 2^>nul') do set RATE=%%i
if "%RATE%"=="" set RATE=1.0

REM 检查端口是否被占用
netstat -ano | findstr :%PORT% >nul 2>&1
if %errorlevel%==0 (
    echo [WARNING] 端口 %PORT% 已被占用，正在终止现有进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 1 >nul
)

REM 创建日志目录
set "LOG_DIR=%PROJECT_ROOT%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 生成时间戳（格式：YYYYMMDD_HHMMSS）
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "timestamp=%datetime:~0,8%_%datetime:~8,6%"
set "LOG_FILE=%LOG_DIR%\api_proxy_%timestamp%.log"

echo.
echo 配置文件: %CONFIG_FILE%
echo 日志文件: %LOG_FILE%
echo.
echo 服务配置:
echo   - 端口: %PORT%
echo   - 速率限制: %RATE% req/s
if "%DEBUG%"=="true" (
    echo   - 模式: 调试模式 ^(显示详细信息^)
) else (
    echo   - 模式: 正常模式 ^(仅显示进度条和错误^)
)
echo.
echo [INFO] 正在启动代理服务器...
echo        按 Ctrl+C 停止服务
echo ==========================================
echo.

REM 切换到代理服务目录
cd /d "%PROJECT_ROOT%\metagpt_api_key_proxy"

REM 检查Python脚本是否存在
if not exist "api_key_proxy_enhanced.py" (
    echo [ERROR] 找不到 api_key_proxy_enhanced.py
    echo         请确保文件位于: %PROJECT_ROOT%\metagpt_api_key_proxy\
    pause
    exit /b 1
)

REM 启动代理服务（使用-u选项禁用缓冲，确保实时输出）
echo [INFO] 启动命令: python -u api_key_proxy_enhanced.py
echo.

REM 直接运行Python，输出会显示在控制台
python -u api_key_proxy_enhanced.py

REM 如果Python退出，显示退出信息
echo.
echo [INFO] API代理服务已停止
pause