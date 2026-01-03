@echo off
setlocal enabledelayedexpansion

REM API Proxy Launch Script - Windows version
REM Supports rate limiting and progress display

REM Clear proxy settings to avoid interference
set "http_proxy="
set "https_proxy="
set "all_proxy="
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "ALL_PROXY="

REM Set NO_PROXY to exclude localhost
set "NO_PROXY=localhost,127.0.0.1,0.0.0.0,*.local"
set "no_proxy=localhost,127.0.0.1,0.0.0.0,*.local"

echo [OK] NO_PROXY set to '%NO_PROXY%'
echo      localhost requests will bypass all proxies

REM Set Python unbuffered output for real-time print
set PYTHONUNBUFFERED=1

REM Get script directory
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
REM Get project root (parent directory)
for %%I in ("%SCRIPT_DIR%") do set "PROJECT_ROOT=%%~dpI"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Check main config file
set "CONFIG_FILE=%PROJECT_ROOT%\config.yaml"
if not exist "%CONFIG_FILE%" (
    echo [ERROR] Config file not found: %CONFIG_FILE%
    pause
    exit /b 1
)

REM Check API pool config file
set "API_POOL_CONFIG=%PROJECT_ROOT%\metagpt_api_key_proxy\api_pool_config.yaml"
if not exist "%API_POOL_CONFIG%" (
    echo [WARNING] API pool config not found: %API_POOL_CONFIG%
    echo           Will use single API endpoint from main config
)

echo ==========================================
echo     Starting MetaGPT API Proxy Service
echo     (Multi-API Pool with Load Balancing)
echo ==========================================

REM Read port and debug mode from main config using Python to parse YAML
for /f "tokens=*" %%i in ('python -c "import yaml; c=yaml.safe_load(open(r'%CONFIG_FILE%')); print(c['services']['metagpt_api_proxy']['port'])" 2^>nul') do set PORT=%%i
if "%PORT%"=="" set PORT=5059

for /f "tokens=*" %%i in ('python -c "import yaml; c=yaml.safe_load(open(r'%CONFIG_FILE%')); print(str(c['services']['metagpt_api_proxy'].get('debug', False)).lower())" 2^>nul') do set DEBUG=%%i
if "%DEBUG%"=="" set DEBUG=false

REM Display API pool information if config exists
if exist "%API_POOL_CONFIG%" (
    echo.
    echo API Pool Configuration:
    python -c "import yaml; config=yaml.safe_load(open(r'%API_POOL_CONFIG%')); pool=config.get('api_pool', []); print(f'API Count: {len(pool)}') if pool else print('No APIs configured'); total_rate=sum(api.get('rate_per_second', 4.0) for api in pool) if pool else 0; print(f'Total Throughput: {total_rate:.1f} req/s') if pool else None; [print(f'  API #{i+1}: {api.get(\"rate_per_second\", 4.0)}req/s, concurrency {api.get(\"max_concurrency\", 20)}') for i, api in enumerate(pool)]" 2>nul
    if errorlevel 1 echo Failed to load API pool configuration
) else (
    echo API pool config file not found - using single endpoint
)

REM Check if port is already in use
netstat -ano | findstr :%PORT% >nul 2>&1
if %errorlevel%==0 (
    echo [WARNING] Port %PORT% is already in use, terminating existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 1 >nul
)

REM Create log directory
set "LOG_DIR=%PROJECT_ROOT%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Generate timestamp (format: YYYYMMDD_HHMMSS)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "timestamp=%datetime:~0,8%_%datetime:~8,6%"
set "LOG_FILE=%LOG_DIR%\api_proxy_%timestamp%.log"

echo.
echo Service Configuration:
echo   Config File: %CONFIG_FILE%
if exist "%API_POOL_CONFIG%" (
    echo   API Pool: %API_POOL_CONFIG%
) else (
    echo   API Pool: Using single endpoint from main config
)
echo   Log File: %LOG_FILE%
echo.
echo Service Settings:
echo   - Port: %PORT%
if "%DEBUG%"=="true" (
    echo   - Mode: Debug mode ^(verbose output^)
) else (
    echo   - Mode: Normal mode ^(progress bars and errors only^)
)
echo.
echo [INFO] Starting proxy server on http://127.0.0.1:%PORT%
echo        Press Ctrl+C to stop the service
echo ==========================================
echo.

REM Change to proxy service directory
cd /d "%PROJECT_ROOT%\metagpt_api_key_proxy"

REM Check if Python script exists - try the pool version first
if exist "api_key_proxy_pool.py" (
    REM Start proxy service with pool support (using -u option to disable buffering)
    echo [INFO] Starting command: python -u api_key_proxy_pool.py
    echo.
    python -u api_key_proxy_pool.py
) else if exist "api_key_proxy_enhanced.py" (
    REM Fallback to enhanced version
    echo [INFO] Pool version not found, using enhanced version
    echo [INFO] Starting command: python -u api_key_proxy_enhanced.py
    echo.
    python -u api_key_proxy_enhanced.py
) else (
    echo [ERROR] Cannot find api_key_proxy_pool.py or api_key_proxy_enhanced.py
    echo         Please ensure files are located in: %PROJECT_ROOT%\metagpt_api_key_proxy\
    pause
    exit /b 1
)

REM If Python exits, show exit message
echo.
echo [INFO] API proxy service has stopped
pause