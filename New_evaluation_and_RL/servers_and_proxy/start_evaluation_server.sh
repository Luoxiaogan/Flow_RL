#!/bin/bash

# API代理启动脚本 - 评估模型服务版本

# 清除代理设置，避免干扰
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY来排除localhost（即使Clash开启系统代理也有效）
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo "✓ 已设置NO_PROXY='$NO_PROXY'"
echo "  localhost请求将绕过所有代理"

# 设置Python无缓冲输出，确保实时看到print内容
export PYTHONUNBUFFERED=1

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查配置文件
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

echo "=========================================="
echo "启动评估模型服务"
echo "=========================================="

# 服务健康检查函数
check_service_health() {
    local service_name=$1
    local port=$2
    local health_endpoint=${3:-"/health"}
    
    echo "🔍 检查 $service_name (端口 $port)..."
    
    # 检查端口是否监听
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo "❌ $service_name 未运行 (端口 $port 无监听)"
        return 1
    fi
    
    # 检查健康状态
    local health_url="http://localhost:$port$health_endpoint"
    if curl -s --max-time 5 "$health_url" > /dev/null 2>&1; then
        echo "✅ $service_name 运行正常"
        return 0
    else
        echo "⚠️ $service_name 端口已占用但健康检查失败"
        echo "   健康检查: $health_url"
        # 对于某些服务，健康检查失败不一定意味着无法使用
        return 0
    fi
}

# 检查必需的依赖服务
echo "🔍 检查评估系统依赖服务"
echo ""

services_ok=true

# 检查MetaGPT API代理
if ! check_service_health "MetaGPT API代理" 5009 "/"; then
    echo "💡 请先启动MetaGPT API代理:"
    echo "   bash start_api_proxy.sh"
    services_ok=false
fi

# 检查ScoreFlow奖励服务器
if ! check_service_health "ScoreFlow奖励服务器" 8899 "/health"; then
    echo "💡 请先启动ScoreFlow奖励服务器:"
    echo "   bash start_scoreflow_reward.sh"
    services_ok=false
fi

echo ""

if [ "$services_ok" = false ]; then
    echo "❌ 依赖服务检查失败"
    echo "请先启动所有必需的服务，然后重新运行此脚本"
    exit 1
fi

echo "✅ 所有依赖服务检查通过"
echo ""

# 从配置文件读取模型模式
MODE=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['mode'])" 2>/dev/null || echo "evaluation_api")

echo "模型模式: $MODE"

# 根据模式决定启动方式
if [ "$MODE" = "evaluation_api" ]; then
    echo "📡 启动评估API代理服务..."
    
    # 从配置文件读取evaluation_api_proxy配置
    PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['evaluation_api_proxy']['port'])" 2>/dev/null || echo "5010")
    DEBUG=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(str(c['services']['evaluation_api_proxy'].get('debug', False)).lower())" 2>/dev/null || echo "false")
    RATE=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['evaluation_api_proxy'].get('rate_per_second', 3.0))" 2>/dev/null || echo "3.0")
    
    # 检查端口是否被占用
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo "端口 $PORT 已被占用，正在终止现有进程..."
        kill -9 $(lsof -t -i:$PORT) 2>/dev/null
        sleep 1
    fi
    
    # 创建日志目录
    LOG_DIR="${PROJECT_ROOT}/logs"
    mkdir -p "$LOG_DIR"
    LOG_FILE="${LOG_DIR}/evaluation_api_proxy_$(date +%Y%m%d_%H%M%S).log"
    
    echo "配置文件: $CONFIG_FILE"
    echo "日志文件: $LOG_FILE"
    echo ""
    echo "服务配置:"
    echo "  - 端口: $PORT"
    echo "  - 速率限制: $RATE req/s"
    if [ "$DEBUG" = "true" ]; then
        echo "  - 模式: 调试模式 (显示详细信息)"
    else
        echo "  - 模式: 正常模式 (仅显示进度条和错误)"
    fi
    echo ""
    echo "正在启动评估API代理..."
    echo "按 Ctrl+C 停止服务"
    echo "=========================================="
    echo ""
    
    # 启动评估专用API代理服务（使用-u选项禁用缓冲，确保实时输出）
    cd "${PROJECT_ROOT}/metagpt_api_key_proxy"
    python3 -u api_key_proxy_enhanced_for_evaluation.py 2>&1 | tee "$LOG_FILE"

