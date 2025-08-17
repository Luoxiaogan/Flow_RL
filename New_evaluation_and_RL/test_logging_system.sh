#!/bin/bash

# ============================================
# 测试Workflow执行日志保存系统
# ============================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   测试Workflow日志保存系统${NC}"
echo -e "${BLUE}========================================${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 步骤1：检查服务状态
echo -e "\n${YELLOW}步骤1: 检查服务状态${NC}"

# 检查API代理服务
echo -n "检查API代理服务 (端口5009)... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5009/ | grep -q "404\|200"; then
    echo -e "${GREEN}✓ 运行中${NC}"
else
    echo -e "${RED}✗ 未运行${NC}"
    echo -e "${YELLOW}正在启动API代理服务...${NC}"
    bash "$SCRIPT_DIR/servers_and_proxy/start_api_proxy.sh" &
    sleep 3
fi

# 检查ScoreFlow Reward服务
echo -n "检查ScoreFlow Reward服务 (端口8899)... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8899/health | grep -q "200"; then
    echo -e "${GREEN}✓ 运行中${NC}"
else
    echo -e "${RED}✗ 未运行${NC}"
    echo -e "${YELLOW}正在启动ScoreFlow Reward服务...${NC}"
    bash "$SCRIPT_DIR/servers_and_proxy/start_scoreflow_reward.sh" &
    sleep 5
fi

# 步骤2：创建workspace目录
echo -e "\n${YELLOW}步骤2: 准备workspace目录${NC}"
WORKSPACE_DIR="$SCRIPT_DIR/workspace"
if [ ! -d "$WORKSPACE_DIR" ]; then
    mkdir -p "$WORKSPACE_DIR"
    echo -e "${GREEN}✓ 创建workspace目录: $WORKSPACE_DIR${NC}"
else
    echo -e "${GREEN}✓ Workspace目录已存在${NC}"
fi

# 步骤3：运行测试
echo -e "\n${YELLOW}步骤3: 运行测试脚本${NC}"
echo "----------------------------------------"
python3 "$SCRIPT_DIR/tests/test_workflow_logging.py"
TEST_RESULT=$?

# 步骤4：检查结果
echo -e "\n${YELLOW}步骤4: 检查测试结果${NC}"

if [ $TEST_RESULT -eq 0 ]; then
    # 找到最新的workflow目录
    LATEST_WORKFLOW=$(ls -td "$WORKSPACE_DIR"/gsm8k/workflow_* 2>/dev/null | head -1)
    
    if [ -n "$LATEST_WORKFLOW" ]; then
        echo -e "${GREEN}✓ 测试成功!${NC}"
        echo -e "\n${BLUE}生成的文件:${NC}"
        ls -la "$LATEST_WORKFLOW"
        
        echo -e "\n${BLUE}查看日志文件:${NC}"
        echo "  查看workflow代码: cat $LATEST_WORKFLOW/workflow.py"
        echo "  查看执行汇总: cat $LATEST_WORKFLOW/summary.json | jq ."
        echo "  查看结果CSV: cat $LATEST_WORKFLOW/results.csv"
        echo "  查看测试日志: cat $LATEST_WORKFLOW/test_case_0.log"
    else
        echo -e "${YELLOW}⚠️ 测试运行但未找到生成的文件${NC}"
    fi
else
    echo -e "${RED}✗ 测试失败${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}   测试完成${NC}"
echo -e "${BLUE}========================================${NC}"

# 询问是否停止服务
echo -e "\n${YELLOW}是否停止测试服务? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "停止服务..."
    pkill -f "api_key_proxy_enhanced.py" 2>/dev/null
    pkill -f "scoreflow_reward_server.py" 2>/dev/null
    echo -e "${GREEN}✓ 服务已停止${NC}"
fi