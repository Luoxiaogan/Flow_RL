#!/bin/bash

# 基于Accelerate的简化训练启动脚本
# 从复杂的7+1卡系统迁移而来，使用标准8卡分布式训练

set -e  # 遇到错误立即退出

echo "🚀 启动基于Accelerate的简化训练系统..."
echo "=================================================="

# 环境变量设置
export WANDB_PROJECT="llama3-8b-accelerate-training"
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7  # 8卡均匀使用
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # 添加src到Python路径

# DeepSpeed专用环境变量（重要：解决初始化冲突）
export ACCELERATE_USE_DEEPSPEED=true
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=1  # 避免系统过载

# 模型和数据路径（本地测试路径，服务器上需要修改）
MODEL_NAME="/nas/models/Meta-Llama-3.1-8B-Instruct"  # 服务器路径
# MODEL_NAME="/Users/luogan/models/Meta-Llama-3.1-8B-Instruct"  # 本地路径（如果有）

DATASET_PATH="/nas/ganluo/Flow_RL/training_data/training_data_raw_0825/filtered.jsonl"  # 服务器路径
# DATASET_PATH="training_data/sample.jsonl"  # 本地测试路径

OUTPUT_DIR="/nas/ganluo/sft_output/Llama-3.1-8B-accelerate-$(date +%Y%m%d_%H%M%S)"  # 服务器路径
# OUTPUT_DIR="./outputs/$(date +%Y%m%d_%H%M%S)"  # 本地路径

# 评估数据路径
EVAL_TEST_DATA_PATH="/nas/ganluo/Flow_RL/New_evaluation_and_RL/parquet_and_jsonl_data/test.jsonl"  # 服务器路径
# EVAL_TEST_DATA_PATH="test_data/sample_test.jsonl"  # 本地路径

# 训练参数
MODEL_TYPE="llama"  # 或 "qwen"
USE_LOSS_MASK=true  # 是否使用损失掩码（必须开启）
ENABLE_EVAL=true  # 是否启用原地评估
EVAL_INTERVAL=20  # 评估间隔
MAX_EVAL_SAMPLES=5  # 评估样本数（测试时用小数值）

# 训练超参数 - ZeRO-2优化配置（与deepspeed_zero2.json保持一致）
NUM_EPOCHS=3
PER_DEVICE_BATCH_SIZE=1      # 与deepspeed配置的train_micro_batch_size_per_gpu一致
GRAD_ACCUM_STEPS=4            # 与deepspeed配置的gradient_accumulation_steps一致
LEARNING_RATE=2e-5            # 与deepspeed配置的lr一致
MAX_SEQ_LENGTH=6500           # 长序列训练
SAVE_STEPS=500
LOGGING_STEPS=1
WARMUP_RATIO=0.03

# 启动信息
echo "🔧 环境变量配置完成"
echo "  WANDB_PROJECT: ${WANDB_PROJECT}"
echo "  ACCELERATE_USE_DEEPSPEED: ${ACCELERATE_USE_DEEPSPEED}"
echo "  OMP_NUM_THREADS: ${OMP_NUM_THREADS}"

# 启动训练
echo "🎯 使用DeepSpeed ZeRO-2开始训练..."
accelerate launch \
    --config_file /nas/ganluo/Flow_RL/my_llama3_h100_huggingface_accelerate/configs/accelerate_config.yaml \
    src/train.py \
    --model_name_or_path "${MODEL_NAME}" \
    --model_type "${MODEL_TYPE}" \
    --use_flash_attention_2 true \
    --use_loss_mask "${USE_LOSS_MASK}" \
    --dataset_path "${DATASET_PATH}" \
    --max_seq_length "${MAX_SEQ_LENGTH}" \
    --enable_inplace_eval "${ENABLE_EVAL}" \
    --eval_interval "${EVAL_INTERVAL}" \
    --eval_test_data_path "${EVAL_TEST_DATA_PATH}" \
    --eval_batch_size 1 \
    --max_eval_samples "${MAX_EVAL_SAMPLES}" \
    --eval_output_dir "${OUTPUT_DIR}/evaluation_reports" \
    --output_dir "${OUTPUT_DIR}" \
    --num_train_epochs "${NUM_EPOCHS}" \
    --per_device_train_batch_size "${PER_DEVICE_BATCH_SIZE}" \
    --gradient_accumulation_steps "${GRAD_ACCUM_STEPS}" \
    --learning_rate "${LEARNING_RATE}" \
    --warmup_ratio "${WARMUP_RATIO}" \
    --logging_steps "${LOGGING_STEPS}" \
    --save_steps "${SAVE_STEPS}" \
    --save_total_limit 3 \
    --report_to wandb \
    --run_name "zero2_$(date +%m%d_%H%M)" \
    --bf16 true \
    --tf32 true \
    --dataloader_drop_last true \
    --remove_unused_columns false \
    --dataloader_num_workers 0 \
    --max_grad_norm 1.0 \
    --weight_decay 0.01 \
    --logging_dir "${OUTPUT_DIR}/logs" \
    --seed 42 \
    --gradient_checkpointing true