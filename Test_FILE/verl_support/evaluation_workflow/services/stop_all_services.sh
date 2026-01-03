#!/bin/bash

# ============================================
# 停止所有服务脚本
# ============================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}        停止所有服务${NC}"
echo -e "${BLUE}========================================${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
LOG_DIR="${PROJECT_ROOT}/logs"

# 停止API代理服务
echo -e "${YELLOW}停止API代理服务...${NC}"
if [ -f "${LOG_DIR}/api_proxy.pid" ]; then
    PID=$(cat "${LOG_DIR}/api_proxy.pid")
    if ps -p $PID > /dev/null 2>&1; then
        kill -9 $PID
        echo -e "${GREEN}✓ API代理服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}  API代理服务未运行${NC}"
    fi
    rm -f "${LOG_DIR}/api_proxy.pid"
else
    # 尝试通过端口查找进程
    PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$PROJECT_ROOT/config.yaml')); print(config['services']['api_proxy']['port'])" 2>/dev/null || echo "5009")
    if lsof -i :$PORT > /dev/null 2>&1; then
        PID=$(lsof -t -i:$PORT)
        kill -9 $PID 2>/dev/null
        echo -e "${GREEN}✓ API代理服务已停止 (端口: $PORT)${NC}"
    else
        echo -e "${YELLOW}  API代理服务未运行${NC}"
    fi
fi

# 停止ScoreFlow Reward服务
echo -e "${YELLOW}停止ScoreFlow Reward服务...${NC}"
if [ -f "${LOG_DIR}/reward_server.pid" ]; then
    PID=$(cat "${LOG_DIR}/reward_server.pid")
    if ps -p $PID > /dev/null 2>&1; then
        kill -9 $PID
        echo -e "${GREEN}✓ ScoreFlow Reward服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}  ScoreFlow Reward服务未运行${NC}"
    fi
    rm -f "${LOG_DIR}/reward_server.pid"
else
    # 尝试通过端口查找进程
    PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$PROJECT_ROOT/config.yaml')); print(config['services']['scoreflow_reward']['port'])" 2>/dev/null || echo "8899")
    if lsof -i :$PORT > /dev/null 2>&1; then
        PID=$(lsof -t -i:$PORT)
        kill -9 $PID 2>/dev/null
        echo -e "${GREEN}✓ ScoreFlow Reward服务已停止 (端口: $PORT)${NC}"
    else
        echo -e "${YELLOW}  ScoreFlow Reward服务未运行${NC}"
    fi
fi

# 停止SGLang服务（如果运行中）
echo -e "${YELLOW}检查SGLang服务...${NC}"
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$PROJECT_ROOT/config.yaml')); print(config['model']['local']['port'])" 2>/dev/null || echo "30000")
if lsof -i :$PORT > /dev/null 2>&1; then
    PID=$(lsof -t -i:$PORT)
    kill -9 $PID 2>/dev/null
    echo -e "${GREEN}✓ SGLang服务已停止 (端口: $PORT)${NC}"
else
    echo -e "${YELLOW}  SGLang服务未运行${NC}"
fi

echo ""
echo -e "${GREEN}所有服务已停止${NC}"
echo ""

# 显示日志文件位置
if [ -d "$LOG_DIR" ]; then
    echo -e "${BLUE}日志文件位置:${NC}"
    echo "  $LOG_DIR"
    echo ""
    echo -e "${YELLOW}最近的日志文件:${NC}"
    ls -lt "$LOG_DIR"/*.log 2>/dev/null | head -5 | awk '{print "  " $9}'
fi