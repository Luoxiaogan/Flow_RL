#!/bin/bash

# ============================================
# ScoreFlow Reward Server 监控器
# ============================================
# 实时监控reward server的并发状态和性能指标
#
# 使用方法:
#   bash monitor_reward_server.sh          # 默认监控 localhost:8899
#   bash monitor_reward_server.sh 8900     # 监控指定端口
#   bash monitor_reward_server.sh --once   # 只查询一次状态
#
# 功能:
#   - 每秒刷新一次状态
#   - 显示并发使用情况、队列长度、统计信息
#   - 显示活跃任务列表

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# 默认配置
DEFAULT_PORT=8899
REFRESH_INTERVAL=1

# 解析参数
PORT=$DEFAULT_PORT
ONCE_MODE=false

for arg in "$@"; do
    case $arg in
        --once)
            ONCE_MODE=true
            shift
            ;;
        [0-9]*)
            PORT=$arg
            shift
            ;;
        *)
            ;;
    esac
done

# 服务器URL
SERVER_URL="http://localhost:$PORT"

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"

# 从配置文件读取API代理端口
API_PROXY_PORT=5009  # 默认值
if [ -f "$CONFIG_FILE" ]; then
    API_PROXY_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config.get('services', {}).get('metagpt_api_proxy', {}).get('port', 5009))" 2>/dev/null || echo "5009")
fi

# 检查API代理服务连通性
check_api_proxy() {
    echo -e "${CYAN}检查 API 代理服务...${NC}"
    
    # 尝试连接API代理的健康检查端点
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$API_PROXY_PORT/health" 2>/dev/null | grep -q "200"; then
        echo -e "${GREEN}✅ API代理服务 (localhost:$API_PROXY_PORT) 连接正常${NC}"
        return 0
    else
        echo -e "${RED}❌ 无法连接到 API代理服务 (localhost:$API_PROXY_PORT)${NC}"
        echo -e "${YELLOW}提示: API代理用于LLM调用，是Reward Server的依赖服务${NC}"
        echo -e "${YELLOW}请先启动: bash servers_and_proxy/start_api_proxy.sh${NC}"
        return 1
    fi
}

