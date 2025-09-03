@echo off
:: Unified Model Evaluation Script (Windows)
:: 统一的模型评估脚本 - 支持本地模型和API模型

echo ==========================================
echo 统一模型评估脚本 (Windows)
echo Unified Model Evaluation Script (Windows)
echo ==========================================

:: Set environment
for %%A in ("%~dp0..") do set "PARENT_DIR=%%~fA"
set "PYTHONPATH=%PYTHONPATH%;%PARENT_DIR%"

:: Activate conda environment
echo 激活 conda 环境...
call conda activate workflow
if %ERRORLEVEL% neq 0 (
    echo ⚠️  无法激活 conda 环境 'workflow'
    echo 请确保已安装 conda 并创建了 workflow 环境
    pause
    exit /b 1
)

:: Check Python packages
echo 检查依赖包...
python -c "import torch; import transformers; import aiohttp" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️  缺少必要的Python包
    echo 请安装: pip install torch transformers aiohttp peft bitsandbytes
)

:: Check if reward server is running
echo 检查 Reward Server...
curl -s http://localhost:8899/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Reward Server 未运行
    echo 请先启动 Reward Server:
    echo   ..\servers_and_proxy\start_scoreflow_reward.bat
    echo.
    set /p REPLY="是否继续? (可能会失败) [y/N]: "
    if /i not "%REPLY%"=="y" (
        exit /b 1
    )
) else (
    echo ✓ Reward Server 正常运行
)

:: Initialize variables
set "CONFIG_FILE=..\configs\models_config.yaml"
set "MAX_SAMPLES="
set "OUTPUT_DIR="
set "BATCH_SIZE="
set "FILTER="
set "LIMIT="
set "YES_FLAG="

:: Parse arguments
:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="-c" set "CONFIG_FILE=%~2" & shift & shift & goto :parse_args
if "%~1"=="--config" set "CONFIG_FILE=%~2" & shift & shift & goto :parse_args
if "%~1"=="-n" set "MAX_SAMPLES=--max-samples %~2" & shift & shift & goto :parse_args
if "%~1"=="--max-samples" set "MAX_SAMPLES=--max-samples %~2" & shift & shift & goto :parse_args
if "%~1"=="-o" set "OUTPUT_DIR=--output-dir %~2" & shift & shift & goto :parse_args
if "%~1"=="--output-dir" set "OUTPUT_DIR=--output-dir %~2" & shift & shift & goto :parse_args
if "%~1"=="-b" set "BATCH_SIZE=--batch-size %~2" & shift & shift & goto :parse_args
if "%~1"=="--batch-size" set "BATCH_SIZE=--batch-size %~2" & shift & shift & goto :parse_args
if "%~1"=="-f" set "FILTER=--filter %~2" & shift & shift & goto :parse_args
if "%~1"=="--filter" set "FILTER=--filter %~2" & shift & shift & goto :parse_args
if "%~1"=="-l" set "LIMIT=--limit %~2" & shift & shift & goto :parse_args
if "%~1"=="--limit" set "LIMIT=--limit %~2" & shift & shift & goto :parse_args
if "%~1"=="-y" set "YES_FLAG=--yes" & shift & goto :parse_args
if "%~1"=="--yes" set "YES_FLAG=--yes" & shift & goto :parse_args
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
echo 未知参数: %~1
goto :show_help

:end_parse

:: Check if config file exists
if not exist "%CONFIG_FILE%" (
    echo ❌ 配置文件不存在: %CONFIG_FILE%
    echo 请检查配置文件路径或创建配置文件
    exit /b 1
)

:: Show configuration
echo.
echo ==========================================
echo 评估配置
echo ==========================================
echo 配置文件: %CONFIG_FILE%
if defined MAX_SAMPLES echo 最大样本数: %MAX_SAMPLES:~14%
if defined OUTPUT_DIR echo 输出目录: %OUTPUT_DIR:~13%
if defined BATCH_SIZE echo 批次大小: %BATCH_SIZE:~13%
if defined FILTER echo 模型过滤: %FILTER:~9%
if defined LIMIT echo 模型限制: %LIMIT:~8%
echo.

:: Confirmation prompt (unless -y flag is set)
if not defined YES_FLAG (
    set /p CONFIRM="确认开始评估? [y/N]: "
    if /i not "%CONFIRM%"=="y" (
        echo 评估已取消
        exit /b 0
    )
)

:: Run evaluation
echo.
echo ==========================================
echo 开始统一模型评估...
echo ==========================================

python run_unified_evaluation.py --config "%CONFIG_FILE%" %MAX_SAMPLES% %OUTPUT_DIR% %BATCH_SIZE% %FILTER% %LIMIT% %YES_FLAG%

set "EXIT_CODE=%ERRORLEVEL%"

echo.
if %EXIT_CODE% equ 0 (
    echo ✓ 评估完成成功
    echo 结果已保存到输出目录
) else (
    echo ❌ 评估过程中出现错误 (退出码: %EXIT_CODE%^)
    echo 请查看日志了解详细信息
)

echo.
pause
exit /b %EXIT_CODE%

:: Help function
:show_help
echo.
echo 使用方法: %~nx0 [选项]
echo.
echo 选项:
echo   -c, --config FILE      模型配置文件 (默认: ..\configs\models_config.yaml^)
echo   -n, --max-samples N    最大评估样本数
echo   -o, --output-dir DIR   输出目录
echo   -b, --batch-size N     批处理大小
echo   -f, --filter TYPE      过滤模型类型 (api/local/等^)
echo   -l, --limit N          限制评估模型数量
echo   -y, --yes              跳过确认提示
echo   -h, --help             显示帮助信息
echo.
echo 示例:
echo   # 评估所有配置的模型
echo   %~nx0
echo.
echo   # 评估API模型，限制100个样本
echo   %~nx0 -f api -n 100 -y
echo.
echo   # 使用自定义配置和输出目录
echo   %~nx0 -c my_config.yaml -o results -b 2
echo.
exit /b 0