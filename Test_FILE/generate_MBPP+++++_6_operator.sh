#!/bin/bash
# 清除代理设置
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY来排除本地服务
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

cd "$(dirname "$0")" || exit

# API_POOL='{
#     "provider": "openai",
#     "model": "qwen-turbo", 
#     "api_key": "dummy",
#     "base_url": "http://localhost:5059"
# }'

API_POOL='[
    {
        "provider": "openai",
        "model": "qwen3-max-preview",
        "api_key": "dummy",
        "base_url": "http://localhost:5059",
        "enable_thinking": true,
        "thinking_budget": 10000,
        "max_tokens": 10000
    }
]'

# 执行LLM，用于【工作流内部的算子】，通常只配置一个高效、可靠的模型。
EXEC_LLM='{
    "provider": "openai",
    "model": "qwen-turbo", 
    "api_key": "dummy",
    "base_url": "http://localhost:5059",
    "max_tokens": 10000
}'

# --- 路径配置 ---
# 总的工作空间，所有生成物和结果都将保存在这里
WORKSPACE_PATH="./workspace_MBPP+++++_6_operator_QWEN3_new"

# --- 系统配置 ---
LOG_LEVEL="INFO"
# 修改变量名以匹配Python参数，提高一致性
MAX_CONCURRENT_TASKS=30  # 生成器内部的最大并发任务数
WORKFLOW_TIMEOUT=600     # 单个工作流的执行超时时间（秒）

# ============================ 任务配置 =======================================
# 说明: 一次只取消注释一个任务块来运行。

# ------------------------- 任务 1: HotPotQA (多跳问答) -------------------------
#
BENCHMARK="mbppplus"
TOTAL_PROBLEMS=374  #374     # Testing with just 1 problem
MIN_SAMPLE_SIZE=2     # 每个工作流最少使用的问题样本数
MAX_SAMPLE_SIZE=2     # 每个工作流最多使用的问题样本数
MAX_CONCURRENT_EXECUTIONS=30  # 并行执行工作流的最大并发数
PARALLELISM=1  # 每个数据组合生成的工作流并行度（默认2个不同版本）
MAX_CONCURRENT_GROUPS=30  # 生成阶段最大并发组数（组间并行，组内串行）
BATCH_SIZE=$MAX_CONCURRENT_GROUPS          # 每批次生成的工作流数量 = 最大并发组数
# 选择要使用的operators（用逗号分隔，可选：generate,revise,summarize,ensemble,programmer,decompose）
OPERATORS="generate,revise,summarize,ensemble,programmer,decompose"
# 数据集文件的路径 (推荐使用相对路径)
# 假设数据存放在项目根目录下的 'data' 文件夹中
DATASET_PATH="../Processed_dataset/mbpp/train.jsonl"
# 训练数据输出文件
TRAINING_DATA_OUTPUT="${WORKSPACE_PATH}/training_data_${BENCHMARK}.jsonl"


# # ------------------------- 任务 2: MBPP (代码生成) --------------------------
# #
# BENCHMARK="mbpp"
# TOTAL_PROBLEMS=374    # MBPP 训练集中的问题总数
# MIN_SAMPLE_SIZE=2     # 每个工作流最少使用的问题样本数
# MAX_SAMPLE_SIZE=3     # 每个工作流最多使用的问题样本数
# BATCH_SIZE=15         # 每批次生成的工作流数量
# # 数据集文件的路径 (推荐使用相对路径)
# DATASET_PATH="./data/mbpp/train.jsonl"
# # 训练数据输出文件
# TRAINING_DATA_OUTPUT="${WORKSPACE_PATH}/training_data_${BENCHMARK}.jsonl"


# ============================ 脚本执行 =======================================

# 检查是否选择了有效的任务
if [ -z "$BENCHMARK" ] || [ -z "$DATASET_PATH" ]; then
    echo "错误: 请取消注释一个任务配置块并设置好 BENCHMARK 和 DATASET_PATH。"
    exit 1
fi

echo "=================================================="
echo "  启动工作流系统 (V3)"
echo "=================================================="
echo "  任务时间: $(date)"
echo "  工作目录: $(pwd)"
echo "  Benchmark: $BENCHMARK"
echo "  数据集路径: $DATASET_PATH"
echo "  工作空间: $WORKSPACE_PATH"
echo "=================================================="
echo

# 调用 master_runner.py，传递所有配置参数
# 注意: 我们将多行JSON字符串用引号括起来以确保正确传递
python3 master_runner.py \
    --benchmark "$BENCHMARK" \
    --total-problems "$TOTAL_PROBLEMS" \
    --min-sample-size "$MIN_SAMPLE_SIZE" \
    --max-sample-size "$MAX_SAMPLE_SIZE" \
    --batch-size "$BATCH_SIZE" \
    --api-pool "$API_POOL" \
    --exec-llm "$EXEC_LLM" \
    --workspace-path "$WORKSPACE_PATH" \
    --dataset-path "$DATASET_PATH" \
    --training-data-output "$TRAINING_DATA_OUTPUT" \
    --log-level "$LOG_LEVEL" \
    --max-concurrent-tasks "$MAX_CONCURRENT_TASKS" \
    --workflow-timeout "$WORKFLOW_TIMEOUT" \
    --max-concurrent-executions "$MAX_CONCURRENT_EXECUTIONS" \
    --parallelism "$PARALLELISM" \
    --max-concurrent-groups "$MAX_CONCURRENT_GROUPS" \
    --operators "$OPERATORS"

# 检查上一个命令的退出状态
if [ $? -eq 0 ]; then
    echo
    echo "=================================================="
    echo "  所有任务处理完毕"
    echo "  完成时间: $(date)"
    echo "=================================================="
else
    echo
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "  脚本执行中遇到错误，请检查以上日志"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
fi