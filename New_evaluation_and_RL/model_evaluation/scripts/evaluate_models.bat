@echo off
:: Batch Model Evaluation Script (Windows)

echo ==========================================
echo 批量模型评估脚本 (Windows)
echo Batch Model Evaluation Script (Windows) 
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
set "CONFIG_FILE=..\configs\evaluation_config.yaml"
set "MAX_SAMPLES="
set "OUTPUT_DIR="
set "BATCH_SIZE="
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
echo 开始批量模型评估...
echo ==========================================

python run_evaluation.py --config "%CONFIG_FILE%" %MAX_SAMPLES% %OUTPUT_DIR% %BATCH_SIZE% %YES_FLAG%

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
echo   -c, --config FILE      配置文件 (默认: ..\configs\evaluation_config.yaml^)
echo   -n, --max-samples N    最大评估样本数
echo   -o, --output-dir DIR   输出目录
echo   -b, --batch-size N     批处理大小
echo   -y, --yes              跳过确认提示
echo   -h, --help             显示帮助信息
echo.
echo 示例:
echo   # 使用默认配置评估
echo   %~nx0
echo.
echo   # 快速测试 10 个样本
echo   %~nx0 -n 10 -y
echo.
echo   # 使用自定义配置
echo   %~nx0 -c example_config.yaml -o test_results
echo.
exit /b 0