#!/bin/bash

# ==============================================================================
#           大规模工作流生成与执行系统 - 调度脚本 (V3 - 修复后版本)
# ==============================================================================
#
# 该脚本通过 master_runner.py 统一调度工作流的生成与执行。
# 它配置并调用 master_runner.py，后者再依次调用:
# 1. workflow_generator.py: 批量生成工作流代码 (.py) 和元数据 (.meta.json)。
# 2. workflow_executor.py: 逐个执行和验证已生成的工作流。
#
# --- 使用方法 ---
# 1. (首次) 设置环境变量: 为了安全，API密钥应通过环境变量提供。
#    在终端运行: export YOUR_API_KEY="sk-xxxxxxxx"
# 2. 修改配置: 在下面的 "通用配置" 和 "任务配置" 部分设置参数。
# 3. 选择任务: 确保您只想运行的任务配置块是未被注释的。
# 4. 运行脚本: bash run_workflow_system.sh
#
# ==============================================================================

# 导航到脚本所在的目录，以确保所有相对路径都能正确解析
cd "$(dirname "$0")" || exit

# ============================ 安全配置 (重要!) ================================
# 请确保您已经设置了包含 API 密钥的环境变量。
# 例如: export YOUR_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
# if [ -z "$YOUR_API_KEY" ]; then
#     echo "错误: 环境变量 YOUR_API_KEY 未设置。"
#     echo "请运行 'export YOUR_API_KEY=\"你的密钥\"' 后再试。"
#     exit 1
# fi

# ============================ 通用配置 =======================================
# 这些参数在不同任务间通常是共享的

# --- API 与模型配置 (JSON格式) ---
# API池，用于【生成阶段】，可以配置多个备用模型。
# 注意: 我们使用 "$YOUR_API_KEY" 从环境变量中读取密钥。
# API_POOL='[
#     {
#     "provider": "openai",
#     "model": "qwen-turbo", 
#     "api_key": "956c41bd0f31beaf68b871d4987af4bb",
#     "base_url": "https://idealab.alibaba-inc.com/api/openai/v1"
# }
# ]'

# # 执行LLM，用于【工作流内部的算子】，通常只配置一个高效、可靠的模型。
# EXEC_LLM='{
#     "provider": "openai",
#     "model": "qwen-turbo", 
#     "api_key": "956c41bd0f31beaf68b871d4987af4bb",
#     "base_url": "https://idealab.alibaba-inc.com/api/openai/v1"
# }'

# ALIBABA代理

# ]'
# EXEC_LLM='{
#     "provider": "openai",
#     "model": "qwen-turbo", 
#     "api_key": "956c41bd0f31beaf68b871d4987af4bb",
#     "base_url": "http://localhost:5001"
# }'

# API_POOL='[
#     {
#         "provider": "openai",
#         "model": "qwen-max-latest",
#         "api_key": "dummy",
#         "base_url": "http://localhost:5059",
#         "stream": false,
#         "stream_options": {"include_usage": true},
#         "enable_thinking": true,
#         "thinking_budget": 5000
#     }
# ]'

# API_POOL='[
#     {
#         "provider": "openai",
#         "model": "qwen-max-latest",
#         "api_key": "956c41bd0f31beaf68b871d4987af4bb",
#         "base_url": "https://idealab.alibaba-inc.com/api/openai/v1",
#         "stream": false,
#         "stream_options": {"include_usage": true},
#         "enable_thinking": true,
#         "thinking_budget": 2000
#     }
# ]'

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
        "thinking_budget": 5000
    }
]'

# 执行LLM，用于【工作流内部的算子】，通常只配置一个高效、可靠的模型。
EXEC_LLM='{
    "provider": "openai",
    "model": "qwen-turbo", 
    "api_key": "dummy",
    "base_url": "http://localhost:5059"
}'

# --- 路径配置 ---
# 总的工作空间，所有生成物和结果都将保存在这里
WORKSPACE_PATH="./workspace_HOTPOTQA_4_operator"

# --- 系统配置 ---
LOG_LEVEL="INFO"
# 修改变量名以匹配Python参数，提高一致性
MAX_CONCURRENT_TASKS=30  # 生成器内部的最大并发任务数
WORKFLOW_TIMEOUT=360     # 单个工作流的执行超时时间（秒）

# ============================ 任务配置 =======================================
# 说明: 一次只取消注释一个任务块来运行。

# ------------------------- 任务 1: HotPotQA (多跳问答) -------------------------
#
BENCHMARK="hotpotqa"
TOTAL_PROBLEMS=500      # Testing with just 1 problem
MIN_SAMPLE_SIZE=1     # 每个工作流最少使用的问题样本数
MAX_SAMPLE_SIZE=2     # 每个工作流最多使用的问题样本数
MAX_CONCURRENT_EXECUTIONS=30  # 并行执行工作流的最大并发数
PARALLELISM=1  # 每个数据组合生成的工作流并行度（默认2个不同版本）
MAX_CONCURRENT_GROUPS=30  # 生成阶段最大并发组数（组间并行，组内串行）
BATCH_SIZE=$MAX_CONCURRENT_GROUPS          # 每批次生成的工作流数量 = 最大并发组数
# 选择要使用的operators（用逗号分隔，可选：generate,revise,summarize,ensemble,programmer,decompose）
OPERATORS="generate,revise,summarize,ensemble,programmer,decompose"
# 数据集文件的路径 (推荐使用相对路径)
# 假设数据存放在项目根目录下的 'data' 文件夹中
DATASET_PATH="../Processed_dataset/hotpotqa/random_400.jsonl"
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