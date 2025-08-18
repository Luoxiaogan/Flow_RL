#!/bin/bash

# ============================================
# 评估系统主启动脚本
# ============================================
# 功能：检查所有必需服务并执行评估
# 依赖：MetaGPT API代理、ScoreFlow奖励服务器、评估模型服务

set -e  # Exit on error

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
CONFIG_FILE="$PROJECT_ROOT/config.yaml"

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}     🎯 评估系统启动${NC}"
echo -e "${CYAN}============================================${NC}"

# 1. 环境设置
echo -e "${BLUE}🔧 环境设置${NC}"

# 清除代理设置，避免干扰
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"
echo "✓ 已清除代理设置并设置NO_PROXY"

# 激活conda环境
if command -v conda &> /dev/null; then
    echo "✓ 检测到conda，激活workflow环境..."
    source /opt/anaconda3/etc/profile.d/conda.sh
    conda activate workflow
    echo "✓ 已激活conda环境: $(conda env list | grep '*' | awk '{print $1}')"
else
    echo "⚠️ 未检测到conda，使用系统Python环境"
fi

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi
echo "✓ 配置文件: $CONFIG_FILE"

# 设置Python无缓冲输出
export PYTHONUNBUFFERED=1

echo ""

# 2. 服务检查函数
check_service() {
    local service_name=$1
    local port=$2
    local health_endpoint=${3:-"/health"}
    local start_script=$4
    
    echo -e "${BLUE}🔍 检查 $service_name (端口 $port)${NC}"
    
    # 检查端口是否监听
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo -e "${RED}❌ $service_name 未运行 (端口 $port 无监听)${NC}"
        if [ -n "$start_script" ]; then
            echo -e "${YELLOW}   请先启动: bash $start_script${NC}"
        fi
        return 1
    fi
    
    # 检查健康状态
    local health_url="http://localhost:$port$health_endpoint"
    if curl -s --max-time 5 "$health_url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name 运行正常${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ $service_name 端口已占用但健康检查失败${NC}"
        echo -e "${YELLOW}   健康检查: $health_url${NC}"
        # 对于某些服务，健康检查失败不一定意味着无法使用
        # 让用户决定是否继续
        return 0
    fi
}

# 3. 检查必需服务
echo -e "${BLUE}🔍 检查必需服务${NC}"
echo ""

services_ok=true

# 检查MetaGPT API代理
if ! check_service "MetaGPT API代理" 5009 "/" "../servers_and_proxy/start_api_proxy.sh"; then
    services_ok=false
fi

# 检查ScoreFlow奖励服务器
if ! check_service "ScoreFlow奖励服务器" 8899 "/health" "../servers_and_proxy/start_scoreflow_reward.sh"; then
    services_ok=false
fi

# 检查评估模型服务（根据配置模式）
echo ""
echo -e "${BLUE}📝 检查评估模型服务配置${NC}"

