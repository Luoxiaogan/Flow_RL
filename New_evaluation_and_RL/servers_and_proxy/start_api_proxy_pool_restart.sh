#!/bin/bash
################################################################################
# API 代理启动脚本（多 API 池 + 120 s 无连接自动重启）
# 改动：Python 进程实时打印到终端，同时写日志
################################################################################

# ---------- 环境 ----------
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"
export PYTHONUNBUFFERED=1

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
[ ! -f "$CONFIG_FILE" ] && { echo "错误: 主配置文件不存在: $CONFIG_FILE"; exit 1; }

# ---------- 基本配置 ----------
PORT=$(python3 -c "import yaml;c=yaml.safe_load(open('$CONFIG_FILE'));print(c['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo 5059)
DEBUG=$(python3 -c "import yaml;c=yaml.safe_load(open('$CONFIG_FILE'));print(str(c['services']['metagpt_api_proxy'].get('debug',False)).lower())" 2>/dev/null || echo false)

# 端口冲突强制清理
if lsof -i :$PORT &>/dev/null; then
    echo "端口 $PORT 被占用，正在清理旧进程..."
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null
    sleep 1
fi

# 日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/api_proxy_pool_$(date +%Y%m%d_%H%M%S).log"

################################################################################
# 120 秒无连接自动重启逻辑
################################################################################
IDLE_LIMIT=120
LAST_TS_FILE="/tmp/last_activity_${PORT}.tmp"
echo $(date +%s) > "$LAST_TS_FILE"
update_ts() { date +%s > "$LAST_TS_FILE"; }

# tcpdump：捕获任何到监听端口的 SYN
tcpdump -i any -nn -l "tcp[tcpflags] & (tcp-syn) != 0 and dst port $PORT" 2>/dev/null \
| while read -r _; do update_ts; done &
TCPDUMP_PID=$!

# 启动服务函数（前台实时输出）
start_service() {
    update_ts
    cd "${PROJECT_ROOT}/metagpt_api_key_proxy"
    # 关键：exec 让 python 直接占用前台，保证终端可见
    exec python3 -u api_key_proxy_pool.py 2>&1 | \
        awk '{print strftime("[%Y-%m-%d %H:%M:%S]"), $0}' | tee -a "$LOG_FILE"
}

# 监控循环（后台定时重启当前脚本）
(
while true; do
    sleep 10
    IDLE=$(( $(date +%s) - $(cat "$LAST_TS_FILE") ))
    if [ "$IDLE" -ge "$IDLE_LIMIT" ]; then
        echo "[$(date '+%F %T')] 已 $IDLE 秒无新连接，重启..."
        pkill -P $$ -f api_key_proxy_pool.py   # 杀掉前台 python
        sleep 2
        exec "$0" "$@"                         # 重新拉起自己
    fi
done
) &
MONITOR_PID=$!

################################################################################
# 首次启动
################################################################################
start_service
