#!/bin/bash

# API代理启动脚本 - 简化版（监控在Python内部）
# 支持Round-Robin分发请求到多个API endpoints
# Python内部监控chat/completions请求，超时自动退出

# 清除代理设置，避免干扰
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY来排除localhost
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo "✓ 已设置NO_PROXY='$NO_PROXY'"

# 设置Python无缓冲输出
export PYTHONUNBUFFERED=1

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查主配置文件
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 主配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 从配置读取端口
PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo "5059")

# 从scoreflow_reward配置读取重启超时时间
RESTART_TIMEOUT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['scoreflow_reward'].get('restart_per_step', 180))" 2>/dev/null || echo "180")

echo "=========================================="
echo "启动 MetaGPT API 代理服务 (内部监控版本)"
echo "=========================================="
echo "端口: $PORT"
echo "监控超时: ${RESTART_TIMEOUT}秒"
echo "配置文件: $CONFIG_FILE"
echo "=========================================="

# 检查端口是否被占用（无交互，直接清理）
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "端口 $PORT 已被占用，正在终止现有进程..."
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null
    sleep 1
fi

# 创建日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"

# 清理函数
cleanup() {
    echo ""
    echo "[$(date '+%F %T')] 停止服务..."
    pkill -f "api_key_proxy_pool.py" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# 主服务循环
cd "${PROJECT_ROOT}/metagpt_api_key_proxy"

while true; do
    echo ""
    echo "========== [服务启动] =========="
    echo "时间: $(date '+%F %T')"

    # 创建新的日志文件
    LOG_FILE="${LOG_DIR}/api_proxy_pool_$(date +%Y%m%d_%H%M%S).log"
    echo "日志: $LOG_FILE"
    echo "================================"

    # 启动Python服务（使用监控版本，前台运行）
    python3 -u api_key_proxy_pool_monitor.py 2>&1 | tee "$LOG_FILE"
    EXIT_CODE=$?

    # 检查退出原因
    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "========== [自动重启中] =========="
        echo "服务正常退出（超时触发），3秒后重启..."
        sleep 3
        continue
    elif [ $EXIT_CODE -eq 130 ] || [ $EXIT_CODE -eq 143 ]; then
        # 130 = Ctrl+C (SIGINT), 143 = SIGTERM
        echo ""
        echo "========== [用户中断] =========="
        echo "服务被用户中断"
        break
    else
        echo ""
        echo "========== [异常退出] =========="
        echo "退出代码: $EXIT_CODE"
        echo "10秒后尝试重启..."
        sleep 10
        continue
    fi
done

echo "服务已完全停止"