# 检查Reward服务器连通性
check_reward_server() {
    echo -e "${CYAN}检查 ScoreFlow Reward Server...${NC}"
    
    # 尝试连接健康检查端点
    if curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL/health" 2>/dev/null | grep -q "200"; then
        echo -e "${GREEN}✅ ScoreFlow Reward Server ($SERVER_URL) 连接正常${NC}"
        
        # 获取并显示服务配置
        config_json=$(curl -s "$SERVER_URL/config" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$config_json" ]; then
            echo -e "${CYAN}服务配置:${NC}"
            echo "$config_json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
server_config = data.get('server_config', {})
print(f\"  最大并发: {server_config.get('max_concurrent_requests', 'N/A')}\")
print(f\"  排队超时: {server_config.get('request_queue_timeout', 'N/A')}秒\")
print(f\"  处理超时: {server_config.get('timeout', 'N/A')}秒\")
benchmarks = data.get('benchmarks', [])
if benchmarks:
    print(f\"  支持的benchmarks: {', '.join(benchmarks[:5])}\")
    if len(benchmarks) > 5:
        print(f\"                    ... 等共{len(benchmarks)}个\")
" 2>/dev/null || echo "  无法解析配置信息"
        fi
        return 0
    else
        echo -e "${RED}❌ 无法连接到 ScoreFlow Reward Server ($SERVER_URL)${NC}"
        echo -e "${YELLOW}请确保服务已启动: bash servers_and_proxy/start_scoreflow_reward.sh${NC}"
        return 1
    fi
}

# 检查所有依赖服务
check_all_services() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BOLD}${BLUE}检查服务依赖${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo
    
    # 检查API代理
    api_proxy_ok=false
    if check_api_proxy; then
        api_proxy_ok=true
    fi
    echo
    
    # 检查Reward服务器
    reward_server_ok=false
    if check_reward_server; then
        reward_server_ok=true
    fi
    echo
    
    # 检查结果
    if [ "$api_proxy_ok" = true ] && [ "$reward_server_ok" = true ]; then
        echo -e "${GREEN}✅ 所有服务检查通过，可以开始监控${NC}"
        echo -e "${BLUE}============================================================${NC}"
        echo
        return 0
    else
        echo -e "${RED}❌ 服务检查未通过${NC}"
        
        if [ "$api_proxy_ok" = false ] && [ "$reward_server_ok" = false ]; then
            echo -e "${YELLOW}请按以下顺序启动服务:${NC}"
            echo -e "${YELLOW}  1. bash servers_and_proxy/start_api_proxy.sh${NC}"
            echo -e "${YELLOW}  2. bash servers_and_proxy/start_scoreflow_reward.sh${NC}"
        elif [ "$api_proxy_ok" = false ]; then
            echo -e "${YELLOW}请先启动API代理服务${NC}"
        else
            echo -e "${YELLOW}请启动Reward服务器${NC}"
        fi
        
        echo -e "${BLUE}============================================================${NC}"
        exit 1
    fi
}

# 格式化JSON输出
format_status() {
    local json_data="$1"
    
    # 使用Python美化输出
    python3 - <<EOF
import json
import sys
from datetime import datetime

data = json.loads('''$json_data''')

# 服务器URL从环境变量传入
SERVER_URL = "$SERVER_URL"

# 颜色码
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'
BOLD = '\033[1m'

# 打印标题
print(f"{BLUE}{'='*60}{NC}")
print(f"{BOLD}{BLUE}    ScoreFlow Reward Server 监控 - {SERVER_URL}{NC}")
print(f"{BLUE}{'='*60}{NC}")

# 服务器时间
print(f"{CYAN}服务器时间:{NC} {data.get('server_time', 'N/A')}")
print()

# 并发状态
concurrency = data.get('concurrency', {})
active = concurrency.get('active_requests', 0)
max_concurrent = concurrency.get('max_concurrent', 5)
available = concurrency.get('available_slots', 0)
queued = concurrency.get('queued_requests', 0)

# 计算使用率百分比
usage_percent = (active / max_concurrent * 100) if max_concurrent > 0 else 0

# 生成进度条
bar_length = 40
filled_length = int(bar_length * active / max_concurrent) if max_concurrent > 0 else 0
bar = '█' * filled_length + '░' * (bar_length - filled_length)

# 选择颜色
if usage_percent >= 80:
    color = RED
elif usage_percent >= 60:
    color = YELLOW
else:
    color = GREEN

print(f"{BOLD}📊 并发状态{NC}")
print(f"  使用率: {color}[{bar}] {active}/{max_concurrent} ({usage_percent:.1f}%){NC}")
print(f"  可用槽位: {GREEN if available > 0 else RED}{available}{NC}")
print(f"  排队请求: {YELLOW if queued > 0 else GREEN}{queued}{NC}")
print()

# 统计信息
stats = data.get('statistics', {})
total = stats.get('total_processed', 0)
succeeded = stats.get('total_succeeded', 0)
failed = stats.get('total_failed', 0)
timeout = stats.get('total_timeout', 0)
success_rate = stats.get('success_rate', 0)
avg_wait = stats.get('average_wait_time', 0)
avg_process = stats.get('average_process_time', 0)

print(f"{BOLD}📈 统计信息{NC}")
print(f"  总处理: {total}  成功: {GREEN}{succeeded}{NC}  失败: {RED}{failed}{NC}  超时: {YELLOW}{timeout}{NC}")
print(f"  成功率: {GREEN if success_rate >= 90 else YELLOW if success_rate >= 70 else RED}{success_rate:.1f}%{NC}")
print(f"  平均等待: {CYAN}{avg_wait:.2f}s{NC}  平均处理: {CYAN}{avg_process:.2f}s{NC}")
print()

# 活跃任务
tasks = data.get('active_tasks', [])
if tasks:
    print(f"{BOLD}🔄 活跃任务 ({len(tasks)}){NC}")
    for task in tasks:
        task_id = task.get('id', 'N/A')
        benchmark = task.get('benchmark', 'unknown')
        duration = task.get('duration', 0)
        wait_time = task.get('wait_time', 0)
        
        # 根据执行时间选择颜色
        if duration > 30:
            dur_color = RED
        elif duration > 15:
            dur_color = YELLOW
        else:
            dur_color = GREEN
        
        print(f"  [{task_id:3d}] {benchmark:15s} - 运行: {dur_color}{duration:6.2f}s{NC}  等待: {wait_time:.2f}s")
else:
    print(f"{BOLD}🔄 活跃任务{NC}")
    print(f"  {GREEN}当前无活跃任务{NC}")

print()
print(f"{BLUE}{'='*60}{NC}")
EOF
}

# 显示监控信息
show_monitor() {
    # 清屏
    clear
    
    # 获取状态
    status_json=$(curl -s "$SERVER_URL/status" 2>/dev/null)
    
    if [ $? -ne 0 ] || [ -z "$status_json" ]; then
        echo -e "${RED}❌ 无法获取服务器状态${NC}"
        return 1
    fi
    
    # 格式化并显示
    format_status "$status_json"
    
    # 显示提示信息
    if [ "$ONCE_MODE" = false ]; then
        echo -e "${YELLOW}按 Ctrl+C 退出监控   [自动刷新: ${REFRESH_INTERVAL}秒]${NC}"
    fi
}

# 主函数
main() {
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 需要Python3来格式化输出${NC}"
        exit 1
    fi
    
    # 检查curl
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}错误: 需要curl来查询服务器${NC}"
        exit 1
    fi
    
    # 检查yaml模块
    if ! python3 -c "import yaml" 2>/dev/null; then
        echo -e "${YELLOW}警告: Python yaml模块未安装，使用默认配置${NC}"
        echo -e "${YELLOW}建议安装: pip install pyyaml${NC}"
    fi
    
    # 显示监控器信息
    echo -e "${BOLD}${CYAN}ScoreFlow Reward Server 监控器${NC}"
    echo -e "${CYAN}版本: 1.0.0${NC}"
    echo
    
    # 检查所有依赖服务
    check_all_services
    
    # 等待一下让用户看到检查结果
    if [ "$ONCE_MODE" = false ]; then
        echo -e "${GREEN}3秒后开始监控...${NC}"
        sleep 3
    fi
    
    if [ "$ONCE_MODE" = true ]; then
        # 只显示一次
        show_monitor
    else
        # 循环监控
        trap "echo -e '\n${GREEN}监控已停止${NC}'; exit 0" INT TERM
        
        while true; do
            show_monitor
            sleep $REFRESH_INTERVAL
        done
    fi
}

# 运行主函数
main