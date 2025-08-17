#!/bin/bash

# ============================================
# 启动所有评估相关服务
# ============================================

unset http_proxy https_proxy all_proxy
echo "已清除代理设置"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}     启动所有评估服务${NC}"
echo -e "${CYAN}========================================${NC}"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 读取模式
MODE=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['model']['mode'])" 2>/dev/null)
echo -e "${BLUE}当前评估模式: $MODE${NC}"
echo ""

# 启动函数
start_service() {
    local service_name=$1
    local script_name=$2
    local port=$3
    
    echo -e "${YELLOW}检查 $service_name...${NC}"
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $service_name 已在运行 (端口: $port)${NC}"
    else
        echo -e "${YELLOW}启动 $service_name...${NC}"
        cd "$SCRIPT_DIR"
        ./$script_name > /dev/null 2>&1 &
        sleep 3
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${GREEN}✓ $service_name 启动成功${NC}"
        else
            echo -e "${RED}✗ $service_name 启动失败${NC}"
            return 1
        fi
    fi
    echo ""
    return 0
}

# 记录启动状态
all_success=true

# 1. 启动MetaGPT API代理（用于workflow执行）
METAGPT_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['port'])" 2>/dev/null)
if ! start_service "MetaGPT API代理" "start_api_proxy.sh" "$METAGPT_PORT"; then
    all_success=false
fi

# 2. 根据模式启动评估API代理
if [ "$MODE" = "evaluation_api" ]; then
    EVAL_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['evaluation_api_proxy']['port'])" 2>/dev/null)
    if ! start_service "评估API代理" "start_evaluation_api_proxy.sh" "$EVAL_PORT"; then
        all_success=false
    fi
elif [ "$MODE" = "local" ]; then
    echo -e "${BLUE}本地模式：将在评估时自动启动SGLang服务器${NC}"
    echo ""
fi

# 3. 启动ScoreFlow Reward服务
SKIP_SCORING=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['evaluation'].get('skip_scoring', False))" 2>/dev/null)
if [ "$SKIP_SCORING" != "True" ]; then
    REWARD_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['port'])" 2>/dev/null)
    if ! start_service "ScoreFlow Reward服务" "start_scoreflow_reward.sh" "$REWARD_PORT"; then
        all_success=false
    fi
else
    echo -e "${YELLOW}跳过ScoreFlow Reward服务（skip_scoring=true）${NC}"
    echo ""
fi

# 显示结果
echo -e "${CYAN}========================================${NC}"
if [ "$all_success" = true ]; then
    echo -e "${GREEN}✓ 所有服务启动成功！${NC}"
    echo ""
    echo "服务状态:"
    echo "  MetaGPT API代理: http://localhost:$METAGPT_PORT"
    
    if [ "$MODE" = "evaluation_api" ]; then
        echo "  评估API代理: http://localhost:$EVAL_PORT"
    fi
    
    if [ "$SKIP_SCORING" != "True" ]; then
        echo "  ScoreFlow Reward: http://localhost:$REWARD_PORT/health"
    fi
    
    echo ""
    echo -e "${BLUE}下一步：运行评估${NC}"
    echo "  cd $PROJECT_ROOT/scripts"
    echo "  ./run_evaluation.sh"
else
    echo -e "${RED}✗ 部分服务启动失败${NC}"
    echo "请检查日志文件了解详情:"
    echo "  ls -la $PROJECT_ROOT/logs/"
    exit 1
fi

echo -e "${CYAN}========================================${NC}"
echo ""
echo "提示: 停止所有服务请运行:"
echo "  ./stop_all_services.sh"