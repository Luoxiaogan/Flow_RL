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

# --- 分布式训练及硬件配置 (V100 适配) ---
NUM_GPUS=6 
export CUDA_VISIBLE_DEVICES=2,3,4,5,6,7
#
PER_DEVICE_BATCH_SIZE=1
GRAD_ACCUM_STEPS=6 
# --- OOM (Out of Memory) 备忘录 ---
# 如果在训练开始时遇到显存不足错误:
# 1. 首选策略: 降低 PER_DEVICE_BATCH_SIZE 到 1, 并将 GRAD_ACCUM_STEPS 加倍到 8。
# 2. 如果问题依旧: 降低 MAX_SEQ_LENGTH, 例如从 4096 降低到 2048。

# --- DeepSpeed 与 Accelerate 配置文件路径 ---
ACCELERATE_CONFIG="${PROJECT_DIR}/accelerate_config_v100.yaml"
DEEPSPEED_CONFIG="${PROJECT_DIR}/configs/deepspeed_config_z3_v100.json"

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