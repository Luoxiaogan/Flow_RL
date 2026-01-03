@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================
REM InternBootcamp Reward服务启动脚本 (Windows)
REM ============================================
REM 用于InternBootcamp专属workflow执行和评分计算
REM
REM 使用方法:
REM   start_server.bat          - 正常模式
REM   start_server.bat --debug  - 调试模式（开启详细日志）
REM   start_server.bat --background  - 后台运行模式
REM
REM 调试模式说明:
REM   - Flask服务器以debug模式运行，显示详细错误信息
REM   - 生成debug日志文件到 debug_logs\ 目录
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

echo [√] 已清除代理设置并设置NO_PROXY
echo     NO_PROXY='%NO_PROXY%'
echo     localhost请求将绕过所有代理
echo.

echo ========================================
echo     InternBootcamp Reward服务启动器
echo ========================================
echo.

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
REM 去除末尾的反斜杠
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM 获取项目根目录（向上两级）
pushd "%SCRIPT_DIR%\..\.."
set "PROJECT_ROOT=%CD%"
popd

REM 获取服务根目录（向上一级）
pushd "%SCRIPT_DIR%\.."
set "SERVICE_ROOT=%CD%"
popd

REM 读取配置文件
set "CONFIG_FILE=%SERVICE_ROOT%\config.yaml"
if not exist "%CONFIG_FILE%" (
    echo [×] 错误: 配置文件不存在: %CONFIG_FILE%
    pause
    exit /b 1
)

REM 解析命令行参数
set "DEBUG_MODE=false"
set "BACKGROUND_MODE=false"
:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--debug" (
    set "DEBUG_MODE=true"
)
if "%~1"=="--background" (
    set "BACKGROUND_MODE=true"
)
shift
goto parse_args
:end_parse

REM ============================================
REM 自检步骤1: Python环境检查
REM ============================================
echo [1/7] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [×] Python未安装
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [√] Python已安装: %PYTHON_VERSION%

REM 检查必要的Python包
echo 检查必要的Python包...
set "MISSING_PACKAGES="
set "HAS_MISSING=0"

python -c "import yaml" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [×] 缺少包: yaml
    set "MISSING_PACKAGES=%MISSING_PACKAGES% pyyaml"
    set "HAS_MISSING=1"
) else (
    echo   [√] yaml 已安装
)

python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [×] 缺少包: flask
    set "MISSING_PACKAGES=%MISSING_PACKAGES% flask"
    set "HAS_MISSING=1"
) else (
    echo   [√] flask 已安装
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [×] 缺少包: requests
    set "MISSING_PACKAGES=%MISSING_PACKAGES% requests"
    set "HAS_MISSING=1"
) else (
    echo   [√] requests 已安装
)

if %HAS_MISSING% equ 1 (
    echo [×] 错误: 缺少必要的Python包
    echo 请运行: pip install%MISSING_PACKAGES%
    pause
    exit /b 1
)

REM ============================================
REM 自检步骤2: 配置文件验证
REM ============================================
echo.
echo [2/7] 验证配置文件...

REM 从YAML提取配置（使用Python解析）
for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['internbootcamp_reward']['port'])" 2^>nul') do set "PORT=%%i"
if "%PORT%"=="" set "PORT=8900"

for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['internbootcamp_reward']['host'])" 2^>nul') do set "HOST=%%i"
if "%HOST%"=="" set "HOST=0.0.0.0"

for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['internbootcamp_reward']['enabled'])" 2^>nul') do set "ENABLED=%%i"
if "%ENABLED%"=="" set "ENABLED=True"

for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['internbootcamp_reward']['timeout'])" 2^>nul') do set "TIMEOUT=%%i"
if "%TIMEOUT%"=="" set "TIMEOUT=300"

for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['internbootcamp_reward']['workspace'])" 2^>nul') do set "WORKSPACE=%%i"
if "%WORKSPACE%"=="" set "WORKSPACE=workspace\internbootcamp"

if "%ENABLED%" neq "True" (
    echo [!] InternBootcamp Reward服务已禁用（config.yaml中enabled=false）
    pause
    exit /b 0
)

