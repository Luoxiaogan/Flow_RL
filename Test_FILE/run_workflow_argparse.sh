#!/bin/bash

# ===== workflow_orchestrator_v5.py 单文件执行脚本 =====
# 硬编码配置，直接通过命令行参数传递给Python脚本

# 导航到脚本目录
cd "$(dirname "$0")"

# === 配置区域 - 在这里修改你的参数 ===

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

# 任务配置
GENERATION_TASKS="GSM8K:0,5,10-11"

# 路径配置
WORKSPACE_PATH="./workspace_v5"
DATASET_BASE_PATH="./ScoreFlow/benchmark/datasets"
GSM8K_DATASET_PATH="./ScoreFlow/benchmark/datasets/gsm8k.jsonl"

# 系统配置
LOG_LEVEL="INFO"
MAX_CONCURRENT_TASKS=10
WORKFLOW_TIMEOUT=120

# === 验证环境变量 ===
# if [ -z "$DASHSCOPE_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
#     echo "错误: 没有设置任何API密钥环境变量。"
#     echo "请设置以下环境变量之一:"
#     echo "  export DASHSCOPE_API_KEY='your-dashscope-key'"
#     echo "  export OPENAI_API_KEY='your-openai-key'"
#     exit 1
# fi

echo "=== 工作流编排器 V5 启动 ==="
echo "执行时间: $(date)"
echo "工作目录: $(pwd)"
echo

# === 执行Python脚本 ===
python3 workflow_orchestrator_v5.py \
    --api-pool "$API_POOL" \
    --exec-llm "$EXEC_LLM" \
    --generation-tasks "$GENERATION_TASKS" \
    --workspace-path "$WORKSPACE_PATH" \
    --dataset-base-path "$DATASET_BASE_PATH" \
    --gsm8k-dataset-path "$GSM8K_DATASET_PATH" \
    --log-level "$LOG_LEVEL" \
    --max-concurrent-tasks $MAX_CONCURRENT_TASKS \
    --workflow-timeout $WORKFLOW_TIMEOUT

echo
echo "=== 执行完成 ==="
echo "完成时间: $(date)"
