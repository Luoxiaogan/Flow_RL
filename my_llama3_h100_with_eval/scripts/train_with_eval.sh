#!/bin/bash

# Script for fine-tuning with automatic evaluation
# This script enables checkpoint evaluation during training

# Ignore SIGHUP signal
trap '' HUP
set -e

# --- Memory optimization environment variables ---
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=0

# ============================================
# Model Configuration
# ============================================
MODEL_TYPE="llama"  # "qwen" or "llama"
USE_LOSS_MASK=true  # Enable loss masking for better training

# ============================================
# Evaluation Configuration
# ============================================
ENABLE_AUTO_EVAL=true  # Enable automatic evaluation
EVAL_INTERVAL=1        # Evaluate every N checkpoints
EVAL_BATCH_SIZE=4      # Batch size for evaluation (reduce if OOM)
ASYNC_EVAL=true        # Run evaluation asynchronously
MAX_EVAL_SAMPLES=50    # Limit evaluation samples for testing (remove for full eval)

# --- Common Configuration ---
export WANDB_PROJECT="${MODEL_TYPE}-8b-workflow-sft-with-eval"
DEEPSPEED_CONFIG="/nas/ganluo/Flow_RL/my_llama3_h100_with_eval/configs/training/deepspeed_z3.json"

# H100 Server Configuration
NUM_GPUS=8
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# --- Model-specific Configuration ---
if [ "$MODEL_TYPE" = "qwen" ]; then
    echo "Training Qwen-2.5-7B-Instruct with evaluation..."
    MODEL_NAME="/nas/models/Qwen2.5-7B-Instruct"
    DATASET_PATH="/nas/ganluo/training_data/0813_filter之后的COT_SFT数据/merged_training_data_qwen.jsonl"
    OUTPUT_DIR="/nas/ganluo/sft_output/Qwen2.5-7B-workflow-sft-eval"
    
    # Qwen training parameters
    PER_DEVICE_BATCH_SIZE=4
    GRAD_ACCUM_STEPS=1
    LEARNING_RATE=2e-5
    MAX_SEQ_LENGTH=6500
    
elif [ "$MODEL_TYPE" = "llama" ]; then
    echo "Training Llama-3.1-8B-Instruct with evaluation..."
    MODEL_NAME="/nas/models/Meta-Llama-3-8B-Instruct"
    DATASET_PATH="/nas/ganluo/training_data/0813_filter之后的COT_SFT数据/merged_training_data_llama.jsonl"
    OUTPUT_DIR="/nas/ganluo/sft_output/Llama-3.1-8B-workflow-sft-eval"
    
    # Llama training parameters
    PER_DEVICE_BATCH_SIZE=4
    GRAD_ACCUM_STEPS=1
    LEARNING_RATE=2e-5
    MAX_SEQ_LENGTH=6500
else
    echo "Error: MODEL_TYPE must be 'qwen' or 'llama'"
    exit 1
fi

# --- Evaluation Data Path ---
EVAL_TEST_DATA="/nas/ganluo/Flow_RL/New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl"
REWARD_SERVER_URL="http://localhost:8899"
EVAL_OUTPUT_DIR="${OUTPUT_DIR}/evaluation_reports"

# Create output directories
mkdir -p $OUTPUT_DIR
mkdir -p $EVAL_OUTPUT_DIR

# Check if dataset exists
if [ ! -f "$DATASET_PATH" ]; then
    echo "Error: Training dataset not found at $DATASET_PATH"
    exit 1
fi

# Check if evaluation dataset exists
if [ "$ENABLE_AUTO_EVAL" = "true" ] && [ ! -f "$EVAL_TEST_DATA" ]; then
    echo "Error: Evaluation dataset not found at $EVAL_TEST_DATA"
    exit 1
fi

