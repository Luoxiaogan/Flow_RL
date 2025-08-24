#!/bin/bash
# 最简版本 - train_qwen3_minimal.sh

# 设置必要的环境变量
export USE_SGLANG=1
export NCCL_DEBUG=INFO
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# 配置路径
CONFIG_DIR="/nas/ganluo/Flow_RL/New_evaluation_and_RL/RL_part/configs"
DATASET_PATH="/nas/ganluo/Flow_RL/New_evaluation_and_RL/RL_part/custom_datasets/qwen3_thinking_dataset.py"

# 直接执行
python /nas/ganluo/Flow_RL/verl/verl/trainer/main_ppo.py \
    --config-path=${CONFIG_DIR} \
    --config-name=qwen3_thinking_config \
    data.custom_cls.path=${DATASET_PATH} \
    data.custom_cls.name=Qwen3ThinkingDataset \
    "$@"  # 传递任何额外的命令行参数