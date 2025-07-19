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
# source /opt/miniconda3/etc/profile.d/conda.sh
source /mnt/mydisk/miniconda3/etc/profile.d/conda.sh
conda activate lg_workflow

# 忽略SIGHUP信号
trap '' HUP
# 确保脚本在任何命令失败时退出
set -e

# --- 内存优化环境变量 ---
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=0
# 添加以下针对V100的优化
export NCCL_DEBUG=INFO
export NCCL_IB_DISABLE=1
export NCCL_P2P_DISABLE=1

# --- 可配置参数 ---
export WANDB_PROJECT="llama3-8b-workflow"
MODEL_NAME="/mnt/mydisk/haoyu/hf_models/hub/models--meta-llama--Meta-Llama-3-8B-Instruct/snapshots/e1945c40cd546c78e41f1151f4db032b271faeaa"
DATASET_PATH="/root/lg/Flow_RL_luogan/training_data/gsm8k/jsonl1_verified_correct.jsonl"
OUTPUT_DIR="/mnt/mydisk/luogan/Llama-3-8B-Instruct-Workflow/gsm8k"
DEEPSPEED_CONFIG="/root/lg/Flow_RL_luogan/my_llama3_full_finetune/configs/deepspeed_config_z2.json"

NUM_GPUS=4 # 设置为4个GPU
export CUDA_VISIBLE_DEVICES=0,1,2,3 # 使用前4张GPU
# 全局批大小 = NUM_GPUS * GRAD_ACCUM_STEPS * PER_DEVICE_BATCH_SIZE
# 目标全局批次大小32: 4 * 1 * 8 = 32
PER_DEVICE_BATCH_SIZE=1
GRAD_ACCUM_STEPS=8 

# (可选) 张量并行配置
# 对于8B模型在2张A800上，TP不是必须的，但可以开启以观察效果
# 开启TP需要修改模型加载方式，通常在更复杂的框架如Megatron-LM中处理
# 在transformers+accelerate中，deepspeed会自动处理数据并行(DP)，这是最直接的方式
# 如果要强行开启TP，deepspeed配置需要修改，且对模型结构有要求。
# 这里我们专注于最高效的数据并行(ZeRO-3)方案。

# --- Accelerate 启动命令 ---

# 使用python -m确保使用当前conda环境中的accelerate
python -m accelerate.commands.launch --config_file /root/lg/Flow_RL_luogan/my_llama3_full_finetune/accelerate_config.yaml /root/lg/Flow_RL_luogan/my_llama3_full_finetune/src/train.py \
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
    --fp16 True \
    # --tf32 True \ TF32 数据格式需要 Ampere架构或更新的GPU
    --gradient_checkpointing True \
    --report_to "wandb" \
    --deepspeed $DEEPSPEED_CONFIG \
    --max_seq_length 4096 \
    # --use_flash_attention_2 True v100不支持


# nohup bash /root/lg/Flow_RL_luogan/my_llama3_full_finetune/run_finetune.sh > output_new.log 2>&1 &