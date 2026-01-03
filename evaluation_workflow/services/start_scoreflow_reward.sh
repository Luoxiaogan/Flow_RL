#!/bin/bash

# ============================================
# ScoreFlow Reward服务启动脚本
# ============================================
# 用于workflow执行和评分计算

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    ScoreFlow Reward服务启动器${NC}"
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
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['port'])" 2>/dev/null || echo "8899")
HOST=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['host'])" 2>/dev/null || echo "0.0.0.0")
ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['enabled'])" 2>/dev/null || echo "True")
TIMEOUT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['timeout'])" 2>/dev/null || echo "300")

if [ "$ENABLED" != "True" ]; then
    echo -e "${YELLOW}ScoreFlow Reward服务已禁用（config.yaml中enabled=false）${NC}"
    exit 0
fi

echo -e "${GREEN}配置信息:${NC}"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  超时: ${TIMEOUT}秒"
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
LOG_FILE="${LOG_DIR}/scoreflow_reward_$(date +%Y%m%d_%H%M%S).log"

# 显示服务信息
echo -e "${GREEN}✓ 正在启动ScoreFlow Reward服务...${NC}"
echo ""
echo -e "${BLUE}服务信息:${NC}"
echo "  URL: http://$HOST:$PORT"
echo "  日志: $LOG_FILE"
echo ""
echo -e "${YELLOW}提示: 按 Ctrl+C 停止服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 切换到scoreflow目录
cd "${PROJECT_ROOT}/scoreflow"

# 启动Python服务（前台运行，同时输出到终端和日志文件）
python3 scoreflow_reward_server.py --port $PORT --host $HOST 2>&1 | tee "$LOG_FILE"