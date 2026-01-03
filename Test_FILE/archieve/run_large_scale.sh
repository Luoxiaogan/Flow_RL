#!/bin/bash

# ===== 大规模工作流生成调度脚本 =====
# 该脚本通过 master_runner.py 分批次地调用 workflow_orchestrator_v5.py
# 以处理大型数据集，并支持随机抽样。

# 导航到脚本目录
cd "$(dirname "$0")"

# === 配置区域 - 在这里修改你的参数 ===

# -- 调度器配置 --
BENCHMARK="GSM8K"
TOTAL_PROBLEMS=7473   # 数据集中的问题总数
MIN_SAMPLE_SIZE=2     # 每个工作流最少使用的问题样本数
MAX_SAMPLE_SIZE=4     # 每个工作流最多使用的问题样本数
BATCH_SIZE=15         # 每批次并行处理的工作流数量

# API池配置 (JSON格式)
API_POOL='[
    {
        "provider": "openai",
        "model": "qwen-turbo",
        "api_key": "sk-70e93be8280d4cd08526438db5441bae",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
]'

# 执行LLM配置 (JSON格式)
EXEC_LLM='{
        "provider": "openai",
        "model": "qwen-turbo",
        "api_key": "sk-70e93be8280d4cd08526438db5441bae",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}'

# -- 路径配置 --
WORKSPACE_PATH="./workspace_large_scale"
DATASET_BASE_PATH="./ScoreFlow/benchmark/datasets"
GSM8K_DATASET_PATH="/home/lg/workflow_tooluse/Flow_RL_luogan/Processed_dataset/gsm8k/train.jsonl" # 可选，如果为空则使用默认

# -- 输出配置 --
TRAINING_DATA_OUTPUT="./training_data_gsm8k.jsonl" # 训练数据总输出文件
SUMMARY_CSV_OUTPUT="${WORKSPACE_PATH}/gsm8k.csv" # 结果CSV总输出文件

# -- 系统配置 --
LOG_LEVEL="INFO"
MAX_CONCURRENT_TASKS=10
WORKFLOW_TIMEOUT=120

# === 脚本执行 ===

# 启动前清空旧的输出文件，以确保从头开始
# echo "正在清空旧的输出文件..."
# rm -f "$TRAINING_DATA_OUTPUT"
# rm -f "$SUMMARY_CSV_OUTPUT"
# echo "旧文件已清空。"

echo
echo "=== 大规模工作流调度器启动 ==="
echo "执行时间: $(date)"
echo "工作目录: $(pwd)"
echo

python3 master_runner.py \
    --benchmark "$BENCHMARK" \
    --total-problems $TOTAL_PROBLEMS \
    --min-sample-size $MIN_SAMPLE_SIZE \
    --max-sample-size $MAX_SAMPLE_SIZE \
    --batch-size $BATCH_SIZE \
    --api-pool "$API_POOL" \
    --exec-llm "$EXEC_LLM" \
    --workspace-path "$WORKSPACE_PATH" \
    --dataset-base-path "$DATASET_BASE_PATH" \
    --gsm8k-dataset-path "$GSM8K_DATASET_PATH" \
    --training-data-output "$TRAINING_DATA_OUTPUT" \
    --log-level "$LOG_LEVEL" \
    --max-concurrent-tasks $MAX_CONCURRENT_TASKS \
    --workflow-timeout $WORKFLOW_TIMEOUT

echo
echo "=== 执行完成 ==="
echo "完成时间: $(date)"