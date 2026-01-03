#!/bin/bash

# # 创建新的tmux会话
# tmux new-session -d -s llama_training
# tmux kill-session -t llama_training

# # 在tmux会话中运行训练
# tmux send-keys -t llama_training "cd /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune" Enter
# tmux send-keys -t llama_training "conda activate qzh" Enter
# tmux send-keys -t llama_training "bash /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/run_finetune.sh" Enter

# # 查看训练状态
# tmux attach -t llama_training

# 显式初始化conda环境 - 使用正确的miniconda路径
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate qzh

# 忽略SIGHUP信号
trap '' HUP
# 确保脚本在任何命令失败时退出
set -e

# --- 内存优化环境变量 ---
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=0

# --- 可配置参数 ---
export WANDB_PROJECT="llama3-8b-workflow-full-sft"
MODEL_NAME="/data/pretrained_models/Meta-Llama-3-8B-Instruct"
DATASET_PATH="/home/lg/workflow_tooluse/Flow_RL_luogan/training_data/gsm8k/jsonl1_verified_correct.jsonl"
OUTPUT_DIR="/data/datasets/lg/Llama-3-8B-Instruct-Workflow-Expert-Full"
DEEPSPEED_CONFIG="/home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/configs/deepspeed_config_z3.json"

NUM_GPUS=2 # 设置为1个GPU
export CUDA_VISIBLE_DEVICES=0,1 # 使用GPU 0和1
# export CUDA_VISIBLE_DEVICES=0 # 只使用GPU 0
# 全局批大小 = NUM_GPUS * GRAD_ACCUM_STEPS * PER_DEVICE_BATCH_SIZE
# 假设我们想要一个16的全局批大小
# 双GPU配置 - 全局批次大小 = NUM_GPUS * GRAD_ACCUM_STEPS * PER_DEVICE_BATCH_SIZE
# 目标全局批次大小32: 2 * 8 * 2 = 32
PER_DEVICE_BATCH_SIZE=2
GRAD_ACCUM_STEPS=8 

# (可选) 张量并行配置
# 对于8B模型在2张A800上，TP不是必须的，但可以开启以观察效果
# 开启TP需要修改模型加载方式，通常在更复杂的框架如Megatron-LM中处理
# 在transformers+accelerate中，deepspeed会自动处理数据并行(DP)，这是最直接的方式
# 如果要强行开启TP，deepspeed配置需要修改，且对模型结构有要求。
# 这里我们专注于最高效的数据并行(ZeRO-3)方案。

# --- Accelerate 启动命令 ---

# 使用python -m确保使用当前conda环境中的accelerate
python -m accelerate.commands.launch --config_file /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/accelerate_config.yaml /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/src/train.py \
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
    --bf16 True \
    --tf32 True \
    --gradient_checkpointing True \
    --report_to "wandb" \
    --deepspeed $DEEPSPEED_CONFIG \
    --max_seq_length 4096 \
    --use_flash_attention_2 True


# nohup bash /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/run_finetune.sh > output.log 2>&1 &#!/bin/bash

# # 创建新的tmux会话
# tmux new-session -d -s llama_training
# tmux kill-session -t llama_training

# # 在tmux会话中运行训练
# tmux send-keys -t llama_training "cd /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune" Enter
# tmux send-keys -t llama_training "conda activate qzh" Enter
# tmux send-keys -t llama_training "bash /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/run_finetune.sh" Enter

# # 查看训练状态
# tmux attach -t llama_training

# 显式初始化conda环境 - 使用正确的miniconda路径
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate qzh

# 忽略SIGHUP信号
trap '' HUP
# 确保脚本在任何命令失败时退出
set -e

# --- 可配置参数 ---
export WANDB_PROJECT="llama3-8b-workflow-full-sft"
MODEL_NAME="/data/pretrained_models/Meta-Llama-3-8B-Instruct"
DATASET_PATH="/home/lg/workflow_tooluse/Flow_RL_luogan/training_data/gsm8k/jsonl1_verified_correct.jsonl"
OUTPUT_DIR="/data/datasets/lg/Llama-3-8B-Instruct-Workflow-Expert-Full"
DEEPSPEED_CONFIG="/home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/configs/deepspeed_config_z3.json"

NUM_GPUS=1 # 这里设置为1，实际使用时可以根据GPU数量调整
export CUDA_VISIBLE_DEVICES=1 # 确保只使用指定的GPU
# 全局批大小 = NUM_GPUS * GRAD_ACCUM_STEPS * PER_DEVICE_BATCH_SIZE
# 假设我们想要一个32的全局批大小
PER_DEVICE_BATCH_SIZE=2
GRAD_ACCUM_STEPS=8 # 32 / 2 / 2 = 8

# (可选) 张量并行配置
# 对于8B模型在2张A800上，TP不是必须的，但可以开启以观察效果
# 开启TP需要修改模型加载方式，通常在更复杂的框架如Megatron-LM中处理
# 在transformers+accelerate中，deepspeed会自动处理数据并行(DP)，这是最直接的方式
# 如果要强行开启TP，deepspeed配置需要修改，且对模型结构有要求。
# 这里我们专注于最高效的数据并行(ZeRO-3)方案。

# --- Accelerate 启动命令 ---

# 使用python -m确保使用当前conda环境中的accelerate
python -m accelerate.commands.launch --config_file /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/accelerate_config.yaml /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/src/train.py \
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
    --bf16 True \
    --tf32 True \
    --gradient_checkpointing True \
    --report_to "wandb" \
    --deepspeed $DEEPSPEED_CONFIG \
    --max_seq_length 4096 \
    --use_flash_attention_2 True


# nohup bash /home/lg/workflow_tooluse/Flow_RL_luogan/my_llama3_full_finetune/run_finetune.sh > output.log 2>&1 &
