#!/bin/bash

# ============================================
# ScoreFlow Reward服务启动脚本
# ============================================
# 用于workflow执行和评分计算
#
# 使用方法:
#   bash start_scoreflow_reward.sh          # 正常模式
#   bash start_scoreflow_reward.sh --debug  # 调试模式（开启详细日志）
#
# 调试模式说明:
#   - Flask服务器以debug模式运行，显示详细错误信息
#   - 生成debug日志文件到 debug_logs/ 目录
#   - 记录每个workflow的执行详情、LLM调用、耗时等

# 清除代理设置，避免干扰本地服务通信
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY来排除localhost（即使Clash开启系统代理也有效）
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo "✓ 已清除代理设置并设置NO_PROXY"
echo "  NO_PROXY='$NO_PROXY'"
echo "  localhost请求将绕过所有代理"

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

# 从YAML提取配置（使用Python解析）
echo -e "${YELLOW}读取配置文件...${NC}"
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['port'])" 2>/dev/null || echo "8899")
HOST=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['host'])" 2>/dev/null || echo "0.0.0.0")
ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['enabled'])" 2>/dev/null || echo "True")
TIMEOUT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['timeout'])" 2>/dev/null || echo "300")

# 提取MetaGPT相关配置并设置环境变量
echo -e "${YELLOW}配置MetaGPT环境变量...${NC}"

# 获取MetaGPT配置文件路径
METAGPT_CONFIG_PATH=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['paths']['metagpt_config'])" 2>/dev/null || echo "")
if [ -n "$METAGPT_CONFIG_PATH" ]; then
    # 从配置路径推导出metagpt_root（去掉/config/config2.yaml部分）
    METAGPT_ROOT=$(dirname $(dirname "$METAGPT_CONFIG_PATH"))
    echo "  MetaGPT根目录: $METAGPT_ROOT"
    echo "  MetaGPT配置文件: $METAGPT_CONFIG_PATH"
    
    # 设置MetaGPT环境变量
    export METAGPT_CONFIG="$METAGPT_CONFIG_PATH"
    export METAGPT_PROJECT_ROOT="$METAGPT_ROOT"
    export METAGPT_WORKSPACE="$METAGPT_ROOT/workspace"
    export METAGPT_LOG_DIR="$METAGPT_ROOT/logs"
    export METAGPT_DATA_PATH="$METAGPT_ROOT/data"
fi

# 获取API代理配置
API_PROXY_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo "5009")
API_KEY=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['llm_settings']['key'])" 2>/dev/null || echo "sk-placeholder")
MODEL=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['llm_settings']['model'])" 2>/dev/null || echo "qwen-turbo")

# 设置OpenAI兼容的环境变量（MetaGPT也会使用这些）
export OPENAI_API_KEY="$API_KEY"
export OPENAI_API_BASE="http://localhost:$API_PROXY_PORT"
export OPENAI_API_MODEL="$MODEL"

echo -e "${GREEN}✓ MetaGPT环境变量已设置${NC}"

# 检查API代理服务连通性
echo -e "${YELLOW}检查API代理服务连通性...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$API_PROXY_PORT/health | grep -q "200"; then
    echo -e "${GREEN}✓ API代理服务 (localhost:$API_PROXY_PORT) 连接成功${NC}"
else
    echo -e "${RED}⚠️  警告: 无法连接到API代理服务 (localhost:$API_PROXY_PORT)${NC}"
    echo -e "${YELLOW}   请确保已启动: bash servers_and_proxy/start_api_proxy.sh${NC}"
    echo ""
    read -p "是否继续启动? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}退出启动${NC}"
        exit 1
    fi
fi

if [ "$ENABLED" != "True" ]; then
    echo -e "${YELLOW}ScoreFlow Reward服务已禁用（config.yaml中enabled=false）${NC}"
    exit 0
fi

echo -e "${GREEN}配置信息:${NC}"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  超时: ${TIMEOUT}秒"
if [ "$DEBUG_MODE" = true ]; then
    echo -e "  ${YELLOW}调试模式: 已启用${NC}"
fi
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

# 如果是debug模式，创建debug日志目录
if [ "$DEBUG_MODE" = true ]; then
    DEBUG_LOG_DIR="${PROJECT_ROOT}/debug_logs"
    mkdir -p "$DEBUG_LOG_DIR"
    echo -e "${YELLOW}📝 Debug日志将保存到: $DEBUG_LOG_DIR${NC}"
fi

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
cd "${PROJECT_ROOT}/reward_server"

# 构建启动命令
CMD="python3 scoreflow_reward_server.py --port $PORT --host $HOST"

# 如果启用debug模式，添加--debug参数
if [ "$DEBUG_MODE" = true ]; then
    CMD="$CMD --debug"
    echo -e "${YELLOW}🔍 Flask服务器将以调试模式运行${NC}"
    echo -e "${YELLOW}📂 Debug数据将保存到: ${DEBUG_LOG_DIR}${NC}"
    echo ""
fi

# 启动Python服务（前台运行，同时输出到终端和日志文件）
$CMD 2>&1 | tee "$LOG_FILE"