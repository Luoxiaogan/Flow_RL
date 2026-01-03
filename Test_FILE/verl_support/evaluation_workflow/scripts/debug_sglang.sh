#!/bin/bash

# ============================================
# SGLang调试脚本
# ============================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}        SGLang 调试模式${NC}"
echo -e "${BLUE}========================================${NC}"

# 获取配置
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 读取模型配置
MODEL_PATH=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['model_path'])")
PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['port'])")
TP=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local']['tensor_parallel'])")
MEM_FRAC=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['model']['local'].get('mem_fraction_static', 0.85))")

echo -e "${GREEN}配置信息:${NC}"
echo "  模型路径: $MODEL_PATH"
echo "  端口: $PORT"
echo "  张量并行: $TP"
echo "  内存分配: $MEM_FRAC"
echo ""

# 检查模型路径
if [ ! -d "$MODEL_PATH" ]; then
    echo -e "${RED}错误: 模型路径不存在: $MODEL_PATH${NC}"
    exit 1
fi

# 检查GPU
echo -e "${YELLOW}GPU状态:${NC}"
nvidia-smi --query-gpu=index,name,memory.free,memory.total --format=csv
echo ""

# 检查端口
if lsof -i :$PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}警告: 端口 $PORT 已被占用${NC}"
    lsof -i :$PORT
    echo ""
    read -p "是否终止占用进程? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -9 $(lsof -t -i:$PORT)
        echo -e "${GREEN}已终止占用进程${NC}"
    fi
fi

# 构建SGLang命令
CMD="python -m sglang.launch_server \
    --model-path $MODEL_PATH \
    --port $PORT \
    --tp $TP \
    --mem-fraction-static $MEM_FRAC"

echo -e "${YELLOW}SGLang启动命令:${NC}"
echo "$CMD"
echo ""
echo -e "${GREEN}启动SGLang服务器（调试模式）...${NC}"
echo -e "${YELLOW}提示: 按 Ctrl+C 停止服务器${NC}"
echo "=========================================="
echo ""

# 执行命令
$CMD