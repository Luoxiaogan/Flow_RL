#!/bin/bash
# 设置必要的环境变量
export USE_SGLANG=1
export NCCL_DEBUG=INFO
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# 配置路径
CONFIG_DIR="/nas/ganluo/Flow_RL/New_evaluation_and_RL/RL_part/configs"
VERL_CONFIG_DIR="/nas/ganluo/Flow_RL/verl/verl/trainer/config"
DATASET_PATH="/nas/ganluo/Flow_RL/New_evaluation_and_RL/RL_part/custom_datasets/qwen3_thinking_dataset.py"

# 创建临时配置目录
TEMP_CONFIG_DIR="/tmp/qwen3_training_configs_$$"
mkdir -p ${TEMP_CONFIG_DIR}

# 复制VERL的配置文件到临时目录
cp -r ${VERL_CONFIG_DIR}/* ${TEMP_CONFIG_DIR}/

# 复制您的配置文件到临时目录
cp ${CONFIG_DIR}/qwen3_simplified.yaml ${TEMP_CONFIG_DIR}/

# 执行训练
python /nas/ganluo/Flow_RL/verl/verl/trainer/main_ppo.py \
    --config-path=${TEMP_CONFIG_DIR} \
    --config-name=qwen3_simplified \
    data.custom_cls.path=${DATASET_PATH} \
    data.custom_cls.name=Qwen3ThinkingDataset \
    "$@"

# 清理临时目录（可选）
# rm -rf ${TEMP_CONFIG_DIR}