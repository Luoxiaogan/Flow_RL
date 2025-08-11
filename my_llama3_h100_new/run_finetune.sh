#!/bin/bash

# 忽略SIGHUP信号
trap '' HUP
set -e

# --- 内存优化环境变量 ---
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=0

# ============================================
# 选择模型类型: "qwen" 或 "llama"
# ============================================
MODEL_TYPE="llama"  # 修改这里来切换模型

# ============================================
# 是否启用损失掩码 (只在助手回答上计算损失)
# ============================================
USE_LOSS_MASK=true  # 设置为 true 启用损失掩码

# --- 通用配置 ---
export WANDB_PROJECT="${MODEL_TYPE}-8b-workflow-sft"
DEEPSPEED_CONFIG="/nas/ganluo/Flow_RL/my_llama3_h100/configs/deepspeed_config_z3.json"

# H100服务器配置
NUM_GPUS=8
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# --- 模型特定配置 ---
if [ "$MODEL_TYPE" = "qwen" ]; then
    echo "Training Qwen-2.5-7B-Instruct..."
    MODEL_NAME="/nas/models/Qwen2.5-7B-Instruct"  # 需要确认实际路径
    DATASET_PATH="/nas/ganluo/Flow_RL/training_data/0807_SFT_没有filter就合并/merged_training_data_qwen.jsonl"
    OUTPUT_DIR="/nas/ganluo/sft_output/Qwen2.5-7B-workflow-sft"
    
    # Qwen 推荐的训练参数
    PER_DEVICE_BATCH_SIZE=4
    GRAD_ACCUM_STEPS=4
    LEARNING_RATE=2e-5
    MAX_SEQ_LENGTH=8192  # Qwen支持更长的序列
    
elif [ "$MODEL_TYPE" = "llama" ]; then
    echo "Training Llama-3.1-8B-Instruct..."
    MODEL_NAME="/nas/models/Meta-Llama-3-8B-Instruct"
    DATASET_PATH="/nas/ganluo/Flow_RL/training_data/0807_SFT_没有filter就合并/merged_training_data_llama.jsonl"
    OUTPUT_DIR="/nas/ganluo/sft_output/Llama-3.1-8B-workflow-sft"
    
    # Llama 推荐的训练参数
    PER_DEVICE_BATCH_SIZE=4
    GRAD_ACCUM_STEPS=4
    LEARNING_RATE=1e-5
    MAX_SEQ_LENGTH=4096
else
    echo "Error: MODEL_TYPE must be 'qwen' or 'llama'"
    exit 1
fi

# 创建输出目录
mkdir -p $OUTPUT_DIR

# 检查数据文件是否存在
if [ ! -f "$DATASET_PATH" ]; then
    echo "Error: Dataset not found at $DATASET_PATH"
    exit 1
fi

echo "=========================================="
echo "Model: $MODEL_TYPE"
echo "Dataset: $DATASET_PATH"
echo "Output: $OUTPUT_DIR"
echo "Global batch size: $((NUM_GPUS * PER_DEVICE_BATCH_SIZE * GRAD_ACCUM_STEPS))"
echo "Loss masking: $USE_LOSS_MASK"
echo "=========================================="

# --- 构建命令参数 ---
CMD_ARGS=(
    --model_name_or_path $MODEL_NAME
    --model_type $MODEL_TYPE
    --dataset_path $DATASET_PATH
    --output_dir $OUTPUT_DIR
    --num_train_epochs 3
    --per_device_train_batch_size $PER_DEVICE_BATCH_SIZE
    --per_device_eval_batch_size 2
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS
    --learning_rate $LEARNING_RATE
    --lr_scheduler_type "cosine"
    --warmup_ratio 0.03
    --logging_steps 1
    --save_strategy "steps"
    --save_steps 500
    --save_total_limit 3
    --bf16 True
    --tf32 True
    --gradient_checkpointing True
    --report_to "wandb"
    --deepspeed $DEEPSPEED_CONFIG
    --max_seq_length $MAX_SEQ_LENGTH
    --use_flash_attention_2 True
)

# 添加损失掩码参数
if [ "$USE_LOSS_MASK" = "true" ]; then
    CMD_ARGS+=(--use_loss_mask True)
fi

# --- Accelerate 启动命令 ---
python -m accelerate.commands.launch \
    --config_file /nas/ganluo/Flow_RL/my_llama3_h100/accelerate_config.yaml \
    /nas/ganluo/Flow_RL/my_llama3_h100/src/train.py \
    "${CMD_ARGS[@]}"