#!/bin/bash

# 创建新的tmux会话
# tmux new-session -d -s llama_h100_training
# tmux kill-session -t llama_h100_training

# 在tmux会话中运行训练
# tmux send-keys -t llama_h100_training "cd /nas/ganluo/Flow_RL/my_llama3_h100" Enter
# tmux send-keys -t llama_h100_training "conda activate qzh" Enter
# tmux send-keys -t llama_h100_training "bash /nas/ganluo/Flow_RL/my_llama3_h100/run_finetune.sh" Enter

# 查看训练状态
# tmux attach -t llama_h100_training

# 显式初始化conda环境 - 使用正确的miniconda路径
# source /opt/miniconda3/etc/profile.d/conda.sh
# conda activate qzh

# 忽略SIGHUP信号
trap '' HUP
# 确保脚本在任何命令失败时退出
set -e

# --- 内存优化环境变量 ---
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=0

# --- H100/L20Z GPU配置参数 ---
export WANDB_PROJECT="llama3-8b-workflow-h100-sft"
MODEL_NAME="/nas/models/Meta-Llama-3-8B-Instruct"
DATASET_PATH="/nas/ganluo/Flow_RL/training_data/gsm8k/jsonl1_verified_correct.jsonl"
OUTPUT_DIR="/nas/ganluo/sft_output/Llama-3-8B-Instruct-Workflow-Expert-H100"
DEEPSPEED_CONFIG="/nas/ganluo/Flow_RL/my_llama3_h100/configs/deepspeed_config_z3.json"

# H100服务器有8张L20Z GPU，每张80GB显存
NUM_GPUS=8
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7  # 使用所有8张GPU

# 全局批大小 = NUM_GPUS * GRAD_ACCUM_STEPS * PER_DEVICE_BATCH_SIZE
# 8张GPU配置 - 目标全局批次大小128: 8 * 4 * 4 = 128
# 由于有更多GPU和显存，可以适当增加per_device_batch_size
PER_DEVICE_BATCH_SIZE=4
GRAD_ACCUM_STEPS=4

# --- Accelerate 启动命令 ---
# 使用python -m确保使用当前conda环境中的accelerate
python -m accelerate.commands.launch \
    --config_file /nas/ganluo/Flow_RL/my_llama3_h100/accelerate_config.yaml \
    /nas/ganluo/Flow_RL/my_llama3_h100/src/train.py \
    --model_name_or_path $MODEL_NAME \
    --dataset_path $DATASET_PATH \
    --output_dir $OUTPUT_DIR \
    --num_train_epochs 3 \
    --per_device_train_batch_size $PER_DEVICE_BATCH_SIZE \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS \
    --learning_rate 2e-5 \
    --lr_scheduler_type "cosine" \
    --warmup_ratio 0.03 \
    --logging_steps 1 \
    --save_strategy "no" \
    --save_steps 50 \
    --save_total_limit 10 \
    --bf16 True \
    --tf32 True \
    --gradient_checkpointing True \
    --report_to "wandb" \
    --deepspeed $DEEPSPEED_CONFIG \
    --max_seq_length 4096 \
    --use_flash_attention_2 True

# 后台运行命令
# nohup bash run_finetune.sh > training_h100.log 2>&1 &