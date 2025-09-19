#!/bin/bash

# ScoreFlow Reward服务启动脚本 - 简化版
# 依赖API代理的内部监控机制协调重启

# 清除代理设置
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo "✓ 已设置NO_PROXY='$NO_PROXY'"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    ScoreFlow Reward服务启动器（简化版）${NC}"
echo -e "${BLUE}========================================${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 读取配置文件
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 解析命令行参数
DEBUG_MODE=false
for arg in "$@"; do
    case $arg in
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        *)
            ;;
    esac
done

# 从YAML提取配置
echo -e "${YELLOW}读取配置文件...${NC}"
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['port'])" 2>/dev/null || echo "7788")
HOST=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['host'])" 2>/dev/null || echo "0.0.0.0")
ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['enabled'])" 2>/dev/null || echo "True")

# 提取MetaGPT配置
METAGPT_CONFIG_PATH=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['paths']['metagpt_config'])" 2>/dev/null || echo "")
if [ -n "$METAGPT_CONFIG_PATH" ]; then
    METAGPT_ROOT=$(dirname $(dirname "$METAGPT_CONFIG_PATH"))
    export METAGPT_CONFIG="$METAGPT_CONFIG_PATH"
    export METAGPT_PROJECT_ROOT="$METAGPT_ROOT"
    export METAGPT_WORKSPACE="$METAGPT_ROOT/workspace"
    export METAGPT_LOG_DIR="$METAGPT_ROOT/logs"
    export METAGPT_DATA_PATH="$METAGPT_ROOT/data"
    echo "✓ MetaGPT环境变量已设置"
fi

# 获取API代理配置
API_PROXY_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo "5059")
API_KEY=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['llm_settings']['key'])" 2>/dev/null || echo "sk-placeholder")
MODEL=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['llm_settings']['model'])" 2>/dev/null || echo "qwen-turbo")

# 设置OpenAI兼容的环境变量
export OPENAI_API_KEY="$API_KEY"
export OPENAI_API_BASE="http://localhost:$API_PROXY_PORT"
export OPENAI_API_MODEL="$MODEL"

if [ "$ENABLED" != "True" ]; then
    echo -e "${YELLOW}ScoreFlow Reward服务已禁用（enabled=false）${NC}"
    exit 0
fi

echo -e "${GREEN}配置信息:${NC}"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  API代理: localhost:$API_PROXY_PORT"
if [ "$DEBUG_MODE" = true ]; then
    echo -e "  ${YELLOW}调试模式: 已启用${NC}"
fi
echo ""

# 检查端口是否被占用（无交互，直接清理）
if lsof -i :$PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}端口 $PORT 已被占用，正在终止现有进程...${NC}"
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null
    sleep 1
fi

# 创建日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"

# 如果是debug模式，创建debug日志目录
if [ "$DEBUG_MODE" = true ]; then
    DEBUG_LOG_DIR="${PROJECT_ROOT}/debug_logs"
    mkdir -p "$DEBUG_LOG_DIR"
fi

# 监控重启信号的函数
monitor_restart_signal() {
    local python_pid=$1
    local restart_flag="/tmp/scoreflow_restart_requested"

    echo -e "${YELLOW}🔍 启动重启信号监控 (PID: $python_pid)${NC}"

    while kill -0 $python_pid 2>/dev/null; do
        if [ -f "$restart_flag" ]; then
            echo -e "${RED}🔴 检测到重启信号，开始外部终止进程...${NC}"

            # 先尝试SIGTERM (优雅退出)
            echo -e "${YELLOW}📤 发送SIGTERM信号...${NC}"
            kill -TERM $python_pid 2>/dev/null
            sleep 2

            # 检查是否还在运行
            if kill -0 $python_pid 2>/dev/null; then
                echo -e "${RED}📤 SIGTERM无效，发送SIGKILL信号...${NC}"
                kill -KILL $python_pid 2>/dev/null
            fi

            # 清理标志文件
            rm -f "$restart_flag"
            echo -e "${GREEN}✅ 进程已终止，标志文件已清理${NC}"
            break
        fi
        sleep 0.5  # 每0.5秒检查一次
    done

    echo -e "${BLUE}🏁 重启信号监控结束${NC}"
}

# 清理函数
cleanup() {
    echo ""
    echo -e "${BLUE}[$(date '+%F %T')] 停止服务...${NC}"

    # 清理重启标志文件
    rm -f "/tmp/scoreflow_restart_requested"

    # 终止所有相关进程
    pkill -f "scoreflow_reward_server.py" 2>/dev/null || true
    pkill -f "monitor_restart_signal" 2>/dev/null || true

    exit 0
}

trap cleanup SIGINT SIGTERM

# 主服务循环
cd "${PROJECT_ROOT}/reward_server"

while true; do
    echo ""
    echo -e "${GREEN}========== [服务启动] ==========${NC}"
    echo "时间: $(date '+%F %T')"

    # 等待API代理就绪
    echo -e "${YELLOW}检查API代理服务...${NC}"
    api_ready=false
    for i in {1..6}; do
        if curl -s -f http://localhost:$API_PROXY_PORT/health >/dev/null 2>&1; then
            echo -e "${GREEN}✓ API代理服务已就绪${NC}"
            api_ready=true
            break
        fi
        if [ $i -lt 6 ]; then
            echo "等待API代理启动... ($i/6)"
            sleep 5
        fi
    done

    if [ "$api_ready" = false ]; then
        echo -e "${YELLOW}⚠️ API代理未就绪，但继续启动${NC}"
    fi

    # 创建新的日志文件
    LOG_FILE="${LOG_DIR}/scoreflow_reward_$(date +%Y%m%d_%H%M%S).log"
    echo "日志: $LOG_FILE"
    echo -e "${GREEN}=================================${NC}"

    # 构建启动命令
    CMD="python3 scoreflow_reward_server.py --port $PORT --host $HOST"
    if [ "$DEBUG_MODE" = true ]; then
        CMD="$CMD --debug"
    fi

    # 启动主服务（后台运行，支持外部监控）
    echo -e "${GREEN}🚀 启动Python进程...${NC}"
    $CMD 2>&1 | tee "$LOG_FILE" &
    PYTHON_PID=$!

    echo -e "${BLUE}📋 Python进程PID: $PYTHON_PID${NC}"

    # 启动监控进程 (后台运行)
    monitor_restart_signal $PYTHON_PID &
    MONITOR_PID=$!

    # 等待Python进程结束
    wait $PYTHON_PID
    EXIT_CODE=$?

    # 清理监控进程
    kill $MONITOR_PID 2>/dev/null || true
    wait $MONITOR_PID 2>/dev/null || true

    echo -e "${BLUE}💭 Python进程已退出，退出代码: $EXIT_CODE${NC}"

    # 检查退出原因
    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo -e "${GREEN}========== [正常退出] ==========${NC}"
        echo "服务正常退出，可能是收到重启通知"
        echo "5秒后重新启动..."
        sleep 5
        continue
    elif [ $EXIT_CODE -eq 130 ] || [ $EXIT_CODE -eq 143 ]; then
        # 130 = Ctrl+C (SIGINT), 143 = SIGTERM
        echo ""
        echo -e "${BLUE}========== [用户中断] ==========${NC}"
        break
    else
        echo ""
        echo -e "${YELLOW}========== [异常退出] ==========${NC}"
        echo "退出代码: $EXIT_CODE"
        echo "10秒后尝试重启..."
        sleep 10
        continue
    fi
done

echo "服务已完全停止"