echo [√] 配置文件解析成功
echo     主机: %HOST%
echo     端口: %PORT%
echo     超时: %TIMEOUT%秒
echo     工作目录: %WORKSPACE%

REM ============================================
REM 自检步骤3: 端口占用检查
REM ============================================
echo.
echo [3/7] 检查端口占用...

netstat -an | findstr ":%PORT% " >nul 2>&1
if %errorlevel% equ 0 (
    echo [!] 警告: 端口 %PORT% 已被占用
    echo.
    echo 占用进程信息:
    netstat -ano | findstr ":%PORT% "
    echo.
    set /p "REPLY=是否继续启动? (y/n): "
    if /i not "!REPLY!"=="y" (
        echo [×] 退出启动
        pause
        exit /b 1
    )
) else (
    echo [√] 端口 %PORT% 可用
)

REM ============================================
REM 自检步骤4: API代理服务检查
REM ============================================
echo.
echo [4/7] 检查API代理服务连通性...

REM 获取API代理配置
for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['metagpt_api_proxy']['port'])" 2^>nul') do set "API_PROXY_PORT=%%i"
if "%API_PROXY_PORT%"=="" set "API_PROXY_PORT=5009"

for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['evaluation_api_proxy']['port'])" 2^>nul') do set "EVAL_API_PROXY_PORT=%%i"
if "%EVAL_API_PROXY_PORT%"=="" set "EVAL_API_PROXY_PORT=5010"

REM 使用Python检查MetaGPT API代理（更可靠）
echo 检查MetaGPT API代理服务 - 端口 %API_PROXY_PORT%...
REM 创建临时Python脚本来检查连接
echo import socket > temp_check.py
echo s = socket.socket^(^) >> temp_check.py
echo s.settimeout^(2^) >> temp_check.py
echo try: >> temp_check.py
echo     result = s.connect_ex^(^('localhost', %API_PROXY_PORT%^)^) >> temp_check.py
echo     s.close^(^) >> temp_check.py
echo     exit^(0 if result == 0 else 1^) >> temp_check.py
echo except: >> temp_check.py
echo     exit^(1^) >> temp_check.py

python temp_check.py 2>nul
if %errorlevel% equ 0 (
    echo [√] MetaGPT API代理服务连接成功
) else (
    echo [!] 警告: 无法连接到MetaGPT API代理服务 - localhost:%API_PROXY_PORT%
    echo     请确保已启动: start_api_proxy.bat
)
del temp_check.py >nul 2>&1

REM 使用Python检查Evaluation API代理（更可靠）
echo 检查Evaluation API代理服务 - 端口 %EVAL_API_PROXY_PORT%...
REM 创建临时Python脚本来检查连接
echo import socket > temp_check2.py
echo s = socket.socket^(^) >> temp_check2.py
echo s.settimeout^(2^) >> temp_check2.py
echo try: >> temp_check2.py
echo     result = s.connect_ex^(^('localhost', %EVAL_API_PROXY_PORT%^)^) >> temp_check2.py
echo     s.close^(^) >> temp_check2.py
echo     exit^(0 if result == 0 else 1^) >> temp_check2.py
echo except: >> temp_check2.py
echo     exit^(1^) >> temp_check2.py

python temp_check2.py 2>nul
if %errorlevel% equ 0 (
    echo [√] Evaluation API代理服务连接成功
) else (
    echo [!] 警告: 无法连接到Evaluation API代理服务 - localhost:%EVAL_API_PROXY_PORT%
    echo     如需使用评估功能，请启动评估API代理
)
del temp_check2.py >nul 2>&1

REM ============================================
REM 自检步骤5: 目录结构检查
REM ============================================
echo.
echo [5/7] 检查目录结构...

REM 创建必要的目录
set "WORKSPACE_DIR=%PROJECT_ROOT%\%WORKSPACE%"
set "LOG_DIR=%SERVICE_ROOT%\logs"
set "DEBUG_LOG_DIR=%SERVICE_ROOT%\debug_logs"

