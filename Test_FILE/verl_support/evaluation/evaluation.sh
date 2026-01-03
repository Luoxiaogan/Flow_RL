#!/bin/bash

# ============================================
# 模型评测脚本
# ============================================
# 该脚本用于运行模型评测流程

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 加载共享配置文件
CONFIG_FILE="${SCRIPT_DIR}/config.sh"
if [ -f "$CONFIG_FILE" ]; then
    echo "加载配置文件: $CONFIG_FILE"
    source "$CONFIG_FILE"
else
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    echo "请先创建 config.sh 文件"
    exit 1
fi

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 无颜色

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}      模型评测系统启动${NC}"
echo -e "${GREEN}========================================${NC}"

# 如果API配置不存在，创建模板
if [ "$MODE" = "api" ] && [ ! -f "$API_CONFIG_FILE" ]; then
    echo -e "${YELLOW}创建API配置文件模板: $API_CONFIG_FILE${NC}"
    cat > "$API_CONFIG_FILE" << EOF
{
    "api_url": "https://api.openai.com/v1/chat/completions",
    "api_key": "your-api-key-here",
    "api_model": "gpt-4"
}
EOF
    echo -e "${RED}请先编辑 $API_CONFIG_FILE 填入您的API凭证！${NC}"
    exit 1
fi

# ScoreFlow Reward Server URL
SCOREFLOW_URL="http://localhost:$SCOREFLOW_PORT/health"

echo -e "${YELLOW}检查 ScoreFlow Reward Server...${NC}"
if curl -s -o /dev/null -w "%{http_code}" "$SCOREFLOW_URL" | grep -q "200"; then
    echo -e "${GREEN}✓ ScoreFlow Reward Server 运行中${NC}"
else
    echo -e "${RED}✗ ScoreFlow Reward Server 未运行${NC}"
    echo -e "${YELLOW}需要启动 ScoreFlow Reward Server...${NC}"
    echo -e "${YELLOW}请在另一个终端运行:${NC}"
    echo -e "${GREEN}cd /Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/verl_support${NC}"
    echo -e "${GREEN}python scoreflow_reward_server.py${NC}"
    echo ""
    read -p "启动服务器后按回车，或输入 'skip' 跳过评分: " response
    if [ "$response" = "skip" ]; then
        SKIP_SCORING=true
        echo -e "${YELLOW}跳过评分阶段...${NC}"
    else
        # 再次检查
        if curl -s -o /dev/null -w "%{http_code}" "$SCOREFLOW_URL" | grep -q "200"; then
            echo -e "${GREEN}✓ ScoreFlow Reward Server 确认运行中${NC}"
        else
            echo -e "${RED}服务器仍未检测到。跳过评分阶段...${NC}"
            SKIP_SCORING=true
        fi
    fi
fi

# ============================================
# 构建命令
# ============================================

# 基础命令
CMD="python /Users/luogan/Code/workflow_generation/Flow_RL/Test_FILE/verl_support/evaluation/evaluate_model.py"

# 添加模式特定参数
if [ "$MODE" = "local" ]; then
    echo -e "${GREEN}使用本地模型: $MODEL_PATH${NC}"
    CMD="$CMD --model-path $MODEL_PATH"
    CMD="$CMD --port $PORT"
    CMD="$CMD --tensor-parallel $TENSOR_PARALLEL"
    
    if [ "$DATA_PARALLEL" -gt 1 ]; then
        CMD="$CMD --data-parallel $DATA_PARALLEL"
    fi
elif [ "$MODE" = "api" ]; then
    echo -e "${GREEN}使用API配置: $API_CONFIG_FILE${NC}"
    CMD="$CMD --api-config $API_CONFIG_FILE"
else
    echo -e "${RED}无效的MODE: $MODE。必须是 'local' 或 'api'${NC}"
    exit 1
fi

# 添加通用参数
CMD="$CMD --test-data $TEST_DATA"
CMD="$CMD --output-dir $OUTPUT_DIR"
CMD="$CMD --max-inference-workers $MAX_INFERENCE_WORKERS"
CMD="$CMD --max-scoring-workers $MAX_SCORING_WORKERS"
CMD="$CMD --batch-size $BATCH_SIZE"
CMD="$CMD --temperature $TEMPERATURE"
CMD="$CMD --max-tokens $MAX_TOKENS"

# 添加可选参数
if [ -n "$LIMIT" ]; then
    CMD="$CMD --limit $LIMIT"
fi

if [ "$SKIP_SCORING" = true ]; then
    CMD="$CMD --skip-scoring"
fi

# ============================================
# 执行评测
# ============================================

echo ""
echo -e "${YELLOW}配置汇总:${NC}"
echo "  模式: $MODE"
if [ "$MODE" = "local" ]; then
    echo "  模型路径: $MODEL_PATH"
    echo "  端口: $PORT"
    echo "  张量并行: $TENSOR_PARALLEL"
else
    echo "  API配置: $API_CONFIG_FILE"
fi
echo "  测试数据: $TEST_DATA"
echo "  输出目录: $OUTPUT_DIR"
echo "  最大推理并发: $MAX_INFERENCE_WORKERS"
echo "  最大评分并发: $MAX_SCORING_WORKERS"
echo "  温度: $TEMPERATURE"
echo "  最大Token: $MAX_TOKENS"
echo "  跳过评分: $SKIP_SCORING"
if [ -n "$LIMIT" ]; then
    echo "  样本限制: $LIMIT"
fi

echo ""
echo -e "${YELLOW}将执行的命令:${NC}"
echo "$CMD"
echo ""

# 确认提示
read -p "是否继续评测? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}评测已取消。${NC}"
    exit 1
fi

# 创建输出目录（如果不存在）
mkdir -p "$OUTPUT_DIR"

# 运行评测
echo -e "${GREEN}开始评测...${NC}"
echo "=========================================="

# 记录时间并执行
start_time=$(date +%s)

$CMD

exit_code=$?

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "=========================================="

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ 评测成功完成！${NC}"
    echo -e "${GREEN}耗时: $((duration / 60)) 分钟 $((duration % 60)) 秒${NC}"
    echo -e "${GREEN}结果保存在: $OUTPUT_DIR${NC}"
    
    # 查找最新的结果目录
    LATEST_RESULT=$(ls -td "$OUTPUT_DIR"/*/ 2>/dev/null | head -1)
    if [ -n "$LATEST_RESULT" ]; then
        echo ""
        echo -e "${YELLOW}最新结果位于: $LATEST_RESULT${NC}"
        echo -e "${YELLOW}查看汇总报告:${NC}"
        echo "  cat ${LATEST_RESULT}summary_report.md"
    fi
else
    echo -e "${RED}✗ 评测失败，退出码: $exit_code${NC}"
    exit $exit_code
fi