echo "=========================================="
echo "Configuration Summary:"
echo "=========================================="
echo "Model: $MODEL_TYPE"
echo "Training Data: $DATASET_PATH"
echo "Output: $OUTPUT_DIR"
echo "Global batch size: $((NUM_GPUS * PER_DEVICE_BATCH_SIZE * GRAD_ACCUM_STEPS))"
echo "Loss masking: $USE_LOSS_MASK"
echo ""
echo "Evaluation Settings:"
echo "  Enabled: $ENABLE_AUTO_EVAL"
if [ "$ENABLE_AUTO_EVAL" = "true" ]; then
    echo "  Test Data: $EVAL_TEST_DATA"
    echo "  Reward Server: $REWARD_SERVER_URL"
    echo "  Interval: Every $EVAL_INTERVAL checkpoint(s)"
    echo "  Batch Size: $EVAL_BATCH_SIZE"
    echo "  Async: $ASYNC_EVAL"
    echo "  Max Samples: ${MAX_EVAL_SAMPLES:-All}"
    echo "  Reports: $EVAL_OUTPUT_DIR"
fi
echo "=========================================="

# --- Check Reward Server Status (if evaluation enabled) ---
if [ "$ENABLE_AUTO_EVAL" = "true" ]; then
    echo ""
    echo "Checking Reward Server status..."
    if curl -s -o /dev/null -w "%{http_code}" $REWARD_SERVER_URL/health | grep -q "200"; then
        echo "✓ Reward Server is running at $REWARD_SERVER_URL"
    else
        echo "⚠ Warning: Reward Server is not running at $REWARD_SERVER_URL"
        echo "Please start it manually:"
        echo "  cd New_evaluation_and_RL/reward_server"
        echo "  python scoreflow_reward_server.py"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# --- Build Command Arguments ---
CMD_ARGS=(
    --model_name_or_path $MODEL_NAME
    --model_type $MODEL_TYPE
    --dataset_path $DATASET_PATH
    --output_dir $OUTPUT_DIR
    --num_train_epochs 10
    --per_device_train_batch_size $PER_DEVICE_BATCH_SIZE
    --per_device_eval_batch_size 2
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS
    --learning_rate $LEARNING_RATE
    --lr_scheduler_type "cosine"
    --warmup_ratio 0.03
    --logging_steps 1
    --save_strategy "steps"
    --save_steps 200
    --save_total_limit 3
    --bf16 True
    --tf32 True
    --gradient_checkpointing True
    --report_to "wandb"
    --deepspeed $DEEPSPEED_CONFIG
    --max_seq_length $MAX_SEQ_LENGTH
    --use_flash_attention_2 True
)

# Add loss masking parameter
if [ "$USE_LOSS_MASK" = "true" ]; then
    CMD_ARGS+=(--use_loss_mask True)
fi

# Add evaluation parameters
if [ "$ENABLE_AUTO_EVAL" = "true" ]; then
    CMD_ARGS+=(
        --enable_auto_eval True
        --eval_test_data_path $EVAL_TEST_DATA
        --reward_server_url $REWARD_SERVER_URL
        --eval_batch_size $EVAL_BATCH_SIZE
        --async_evaluation $ASYNC_EVAL
        --eval_interval $EVAL_INTERVAL
        --eval_output_dir $EVAL_OUTPUT_DIR
    )
    
    if [ ! -z "$MAX_EVAL_SAMPLES" ]; then
        CMD_ARGS+=(--max_eval_samples $MAX_EVAL_SAMPLES)
    fi
fi

# --- Launch Training with Accelerate ---
echo ""
echo "Starting training with automatic evaluation..."
echo ""

python -m accelerate.commands.launch \
    --config_file /nas/ganluo/Flow_RL/my_llama3_h100_with_eval/configs/training/accelerate_config.yaml \
    /nas/ganluo/Flow_RL/my_llama3_h100_with_eval/src/training/trainer.py \
    "${CMD_ARGS[@]}"

echo ""
echo "Training completed!"
if [ "$ENABLE_AUTO_EVAL" = "true" ]; then
    echo "Evaluation reports saved to: $EVAL_OUTPUT_DIR"
fi