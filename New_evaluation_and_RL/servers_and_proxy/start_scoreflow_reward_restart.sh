#!/bin/bash
################################################################################
# ScoreFlow Reward 服务启动脚本（保留原生实时输出 + 无连接自动重启）
################################################################################

# 清除代理设置
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
export NO_PROXY="localhost,127.0.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

# 颜色定义
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    ScoreFlow Reward服务启动器${NC}"
echo -e "${BLUE}========================================${NC}"

# 脚本路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 解析参数
DEBUG_MODE=false
for arg in "$@"; do
    [[ "$arg" == "--debug" ]] && DEBUG_MODE=true
done

# 读取配置（使用 Python）
PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['scoreflow_reward']['port'])" 2>/dev/null || echo 8899)
HOST=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['scoreflow_reward']['host'])" 2>/dev/null || echo "0.0.0.0")
API_PROXY_PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo 5009)
ENABLED=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['scoreflow_reward']['enabled'])" 2>/dev/null || echo True)

# MetaGPT 环境变量
METAGPT_CONFIG_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('paths',{}).get('metagpt_config',''))" 2>/dev/null)
if [ -n "$METAGPT_CONFIG_PATH" ]; then
    METAGPT_ROOT=$(dirname "$(dirname "$METAGPT_CONFIG_PATH")")
    export METAGPT_CONFIG="$METAGPT_CONFIG_PATH"
    export METAGPT_PROJECT_ROOT="$METAGPT_ROOT"
    export METAGPT_WORKSPACE="$METAGPT_ROOT/workspace"
    export METAGPT_LOG_DIR="$METAGPT_ROOT/logs"
    export METAGPT_DATA_PATH="$METAGPT_ROOT/data"
fi

# LLM 设置
API_KEY=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('llm_settings',{}).get('key','sk-placeholder'))" 2>/dev/null)
MODEL=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('llm_settings',{}).get('model','qwen-turbo'))" 2>/dev/null)
export OPENAI_API_KEY="$API_KEY"
export OPENAI_API_BASE="http://localhost:$API_PROXY_PORT"
export OPENAI_API_MODEL="$MODEL"

# 检查是否启用
if [ "$ENABLED" != "True" ] && [ "$ENABLED" != "true" ]; then
    echo -e "${YELLOW}Reward 服务已禁用 (enabled=false)，退出。${NC}"
    exit 0
fi

# 检查 API Proxy 健康状态
echo -e "${YELLOW}检查 API 代理连通性...${NC}"
if curl -s -f -o /dev/null -w "%{http_code}" http://localhost:$API_PROXY_PORT/health | grep -q "200"; then
    echo -e "${GREEN}✓ API代理服务正常 (http://localhost:$API_PROXY_PORT)${NC}"
else
    echo -e "${RED}⚠️ 无法访问 API 代理服务，请先启动它${NC}"
    read -p "是否继续？(y/N): " -n1 -r; echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

# 端口占用处理
if lsof -i :$PORT &>/dev/null; then
    echo -e "${YELLOW}端口 $PORT 被占用，正在终止旧进程...${NC}"
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null || true
    sleep 1
fi

# 创建日志目录
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/scoreflow_reward_$(date +%Y%m%d_%H%M%S).log"

if [ "$DEBUG_MODE" = true ]; then
    mkdir -p "$PROJECT_ROOT/debug_logs"
    echo -e "${YELLOW}📝 Debug模式开启，日志将保存至 debug_logs/${NC}"
fi

# 显示信息
echo -e "${GREEN}配置完成${NC}"
echo "  地址: http://$HOST:$PORT"
echo "  日志: $LOG_FILE"
echo -e "${YELLOW}提示: 按 Ctrl+C 可停止服务${NC}"
echo -e "${BLUE}========================================${NC}"

# === 关键设计：主服务与监控分离 ===

# 临时文件用于通信
LAST_CONN_FILE="/tmp/reward_last_conn_${PORT}.ts"
echo $(date +%s) > "$LAST_CONN_FILE"

# 启动 tcpdump 监听 Reward → API_Proxy 的新连接（SYN包）
tcpdump -i any -nn -l \
    "tcp[tcpflags] & tcp-syn != 0 and src host $HOST and dst port $API_PROXY_PORT" 2>/dev/null \
    | stdbuf -oL awk '{print "conn"}' \
    | while read _; do
        echo $(date +%s) > "$LAST_CONN_FILE"
      done &
TCPDUMP_PID=$!

# 后台监控任务：每10秒检查一次空闲时间
(
while true; do
    sleep 10
    last_ts=$(cat "$LAST_CONN_FILE" 2>/dev/null || echo 0)
    idle=$(( $(date +%s) - last_ts ))

    if [ $idle -ge 120 ]; then
        echo -e "\n[$(date '+%F %T')] ${RED}⛔ 120秒未检测到新连接，准备重启服务...${NC}"
        pkill -f "scoreflow_reward_server.py"  # 杀掉主服务
        sleep 1
        exit 0  # 让外层重新执行
    fi
done
) &
MONITOR_PID=$!

# 清理函数
cleanup() {
    echo -e "\n[${BLUE}$(date '+%F %T')${NC}] 服务停止中..."
    kill $TCPDUMP_PID $MONITOR_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# === 主服务：保持最简洁的输出链路！===
cd "$PROJECT_ROOT/reward_server" || exit 1

CMD="python3 -u scoreflow_reward_server.py --port $PORT --host $HOST"
[ "$DEBUG_MODE" = true ] && CMD="$CMD --debug"

# 🔥 核心：只用 tee，不用 awk，不加额外处理，保证实时性！
echo -e "${GREEN}🚀 启动服务...${NC}"
exec stdbuf -oL -eL $CMD 2>&1 | tee -a "$LOG_FILE"