elif [ "$MODE" = "local" ]; then
    echo "🖥️ 启动SGLang本地服务器..."
    echo ""
    
    # 从配置文件读取SGLang配置
    MODEL_PATH=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['model_path'])" 2>/dev/null || echo "/nas/models/Qwen2.5-7B-Instruct")
    LOCAL_HOST=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['host'])" 2>/dev/null || echo "0.0.0.0")
    LOCAL_PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['port'])" 2>/dev/null || echo "30009")
    MEM_FRACTION=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['mem_fraction_static'])" 2>/dev/null || echo "0.85")
    BASE_GPU_ID=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['base_gpu_id'])" 2>/dev/null || echo "0")
    DEBUG_MODE=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(str(c['model']['local']['debug_mode']).lower())" 2>/dev/null || echo "false")
    
    # 检查端口是否被占用
    if lsof -i :$LOCAL_PORT > /dev/null 2>&1; then
        echo "端口 $LOCAL_PORT 已被占用，正在终止现有进程..."
        kill -9 $(lsof -t -i:$LOCAL_PORT) 2>/dev/null
        sleep 2
    fi
    
    # 创建日志目录
    LOG_DIR="${PROJECT_ROOT}/logs"
    mkdir -p "$LOG_DIR"
    LOG_FILE="${LOG_DIR}/sglang_server_$(date +%Y%m%d_%H%M%S).log"
    
    echo "SGLang服务器配置:"
    echo "  - 模型路径: $MODEL_PATH"
    echo "  - 主机地址: $LOCAL_HOST"
    echo "  - 端口: $LOCAL_PORT"
    echo "  - 内存分配: $MEM_FRACTION"
    echo "  - 基础GPU ID: $BASE_GPU_ID"
    echo "  - 调试模式: $DEBUG_MODE"
    echo "  - 日志文件: $LOG_FILE"
    echo ""
    echo "正在启动SGLang服务器..."
    echo "按 Ctrl+C 停止服务"
    echo "=========================================="
    echo ""
    
    # 构建SGLang启动命令（简化版本，只保留必要参数）
    SGLANG_CMD="python -m sglang.launch_server"
    SGLANG_CMD="$SGLANG_CMD --model-path \"$MODEL_PATH\""
    SGLANG_CMD="$SGLANG_CMD --host \"$LOCAL_HOST\""
    SGLANG_CMD="$SGLANG_CMD --port $LOCAL_PORT"
    SGLANG_CMD="$SGLANG_CMD --base-gpu-id $BASE_GPU_ID"
    SGLANG_CMD="$SGLANG_CMD --mem-fraction-static $MEM_FRACTION"
    SGLANG_CMD="$SGLANG_CMD --enable-metrics"
    
    # 如果不是调试模式，减少输出
    if [ "$DEBUG_MODE" != "true" ]; then
        SGLANG_CMD="$SGLANG_CMD --log-level info"
    else
        SGLANG_CMD="$SGLANG_CMD --log-level debug"
    fi
    
    echo "执行命令: $SGLANG_CMD"
    echo ""
    
    # 启动SGLang服务器（前台运行，同时输出到终端和日志文件）
    eval "$SGLANG_CMD" 2>&1 | tee "$LOG_FILE"

else
    echo "❌ 未知的模型模式: $MODE"
    echo ""
    echo "支持的模式："
    echo "  - evaluation_api: 使用评估API代理 (推荐)"
    echo "  - local: SGLang本地服务器"
    echo ""
    echo "请在config.yaml中设置正确的model.mode值"
    exit 1
fi