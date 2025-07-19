#!/bin/bash

# =====================================================================================
# Llama-3 8B 全量微调脚本 (专为 4x V100 GPU 优化)
#
# 该脚本配置了在4张NVIDIA V100 GPU上使用DeepSpeed ZeRO Stage 3和FP16进行
# 高效全量微调的参数。
# =====================================================================================

# 确保脚本在任何命令失败时退出
set -e

# --- 基础环境配置 ---
# 显式初始化conda环境，请根据您的服务器环境修改路径
source /mnt/mydisk/miniconda3/etc/profile.d/conda.sh
conda activate lg_workflow

# --- W&B (Weights & Biases) 项目配置 ---
export WANDB_PROJECT="llama3-8b-workflow-full-sft-v100"

# --- 核心路径配置 (重要: 请根据您的服务器环境修改以下路径) ---
# 建议使用绝对路径以避免潜在的路径问题
PROJECT_DIR="/root/lg/Flow_RL_luogan/my_llama3_v100" # <--- 修改点: 请替换为您的项目根目录
MODEL_NAME="/mnt/mydisk/haoyu/hf_models/hub/models--meta-llama--Meta-Llama-3-8B-Instruct/snapshots/e1945c40cd546c78e41f1151f4db032b271faeaa"
DATASET_PATH="/root/lg/Flow_RL_luogan/training_data/gsm8k/jsonl1_verified_correct.jsonl" # <--- 修改点: 请替换为您的数据集路径
OUTPUT_DIR="/mnt/mydisk/luogan/Llama-3-8B-Instruct-Workflow-Expert-Full-V100"

# --- 显存与批量大小配置 (PP修正) ---
# 使用流水线并行后, per_device_batch_size 概念变为 micro_batch_size
PER_DEVICE_BATCH_SIZE=1 
GRAD_ACCUM_STEPS=6      # 保持不变，全局批大小仍然是 1 * 6 * 6 / 2(DP) = 18. (需要重新计算)

# (重新计算全局批大小)
# 全局批大小 = 数据并行度 * 梯度累积步数 * 单设备微批量
# 数据并行度 = 总GPU / 流水线阶段数 = 6 / 3 = 2
# 为了维持全局批大小接近36, 36 = 2 * GRAD_ACCUM_STEPS * 1 => GRAD_ACCUM_STEPS = 18
# 这是一个较大的累积步数，但为了对比，我们先保持原来的 GRAD_ACCUM_STEPS=6
# Global batch size = 2 * 6 * 1 = 12
GRAD_ACCUM_STEPS=6

# --- DeepSpeed 与 Accelerate 配置文件路径 ---
ACCELERATE_CONFIG="${PROJECT_DIR}/accelerate_config_v100.yaml"
DEEPSPEED_CONFIG="${PROJECT_DIR}/configs/deepspeed_config_z3_pp.json"

# --- Accelerate 启动命令 ---
# 使用 `python -m accelerate.commands.launch` 以确保使用当前conda环境的包
echo "Starting training on $NUM_GPUS V100 GPUs..."

python -m accelerate.commands.launch --config_file $ACCELERATE_CONFIG ${PROJECT_DIR}/src/train.py \
    --model_name_or_path $MODEL_NAME \
    --dataset_path $DATASET_PATH \
    --output_dir $OUTPUT_DIR \
    --num_train_epochs 3 \
    --per_device_train_batch_size $PER_DEVICE_BATCH_SIZE \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS \
    --learning_rate 2e-5 \
    --lr_scheduler_type "cosine" \
    --warmup_ratio 0.03 \
    --logging_steps 1 \
    --save_steps 50 \
    --save_total_limit 10 \
    --gradient_checkpointing True \
    --report_to "wandb" \
    --max_seq_length 1024 \
    --deepspeed $DEEPSPEED_CONFIG \
    --fp16 True \
    --use_flash_attention_2 False

# --- V100 适配关键参数修改说明 ---
# 1. --fp16 True:                   <-- 修改点: 从 --bf16 改为 --fp16, 适配V100的FP16 Tensor Core。
# 2. --tf32 True:                   <-- 修改点: 已移除, V100不支持TF32。
# 3. --use_flash_attention_2 False: <-- 修改点: 明确禁用Flash Attention 2, V100不支持。


echo "Training script finished."

# --- 后台运行指令示例 ---
# nohup bash /path/to/your/project/my_llama3_v100/run_finetune_v100.sh > output.log 2>&1 &