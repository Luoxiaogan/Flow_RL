#!/bin/bash

# 确保脚本在任何命令失败时退出
set -e

# --- 可配置参数 ---
export WANDB_PROJECT="llama3-8b-workflow-full-sft"
MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
DATASET_PATH="./data/train_data.jsonl"
OUTPUT_DIR="./results/Llama-3-8B-Instruct-Workflow-Expert-Full"
DEEPSPEED_CONFIG="./configs/deepspeed_config_z3.json"

NUM_GPUS=2
# 全局批大小 = NUM_GPUS * GRAD_ACCUM_STEPS * PER_DEVICE_BATCH_SIZE
# 假设我们想要一个64的全局批大小
PER_DEVICE_BATCH_SIZE=4
GRAD_ACCUM_STEPS=8 # 64 / 2 / 4 = 8

# (可选) 张量并行配置
# 对于8B模型在2张A800上，TP不是必须的，但可以开启以观察效果
# 开启TP需要修改模型加载方式，通常在更复杂的框架如Megatron-LM中处理
# 在transformers+accelerate中，deepspeed会自动处理数据并行(DP)，这是最直接的方式
# 如果要强行开启TP，deepspeed配置需要修改，且对模型结构有要求。
# 这里我们专注于最高效的数据并行(ZeRO-3)方案。

# --- Accelerate 启动命令 ---

# 使用 accelerate launch 来启动，它会自动处理分布式环境
accelerate launch --config_file ./accelerate_config.yaml src/train.py \
    --model_name_or_path $MODEL_NAME \
    --dataset_path $DATASET_PATH \
    --output_dir $OUTPUT_DIR \
    --num_train_epochs 1 \
    --per_device_train_batch_size $PER_DEVICE_BATCH_SIZE \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS \
    --learning_rate 2e-5 \
    --lr_scheduler_type "cosine" \
    --warmup_ratio 0.03 \
    --logging_steps 5 \
    --save_steps 50 \
    --save_total_limit 2 \
    --bf16 True \
    --tf32 True \
    --gradient_checkpointing True \
    --report_to "wandb" \
    --deepspeed $DEEPSPEED_CONFIG \
    --max_seq_length 2048 \
    --use_flash_attention_2 True