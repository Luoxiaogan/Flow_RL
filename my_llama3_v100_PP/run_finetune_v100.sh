#!/bin/bash

# =====================================================================================
# Llama-3 8B 微调脚本 (专为 6x V100 流水线并行优化 - 最终版)
# =====================================================================================

set -e

# --- 基础环境配置 ---
source /mnt/mydisk/miniconda3/etc/profile.d/conda.sh
conda activate lg_workflow

# --- W&B (Weights & Biases) 项目配置 ---
export WANDB_PROJECT="llama3-8b-pp-sft-v100-6gpu"

# --- 核心路径配置 ---
PROJECT_DIR="/root/lg/Flow_RL_luogan/my_llama3_v100_PP"
MODEL_NAME="/mnt/mydisk/haoyu/hf_models/hub/models--meta-llama--Meta-Llama-3-8B-Instruct/snapshots/e1945c40cd546c78e41f1151f4db032b271faeaa"
DATASET_PATH="/root/lg/Flow_RL_luogan/training_data/gsm8k/jsonl1_verified_correct.jsonl"
OUTPUT_DIR="/mnt/mydisk/luogan/Llama-3-8B-PP-Expert-V100-6gpu"

# --- 分布式与硬件配置 ---
NUM_GPUS=6

# --- 显存与批量大小配置 ---
MICRO_BATCH_SIZE=1
GRAD_ACCUM_STEPS=8 

# --- DeepSpeed 配置文件路径 ---
# 通过环境变量传递这个配置，deepspeed.initialize 会自动读取
export DEEPSPEED_CONFIG="${PROJECT_DIR}/configs/deepspeed_config_z3_pp.json"

# --- DeepSpeed 原生启动命令 ---
echo "Starting training on $NUM_GPUS V100 GPUs using DeepSpeed launcher..."

# 使用 --include 指定要使用的GPU卡号
deepspeed --include="localhost:2,3,4,5,6,7" ${PROJECT_DIR}/src/train_pp.py \
    --model_name_or_path $MODEL_NAME \
    --dataset_path $DATASET_PATH \
    --output_dir $OUTPUT_DIR \
    --num_train_epochs 3 \
    --per_device_train_batch_size $MICRO_BATCH_SIZE \
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS \
    --learning_rate 2e-5 \
    --lr_scheduler_type "cosine" \
    --warmup_ratio 0.03 \
    --save_steps 100 \
    --logging_steps 1 \
    --report_to "none" \
    --max_seq_length 1024

echo "Training script finished."