if not exist "%WORKSPACE_DIR%" mkdir "%WORKSPACE_DIR%"
echo [√] 工作目录已创建: %WORKSPACE_DIR%

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
echo [√] 日志目录已创建: %LOG_DIR%

if "%DEBUG_MODE%"=="true" (
    if not exist "%DEBUG_LOG_DIR%" mkdir "%DEBUG_LOG_DIR%"
    echo [√] Debug日志目录已创建: %DEBUG_LOG_DIR%
)

REM ============================================
REM 自检步骤6: 依赖文件检查
REM ============================================
echo.
echo [6/7] 检查依赖文件...

REM 检查必要的Python文件
set "ALL_FILES_EXIST=1"
set "REQUIRED_FILES=internbootcamp_reward_server.py internbootcamp_reward_utils.py internbootcamp_utils.py"

for %%f in (%REQUIRED_FILES%) do (
    if exist "%SCRIPT_DIR%\%%f" (
        echo [√] %%f 存在
    ) else (
        echo [×] 缺少文件: %%f
        set "ALL_FILES_EXIST=0"
    )
)

if %ALL_FILES_EXIST% equ 0 (
    echo [×] 存在缺失的必要文件
    pause
    exit /b 1
)

REM 检查ScoreFlow路径
if exist "%PROJECT_ROOT%\ScoreFlow" (
    echo [√] ScoreFlow目录存在
) else (
    echo [!] 警告: ScoreFlow目录不存在: %PROJECT_ROOT%\ScoreFlow
)

REM ============================================
REM 自检步骤7: 环境变量设置
REM ============================================
echo.
echo [7/7] 设置环境变量...

REM 设置PYTHONPATH
set "PYTHONPATH=%SCRIPT_DIR%;%SERVICE_ROOT%;%PROJECT_ROOT%;%PYTHONPATH%"
echo [√] PYTHONPATH已设置

REM 设置API相关环境变量
for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('%CONFIG_FILE%'.replace('\\','/'))); print(config['services']['metagpt_api_proxy']['target_api_key'])" 2^>nul') do set "API_KEY=%%i"
if not "%API_KEY%"=="" (
    set "OPENAI_API_KEY=%API_KEY%"
    set "OPENAI_API_BASE=http://localhost:%API_PROXY_PORT%"
    echo [√] API环境变量已设置
)

REM ============================================
REM 启动服务
REM ============================================
echo.
echo ========================================
echo [√] 所有检查通过，正在启动服务...
echo ========================================
echo.

REM 生成日志文件名
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set "datetime=%%i"
set "datetime=%datetime:~0,8%_%datetime:~8,6%"
set "LOG_FILE=%LOG_DIR%\internbootcamp_reward_%datetime%.log"

REM 显示服务信息
echo 服务信息:
echo   URL: http://%HOST%:%PORT%
echo   日志: %LOG_FILE%
echo   工作目录: %WORKSPACE_DIR%

if "%DEBUG_MODE%"=="true" (
    echo   [!] 调试模式: 已启用
    echo   [!] Debug日志: %DEBUG_LOG_DIR%
)

if "%BACKGROUND_MODE%"=="true" (
    echo   [!] 后台模式: 已启用
)

echo.
echo 提示: 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 切换到服务目录
cd /d "%SCRIPT_DIR%"

REM 构建启动命令
set "CMD=python internbootcamp_reward_server.py --port %PORT% --host %HOST%"

REM 如果启用debug模式，添加--debug参数
if "%DEBUG_MODE%"=="true" (
    set "CMD=%CMD% --debug"
)

REM 启动服务
if "%BACKGROUND_MODE%"=="true" (
    echo 在后台启动服务器...
    start /b cmd /c "%CMD% > %LOG_FILE% 2>&1"
    echo [√] 服务器已在后台启动
    echo.
    echo 日志文件: %LOG_FILE%
    echo.
    echo 使用以下命令查看日志:
    echo   type "%LOG_FILE%"
    echo.
    echo 或实时查看（需要PowerShell）:
    echo   powershell Get-Content "%LOG_FILE%" -Wait
    timeout /t 3 /nobreak >nul
) else (
    REM 前台运行
    %CMD%
)

pause