#!/bin/bash
# ============================================
# 共享配置文件 - 所有脚本共用的参数
# ============================================
# 修改这里的值会影响所有引用此文件的脚本

# 模式选择: "local" 或 "api"
MODE="local"

# ---- 本地模型配置 (当 MODE="local" 时) ----
MODEL_PATH="/nas/ganluo/sft_output/Qwen2.5-7B-workflow-sft_new/checkpoint-200"  # 本地checkpoint路径
PORT=30000                                        # SGLang服务器端口
TENSOR_PARALLEL=1                                 # 张量并行GPU数量
DATA_PARALLEL=1                                   # 数据并行模型副本数

# ---- API模型配置 (当 MODE="api" 时) ----
API_CONFIG_FILE="api_config.json"                # API配置文件路径

# ---- 通用配置 ----
TEST_DATA="../data/test_new/test.parquet"        # 测试数据路径
OUTPUT_DIR="./results"                           # 结果输出目录
MAX_INFERENCE_WORKERS=10                         # 最大并发推理请求数
MAX_SCORING_WORKERS=5                            # 最大并发评分请求数
BATCH_SIZE=50                                    # 批处理大小
TEMPERATURE=0.7                                  # 生成温度
MAX_TOKENS=8192                                  # 最大生成token数
LIMIT=""                                         # 样本数限制（空为全部）
SKIP_SCORING=false                               # 是否跳过评分

# ---- ScoreFlow Server配置 ----
SCOREFLOW_PORT=8899                              # ScoreFlow服务器端口

# ---- 调试配置 ----
DEBUG_MODE=false                                 # 是否启用调试模式
TIMEOUT=120                                      # SGLang启动超时（秒）

# 导出所有变量，使子进程可以访问
export MODE MODEL_PATH PORT TENSOR_PARALLEL DATA_PARALLEL
export API_CONFIG_FILE TEST_DATA OUTPUT_DIR
export MAX_INFERENCE_WORKERS MAX_SCORING_WORKERS BATCH_SIZE
export TEMPERATURE MAX_TOKENS LIMIT SKIP_SCORING
export SCOREFLOW_PORT DEBUG_MODE TIMEOUT