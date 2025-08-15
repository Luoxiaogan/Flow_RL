#!/bin/bash

# ============================================
# API代理服务启动脚本
# ============================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}        API代理服务启动器${NC}"
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

# 从YAML提取配置（使用Python解析）
echo -e "${YELLOW}读取配置文件...${NC}"
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['api_proxy']['port'])" 2>/dev/null || echo "5009")
HOST=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['api_proxy']['host'])" 2>/dev/null || echo "localhost")
ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['api_proxy']['enabled'])" 2>/dev/null || echo "True")

if [ "$ENABLED" != "True" ]; then
    echo -e "${YELLOW}API代理服务已禁用（config.yaml中enabled=false）${NC}"
    exit 0
fi

echo -e "${GREEN}配置信息:${NC}"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo ""

# 检查端口是否被占用
if lsof -i :$PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}警告: 端口 $PORT 已被占用${NC}"
    echo "占用进程:"
    lsof -i :$PORT
    echo ""
    read -p "是否终止占用进程并重新启动? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -9 $(lsof -t -i:$PORT) 2>/dev/null
        echo -e "${GREEN}已终止占用进程${NC}"
        sleep 1
    else
        echo -e "${RED}退出启动${NC}"
        exit 1
    fi
fi

# 创建日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/api_proxy_$(date +%Y%m%d_%H%M%S).log"

# 启动服务
echo -e "${GREEN}启动API代理服务...${NC}"
echo -e "${YELLOW}日志文件: $LOG_FILE${NC}"
echo ""

cd "$SCRIPT_DIR"

# 启动Python服务（后台运行）
nohup python3 api_key_proxy.py > "$LOG_FILE" 2>&1 &
PID=$!

echo -e "${GREEN}服务已启动，PID: $PID${NC}"
echo $PID > "${LOG_DIR}/api_proxy.pid"

# 等待服务启动
sleep 2

# 检查服务是否运行
if ps -p $PID > /dev/null; then
    echo -e "${GREEN}✓ API代理服务运行中${NC}"
    echo ""
    echo -e "${BLUE}服务信息:${NC}"
    echo "  URL: http://$HOST:$PORT"
    echo "  PID: $PID"
    echo "  日志: tail -f $LOG_FILE"
    echo ""
    echo -e "${YELLOW}提示: 使用 ./stop_all_services.sh 停止服务${NC}"
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo -e "${RED}查看日志: cat $LOG_FILE${NC}"
    exit 1
fi