# 读取模型模式
if ! MODE=$(python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print(config.get('model', {}).get('mode', 'evaluation_api'))
except Exception as e:
    print('evaluation_api')
" 2>/dev/null); then
    MODE="evaluation_api"
fi

echo "📋 模型模式: $MODE"

# 根据模式检查相应服务
if [ "$MODE" = "evaluation_api" ]; then
    if ! check_service "评估API代理" 5010 "/" "../servers_and_proxy/start_evaluation_server.sh"; then
        echo -e "${YELLOW}🚀 尝试自动启动评估API代理...${NC}"
        cd "$PROJECT_ROOT"
        if bash servers_and_proxy/start_evaluation_server.sh > /dev/null 2>&1 &
        then
            sleep 8  # 等待服务启动
            if check_service "评估API代理" 5010 "/" ""; then
                echo -e "${GREEN}✅ 评估API代理自动启动成功${NC}"
            else
                echo -e "${RED}❌ 评估API代理自动启动失败${NC}"
                services_ok=false
            fi
        else
            echo -e "${RED}❌ 无法自动启动评估API代理${NC}"
            services_ok=false
        fi
        cd "$SCRIPT_DIR"
    fi
elif [ "$MODE" = "local" ]; then
    # 读取本地服务器端口
    LOCAL_PORT=$(python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print(config.get('model', {}).get('local', {}).get('port', 30009))
except:
    print('30009')
" 2>/dev/null)
    
    # SGLang使用不同的健康检查方式，尝试多个端点
    echo -e "${BLUE}🔍 检查 SGLang本地服务器 (端口 $LOCAL_PORT)${NC}"
    
    # 检查端口是否监听
    if ! lsof -i :$LOCAL_PORT > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ SGLang本地服务器未运行 (端口 $LOCAL_PORT 无监听)${NC}"
        echo -e "${YELLOW}   请先启动: bash ../servers_and_proxy/start_evaluation_server.sh${NC}"
        echo -e "${YELLOW}   然后在config.yaml中设置 model.mode: 'local'${NC}"
        services_ok=false
    else
        # 尝试不同的健康检查端点
        health_ok=false
        
        # 尝试 /health 端点
        if curl -s --max-time 5 "http://localhost:$LOCAL_PORT/health" > /dev/null 2>&1; then
            health_ok=true
            echo -e "${GREEN}✅ SGLang本地服务器运行正常 (/health检查通过)${NC}"
        # 尝试 /v1/models 端点 (OpenAI兼容)
        elif curl -s --max-time 5 "http://localhost:$LOCAL_PORT/v1/models" > /dev/null 2>&1; then
            health_ok=true
            echo -e "${GREEN}✅ SGLang本地服务器运行正常 (/v1/models检查通过)${NC}"
        # 尝试 /get_model_info 端点
        elif curl -s --max-time 5 "http://localhost:$LOCAL_PORT/get_model_info" > /dev/null 2>&1; then
            health_ok=true
            echo -e "${GREEN}✅ SGLang本地服务器运行正常 (/get_model_info检查通过)${NC}"
        else
            # 端口已占用但无法验证服务，假定服务正常运行
            echo -e "${YELLOW}⚠️ SGLang本地服务器端口已占用，无法验证健康状态${NC}"
            echo -e "${YELLOW}   假定服务正常运行...${NC}"
            health_ok=true
        fi
        
        if [ "$health_ok" = false ]; then
            echo -e "${RED}❌ SGLang本地服务器未正确运行${NC}"
            services_ok=false
        fi
    fi
else
    echo -e "${RED}❌ 未知的模型模式: $MODE${NC}"
    services_ok=false
fi

echo ""

# 4. 服务状态检查结果
if [ "$services_ok" = false ]; then
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}❌ 服务检查失败${NC}"
    echo -e "${RED}============================================${NC}"
    echo -e "${YELLOW}请确保以下服务正在运行：${NC}"
    echo -e "${YELLOW}1. MetaGPT API代理 (端口5009)${NC}"
    echo -e "${YELLOW}   启动命令: bash ../servers_and_proxy/start_api_proxy.sh${NC}"
    echo -e "${YELLOW}2. ScoreFlow奖励服务器 (端口8899)${NC}"
    echo -e "${YELLOW}   启动命令: bash ../servers_and_proxy/start_scoreflow_reward.sh${NC}"
    if [ "$MODE" = "evaluation_api" ]; then
        echo -e "${YELLOW}3. 评估API代理 (端口5010)${NC}"
        echo -e "${YELLOW}   启动命令: bash ../servers_and_proxy/start_evaluation_server.sh${NC}"
    elif [ "$MODE" = "local" ]; then
        echo -e "${YELLOW}3. SGLang本地服务器 (端口$LOCAL_PORT)${NC}"
        echo -e "${YELLOW}   启动命令: bash ../servers_and_proxy/start_evaluation_server.sh${NC}"
    fi
    echo ""
    echo -e "${YELLOW}或者使用一键启动脚本：${NC}"
    echo -e "${YELLOW}bash ../servers_and_proxy/start_all_services.sh${NC}"
    exit 1
fi

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ 所有服务检查通过${NC}"
echo -e "${GREEN}============================================${NC}"

# 5. 显示评估配置信息
echo -e "${BLUE}📊 评估配置信息${NC}"
echo "模型模式: $MODE"

# 读取测试数据路径
TEST_DATA=$(python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print(config.get('evaluation', {}).get('test_data', '../Test_FILE/verl_support/data/gsm8k/test.parquet'))
except:
    print('../Test_FILE/verl_support/data/gsm8k/test.parquet')
" 2>/dev/null)

echo "测试数据: $TEST_DATA"

# 检查测试数据是否存在
if [ ! -f "$TEST_DATA" ]; then
    echo -e "${RED}❌ 测试数据文件不存在: $TEST_DATA${NC}"
    echo -e "${YELLOW}请检查config.yaml中的evaluation.test_data配置${NC}"
    exit 1
fi

echo "Python环境: $(which python3)"
echo "工作目录: $SCRIPT_DIR"
echo ""

# 6. 运行评估
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}🚀 开始执行评估${NC}"
echo -e "${GREEN}============================================${NC}"

# 准备命令行参数
EVAL_ARGS=""
if [ -n "$TEST_DATA" ] && [ "$TEST_DATA" != "../Test_FILE/verl_support/data/gsm8k/test.parquet" ]; then
    EVAL_ARGS="$EVAL_ARGS --test-data=\"$TEST_DATA\""
fi

# 传递所有命令行参数给evaluation_runner.py
if [ $# -gt 0 ]; then
    EVAL_ARGS="$EVAL_ARGS $@"
fi

echo "运行命令: python3 evaluation_runner.py $EVAL_ARGS"
echo ""

# 切换到evaluation目录并运行
cd "$SCRIPT_DIR"

# 捕获Ctrl+C信号进行优雅退出
trap 'echo -e "\n${YELLOW}⏸️ 接收到中断信号，正在停止评估...${NC}"; exit 130' INT

if eval "python3 evaluation_runner.py $EVAL_ARGS"; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}🎉 评估成功完成！${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo -e "${CYAN}结果文件已保存到 ./results/ 目录${NC}"
    echo -e "${CYAN}检查详细结果：${NC}"
    echo -e "${CYAN}  ls -la ./results/${NC}"
else
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}❌ 评估执行失败${NC}"
    echo -e "${RED}============================================${NC}"
    echo -e "${YELLOW}请检查日志文件了解详细错误信息${NC}"
    exit 1
fi