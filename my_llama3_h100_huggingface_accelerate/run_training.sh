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
USE_LOSS_MASK=false  # 是否使用损失掩码
ENABLE_EVAL=true  # 是否启用原地评估
EVAL_INTERVAL=20  # 评估间隔
MAX_EVAL_SAMPLES=5  # 评估样本数（测试时用小数值）

# 训练超参数 - DDP优化配置（非ZeRO-3）
NUM_EPOCHS=3
PER_DEVICE_BATCH_SIZE=1  # 减小，因为每GPU现在存储完整模型（DDP vs ZeRO-3）
GRAD_ACCUM_STEPS=4       # 增加，保持相同有效batch size
LEARNING_RATE=2e-5
MAX_SEQ_LENGTH=4096
SAVE_STEPS=500
LOGGING_STEPS=10
WARMUP_RATIO=0.03

# 计算全局批次大小
GLOBAL_BATCH_SIZE=$((8 * PER_DEVICE_BATCH_SIZE * GRAD_ACCUM_STEPS))  # = 1×4×8 = 32

echo "📋 训练配置:"
echo "  模型类型: ${MODEL_TYPE}"
echo "  模型路径: ${MODEL_NAME}"
echo "  数据集路径: ${DATASET_PATH}"
echo "  输出目录: ${OUTPUT_DIR}"
echo "  使用损失掩码: ${USE_LOSS_MASK}"
echo "  启用原地评估: ${ENABLE_EVAL}"
echo "  评估间隔: ${EVAL_INTERVAL}"
echo "  最大序列长度: ${MAX_SEQ_LENGTH}"
echo "  训练轮数: ${NUM_EPOCHS}"
echo "  每设备批次大小: ${PER_DEVICE_BATCH_SIZE}"
echo "  梯度累积步数: ${GRAD_ACCUM_STEPS}"
echo "  全局批次大小: ${GLOBAL_BATCH_SIZE}"
echo "  学习率: ${LEARNING_RATE}"
echo ""

# 检查关键文件是否存在
echo "🔍 检查关键文件..."

if [ ! -f "configs/accelerate_config.yaml" ]; then
    echo "❌ 错误: 找不到 configs/accelerate_config.yaml"
    exit 1
fi

if [ ! -f "configs/evaluation_config.yaml" ]; then
    echo "❌ 错误: 找不到 configs/evaluation_config.yaml"
    exit 1
fi

if [ ! -f "src/train.py" ]; then
    echo "❌ 错误: 找不到 src/train.py"
    exit 1
fi

echo "✅ 关键文件检查通过"

# 创建输出目录
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}/evaluation_reports"
mkdir -p "logs"

echo "📁 输出目录已创建: ${OUTPUT_DIR}"

# 检查Accelerate配置
echo "🔧 验证Accelerate配置..."
accelerate test --config_file configs/accelerate_config.yaml

# 启动训练
echo ""
echo "🎯 开始训练..."
echo "=================================================="

accelerate launch \
    --config_file configs/accelerate_config.yaml \
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
    --run_name "accelerate_$(date +%m%d_%H%M)" \
    --bf16 true \
    --tf32 true \
    --dataloader_drop_last true \
    --remove_unused_columns false \
    --dataloader_num_workers 0 \
    --max_grad_norm 1.0 \
    --weight_decay 0.01 \
    --logging_dir "${OUTPUT_DIR}/logs" \
    --seed 42

EXIT_CODE=$?

echo ""
echo "=================================================="
if [ ${EXIT_CODE} -eq 0 ]; then
    echo "🎉 训练成功完成！"
    echo "📁 输出目录: ${OUTPUT_DIR}"
    echo "📊 评估报告: ${OUTPUT_DIR}/evaluation_reports/"
    echo "📝 训练日志: ${OUTPUT_DIR}/logs/"
else
    echo "❌ 训练失败，退出代码: ${EXIT_CODE}"
    echo "🔍 请检查上述日志信息"
fi

echo "=================================================="