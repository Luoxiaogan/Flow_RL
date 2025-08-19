@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================
REM InternBootcamp Reward服务启动脚本 - Windows版本
REM ============================================
REM 用于InternBootcamp任务的workflow执行和评分计算
REM
REM 使用方法:
REM   start_internbootcamp_reward.bat          正常模式
REM   start_internbootcamp_reward.bat --debug  调试模式（开启详细日志）
REM
REM 调试模式说明:
REM   - Flask服务器以debug模式运行，显示详细错误信息
REM   - 生成debug日志文件到 debug_logs/ 目录
REM   - 记录每个workflow的执行详情、LLM调用、耗时等

REM 清除代理设置，避免干扰本地服务通信
set "http_proxy="
set "https_proxy="
set "all_proxy="
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "ALL_PROXY="

REM 设置NO_PROXY来排除localhost
set "NO_PROXY=localhost,127.0.0.1,0.0.0.0,*.local"
set "no_proxy=localhost,127.0.0.1,0.0.0.0,*.local"

echo [OK] 已清除代理设置并设置NO_PROXY
echo      NO_PROXY='%NO_PROXY%'
echo      localhost请求将绕过所有代理
echo.

echo ========================================
echo   InternBootcamp Reward服务启动器
echo ========================================

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
REM 获取项目根目录
for %%I in ("%SCRIPT_DIR%") do set "PROJECT_ROOT=%%~dpI"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM 读取主配置文件
set "CONFIG_FILE=%PROJECT_ROOT%\config.yaml"
if not exist "%CONFIG_FILE%" (
    echo [ERROR] 主配置文件不存在: %CONFIG_FILE%
    pause
    exit /b 1
)

REM 读取InternBootcamp配置文件
set "IB_CONFIG_FILE=%PROJECT_ROOT%\internbootcamp_config.yaml"
if not exist "%IB_CONFIG_FILE%" (
    echo [WARNING] InternBootcamp配置文件不存在: %IB_CONFIG_FILE%
    echo           使用默认配置
)

REM 解析命令行参数
set "DEBUG_MODE=false"
:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--debug" set "DEBUG_MODE=true"
shift
goto parse_args
:end_parse

REM 从YAML提取配置（优先使用internbootcamp_config.yaml）
echo [INFO] 读取配置文件...

REM 先尝试从internbootcamp_config.yaml读取
if exist "%IB_CONFIG_FILE%" (
    for /f "tokens=*" %%i in ('python -c "import yaml; config=yaml.safe_load(open(r'%IB_CONFIG_FILE%', encoding='utf-8')); print(config.get('reward_server',{}).get('port',8900))" 2^>nul') do set PORT=%%i
    for /f "tokens=*" %%i in ('python -c "import yaml; config=yaml.safe_load(open(r'%IB_CONFIG_FILE%', encoding='utf-8')); print(config.get('reward_server',{}).get('host','0.0.0.0'))" 2^>nul') do set HOST=%%i
    for /f "tokens=*" %%i in ('python -c "import yaml; config=yaml.safe_load(open(r'%IB_CONFIG_FILE%', encoding='utf-8')); print(config.get('reward_server',{}).get('enabled',True))" 2^>nul') do set ENABLED=%%i
    for /f "tokens=*" %%i in ('python -c "import yaml; config=yaml.safe_load(open(r'%IB_CONFIG_FILE%', encoding='utf-8')); print(config.get('reward_server',{}).get('timeout',300))" 2^>nul') do set TIMEOUT=%%i
) else (
    REM 默认值
    set PORT=8900
    set HOST=0.0.0.0
    set ENABLED=True
    set TIMEOUT=300
)

REM 提取MetaGPT相关配置并设置环境变量
echo [INFO] 配置MetaGPT环境变量...

REM 获取MetaGPT配置文件路径
for /f "tokens=*" %%i in ('python -c "import yaml, os; config=yaml.safe_load(open(r'%CONFIG_FILE%', encoding='utf-8')); path=config.get('paths',{}).get('metagpt_config',''); print(path.replace('/',os.sep) if path else '')" 2^>nul') do set METAGPT_CONFIG_PATH=%%i

if not "%METAGPT_CONFIG_PATH%"=="" (
    REM 使用Python来正确处理路径
    for /f "tokens=*" %%i in ('python -c "import os; path=r'%METAGPT_CONFIG_PATH%'; root=os.path.dirname(os.path.dirname(path)); print(root)" 2^>nul') do set METAGPT_ROOT=%%i
    
    echo        MetaGPT根目录: !METAGPT_ROOT!
    echo        MetaGPT配置文件: %METAGPT_CONFIG_PATH%
    
    REM 设置MetaGPT环境变量
    set "METAGPT_CONFIG=%METAGPT_CONFIG_PATH%"
    set "METAGPT_PROJECT_ROOT=!METAGPT_ROOT!"
    set "METAGPT_WORKSPACE=!METAGPT_ROOT!\workspace"
    set "METAGPT_LOG_DIR=!METAGPT_ROOT!\logs"
    set "METAGPT_DATA_PATH=!METAGPT_ROOT!\data"
)

REM 获取API代理配置
for /f "tokens=*" %%i in ('python -c "import yaml; config=yaml.safe_load(open(r'%CONFIG_FILE%', encoding='utf-8')); print(config['services']['metagpt_api_proxy']['port'])" 2^>nul') do set API_PROXY_PORT=%%i
if "%API_PROXY_PORT%"=="" set API_PROXY_PORT=5009

