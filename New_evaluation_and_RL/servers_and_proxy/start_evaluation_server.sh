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
    echo "❌ SGLang本地模式暂未实现"
    echo ""
    echo "请在config.yaml中修改配置："
    echo "  model:"
    echo "    mode: \"evaluation_api\"  # 使用评估API代理模式"
    echo ""
    echo "或者使用："
    echo "  model:"
    echo "    mode: \"api\"  # 使用MetaGPT API代理模式"
    echo ""
    echo "然后重新运行评估脚本。"
    exit 1

elif [ "$MODE" = "api" ]; then
    echo "ℹ️ 使用MetaGPT API代理模式"
    echo ""
    echo "✅ 无需启动额外的评估模型服务"
    echo "   评估将直接使用MetaGPT API代理 (端口5009)"
    echo ""
    echo "请确保MetaGPT API代理正在运行："
    echo "  bash start_api_proxy.sh"
    echo ""
    echo "然后可以直接运行评估："
    echo "  cd ../evaluation"
    echo "  bash start_evaluation.sh"
    exit 0

else
    echo "❌ 未知的模型模式: $MODE"
    echo ""
    echo "支持的模式："
    echo "  - evaluation_api: 使用评估API代理 (推荐)"
    echo "  - api: 使用MetaGPT API代理"
    echo "  - local: SGLang本地服务器 (暂未实现)"
    echo ""
    echo "请在config.yaml中设置正确的model.mode值"
    exit 1
fi