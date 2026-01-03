#!/bin/bash

# ============================================
# MetaGPT API代理服务启动脚本
# ============================================
# 用于MetaGPT operator执行时的API调用

unset http_proxy https_proxy all_proxy
echo "已清除代理设置"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}     MetaGPT API代理服务启动器${NC}"
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
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo "5009")
HOST=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['host'])" 2>/dev/null || echo "localhost")
ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['enabled'])" 2>/dev/null || echo "True")

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

# 检查是否有配置target_api_key
TARGET_API_KEY=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy'].get('target_api_key', ''))" 2>/dev/null || echo "")

# 选择使用哪个版本的proxy
if [ -n "$TARGET_API_KEY" ] && [ "$TARGET_API_KEY" != "your-target-api-key-here" ]; then
    echo -e "${GREEN}使用增强版API代理（配置了目标API密钥）${NC}"
    PROXY_SCRIPT="api_key_proxy_enhanced.py"
    # 检查增强版是否存在
    if [ ! -f "$PROXY_SCRIPT" ]; then
        echo -e "${YELLOW}增强版不存在，使用基础版${NC}"
        PROXY_SCRIPT="api_key_proxy.py"
    fi
else
    echo -e "${YELLOW}使用基础版API代理（透传模式）${NC}"
    PROXY_SCRIPT="api_key_proxy.py"
fi

# 显示服务信息
echo -e "${GREEN}✓ 正在启动MetaGPT API代理服务...${NC}"
echo ""
echo -e "${BLUE}服务信息:${NC}"
echo "  URL: http://$HOST:$PORT"
echo "  日志: $LOG_FILE"
echo ""
echo -e "${YELLOW}提示: 按 Ctrl+C 停止服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 启动Python服务（前台运行，同时输出到终端和日志文件）
python3 $PROXY_SCRIPT 2>&1 | tee "$LOG_FILE"