REM 获取LLM配置（从internbootcamp_config.yaml）
if exist "%IB_CONFIG_FILE%" (
    for /f "tokens=*" %%i in ('python -c "import yaml; config=yaml.safe_load(open(r'%IB_CONFIG_FILE%', encoding='utf-8')); print(config.get('llm_config',{}).get('api_key','sk-placeholder'))" 2^>nul') do set API_KEY=%%i
    for /f "tokens=*" %%i in ('python -c "import yaml; config=yaml.safe_load(open(r'%IB_CONFIG_FILE%', encoding='utf-8')); print(config.get('llm_config',{}).get('model','qwen-turbo'))" 2^>nul') do set MODEL=%%i
) else (
    set API_KEY=sk-placeholder
    set MODEL=qwen-turbo
)

REM 设置OpenAI兼容的环境变量（MetaGPT也会使用这些）
set "OPENAI_API_KEY=%API_KEY%"
set "OPENAI_API_BASE=http://localhost:%API_PROXY_PORT%"
set "OPENAI_API_MODEL=%MODEL%"

echo [OK] MetaGPT环境变量已设置
echo.

REM 检查API代理服务连通性
echo [INFO] 检查API代理服务连通性...

REM 使用Python检查连接
python -c "import urllib.request; urllib.request.urlopen('http://localhost:%API_PROXY_PORT%/', timeout=2)" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] API代理服务 ^(localhost:%API_PROXY_PORT%^) 连接成功
) else (
    echo [WARNING] 无法连接到API代理服务 ^(localhost:%API_PROXY_PORT%^)
    echo           请确保已启动: start_api_proxy.bat
    echo.
    set /p CONTINUE=是否继续启动? ^(y/n^) 
    if /i not "!CONTINUE!"=="y" (
        echo [INFO] 退出启动
        pause
        exit /b 1
    )
)
echo.

if "%ENABLED%"=="False" (
    echo [INFO] InternBootcamp Reward服务已禁用（配置中enabled=false）
    pause
    exit /b 0
)

echo 配置信息:
echo   主机: %HOST%
echo   端口: %PORT%
echo   超时: %TIMEOUT%秒
if "%DEBUG_MODE%"=="true" (
    echo   调试模式: 已启用
)
echo.

REM 检查端口是否被占用
netstat -ano | findstr :%PORT% >nul 2>&1
if %errorlevel%==0 (
    echo [WARNING] 端口 %PORT% 已被占用
    echo 占用进程:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
        set PID=%%a
        echo   PID: %%a
        REM 显示进程名称
        for /f "tokens=1" %%b in ('tasklist /FI "PID eq %%a" 2^>nul ^| findstr %%a') do echo   进程: %%b
    )
    echo.
    set /p KILL=是否终止占用进程并重新启动? ^(y/n^) 
    if /i "!KILL!"=="y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
            taskkill /F /PID %%a >nul 2>&1
        )
        echo [OK] 已终止占用进程
        timeout /t 1 >nul
    ) else (
        echo [INFO] 退出启动
        pause
        exit /b 1
    )
)

REM 创建日志目录
set "LOG_DIR=%PROJECT_ROOT%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 生成时间戳
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "timestamp=%datetime:~0,8%_%datetime:~8,6%"
set "LOG_FILE=%LOG_DIR%\internbootcamp_reward_%timestamp%.log"

REM 如果是debug模式，创建debug日志目录
if "%DEBUG_MODE%"=="true" (
    set "DEBUG_LOG_DIR=%PROJECT_ROOT%\debug\internbootcamp"
    if not exist "!DEBUG_LOG_DIR!" mkdir "!DEBUG_LOG_DIR!"
    echo [INFO] Debug日志将保存到: !DEBUG_LOG_DIR!
)

REM 显示服务信息
echo [OK] 正在启动InternBootcamp Reward服务...
echo.
echo 服务信息:
echo   URL: http://%HOST%:%PORT%
echo   日志: %LOG_FILE%
echo.
echo 可用的API端点:
echo   健康检查: http://%HOST%:%PORT%/health
echo   计算分数: http://%HOST%:%PORT%/compute_score
echo   批量计算: http://%HOST%:%PORT%/batch_compute
echo   任务列表: http://%HOST%:%PORT%/tasks
echo   配置信息: http://%HOST%:%PORT%/config
echo.
echo [TIP] 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 切换到internbootcamp_reward_server目录
cd /d "%PROJECT_ROOT%\internbootcamp_reward_server"

REM 检查Python脚本是否存在
if not exist "internbootcamp_reward_server.py" (
    echo [ERROR] 找不到 internbootcamp_reward_server.py
    echo         请确保文件位于: %PROJECT_ROOT%\internbootcamp_reward_server\
    pause
    exit /b 1
)

REM 构建启动命令
set "CMD=python internbootcamp_reward_server.py --port %PORT% --host %HOST%"

REM 如果指定了配置文件，添加到命令中
if exist "%IB_CONFIG_FILE%" (
    set "CMD=%CMD% --config %IB_CONFIG_FILE%"
)

REM 如果启用debug模式，添加--debug参数
if "%DEBUG_MODE%"=="true" (
    set "CMD=%CMD% --debug"
    echo [INFO] Flask服务器将以调试模式运行
    echo [INFO] Debug数据将保存到: %DEBUG_LOG_DIR%
    echo.
)

REM 启动Python服务
echo [INFO] 启动命令: %CMD%
echo.

REM 直接运行，输出显示在控制台
%CMD%

REM 如果服务退出，显示信息
echo.
echo [INFO] InternBootcamp Reward服务已停止
pause