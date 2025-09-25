#!/bin/bash
# IMO Workflow测试脚本

# ========================================
#           配置参数
# ========================================

# 数据索引
INDEX=0
PROBLEM_INDEX=0

# 文件路径
IMO_PROBLEM="/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/imo_data/imo_problems.jsonl"
IMO_RESPONSE="/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/imo_data_0923/imo_test_with_responses_rollout=1.jsonl"
LOG_DIR="/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/imo_execution_log"

# LLM配置（可根据需要切换）
# 配置1: 阿里云通义千问
LLM_MODEL="qwen-turbo"
API_KEY="sk-0040331ac2d442b6b813304a807d88cd"
BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# 配置2: 代理服务器（注释掉上面的，取消注释下面的来使用）
# LLM_MODEL="qwen-turbo"
# API_KEY="8cf060f9e1f444858609730176542253"
# BASE_URL="http://39.96.211.155:8000/proxy/api/openai/v1"

# 执行参数
TIMEOUT=360
ENABLE_STREAM=""  # 添加 "--stream" 来启用流式输出

# ========================================
#           函数定义
# ========================================

# 打印帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项："
    echo "  -i, --index INDEX           设置workflow索引 (默认: $INDEX)"
    echo "  -p, --problem PROBLEM_IDX   设置问题索引 (默认: $PROBLEM_INDEX)"
    echo "  -s, --stream                启用流式输出"
    echo "  -t, --timeout SECONDS       设置超时时间 (默认: $TIMEOUT)"
    echo "  -h, --help                  显示此帮助信息"
    echo ""
    echo "示例："
    echo "  $0                          # 使用默认参数运行"
    echo "  $0 -i 1 -p 2               # 运行第1个workflow和第2个问题"
    echo "  $0 -s                      # 启用流式输出"
    echo "  $0 -i 0 -p 0 -s -t 600    # 完整示例"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--index)
            INDEX="$2"
            shift 2
            ;;
        -p|--problem)
            PROBLEM_INDEX="$2"
            shift 2
            ;;
        -s|--stream)
            ENABLE_STREAM="--stream"
            shift
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# ========================================
#           主执行逻辑
# ========================================

# 创建日志目录
mkdir -p "$LOG_DIR"

# 生成日志文件名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/workflow_idx=${INDEX}_problem_idx=${PROBLEM_INDEX}_${TIMESTAMP}.log"

# 显示执行信息
echo "=========================================="
echo "        IMO Workflow 测试脚本"
echo "=========================================="
echo "📋 配置信息:"
echo "  - Workflow索引: $INDEX"
echo "  - 问题索引: $PROBLEM_INDEX"
echo "  - 超时时间: ${TIMEOUT}秒"
echo "  - 流式输出: $([ -n "$ENABLE_STREAM" ] && echo "启用" || echo "禁用")"
echo "  - LLM模型: $LLM_MODEL"
echo "  - API地址: $BASE_URL"
echo "  - 日志文件: $LOG_FILE"
echo "=========================================="
echo ""

# 激活conda环境（如果需要）
if command -v conda &> /dev/null; then
    echo "🔄 激活conda环境: workflow"
    source /opt/anaconda3/etc/profile.d/conda.sh
    conda activate workflow
fi

# 执行Python脚本，使用tee同时输出到终端和日志
echo "🚀 开始执行..."
echo ""

python /Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/test_workflow_IMO.py \
    --index "$INDEX" \
    --problem-index "$PROBLEM_INDEX" \
    --imo-problem "$IMO_PROBLEM" \
    --imo-response "$IMO_RESPONSE" \
    --llm-model "$LLM_MODEL" \
    --api-key "$API_KEY" \
    --base-url "$BASE_URL" \
    --timeout "$TIMEOUT" \
    $ENABLE_STREAM \
    2>&1 | tee "$LOG_FILE"

# 获取执行结果
EXIT_CODE=${PIPESTATUS[0]}

# 显示结果
echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 执行成功"
else
    echo "❌ 执行失败 (退出码: $EXIT_CODE)"
fi
echo "📁 日志已保存到: $LOG_FILE"
echo "=========================================="

exit $EXIT_CODE