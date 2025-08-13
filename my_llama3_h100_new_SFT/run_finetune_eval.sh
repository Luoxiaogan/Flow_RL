#!/bin/bash

# ============================================
# 训练+评估并行脚本
# 功能：启动训练进程并定期对新检查点进行评估
# ============================================

# 忽略SIGHUP信号
trap '' HUP
set -e

# --- 内存优化环境变量 ---
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=0

# ============================================
# 配置参数
# ============================================

# 模型类型配置
MODEL_TYPE="llama"  # 可选: "llama" 或 "qwen"

# 是否启用损失掩码
USE_LOSS_MASK=true

# 仅保存模型权重（不保存优化器状态）
SAVE_ONLY_MODEL=true

# 评估配置
EVAL_INTERVAL_MINUTES=30  # 评估间隔（分钟）
EVAL_NUM_SAMPLES=500       # 评估样本数（None表示全部）
EVAL_BATCH_SIZE=4          # 评估批大小
EVAL_USE_LOSS_MASK=true    # 评估时是否使用损失掩码

# ============================================
# 路径配置
# ============================================

# 基础路径
BASE_DIR="/nas/ganluo/Flow_RL/my_llama3_h100_new"
DEEPSPEED_CONFIG="${BASE_DIR}/configs/deepspeed_config_z3.json"

# H100服务器配置
NUM_GPUS=8
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# 评估用GPU（使用最后一个GPU进行评估，避免干扰训练）
EVAL_GPU=7

# --- 模型特定配置 ---
if [ "$MODEL_TYPE" = "qwen" ]; then
    echo "配置 Qwen-2.5-7B-Instruct..."
    MODEL_NAME="/nas/models/Qwen2.5-7B-Instruct"
    TRAIN_DATA="/nas/ganluo/training_data/0813_filter之后的COT_SFT数据/merged_training_data_qwen.jsonl"
    EVAL_DATA="/nas/ganluo/training_data/0813_filter之后的COT_SFT数据/eval_data_qwen.jsonl"  # 需要准备评估数据
    OUTPUT_DIR="/nas/ganluo/sft_output/Qwen2.5-7B-workflow-sft-eval"
    
    # Qwen 训练参数
    PER_DEVICE_BATCH_SIZE=4
    GRAD_ACCUM_STEPS=1
    LEARNING_RATE=2e-5
    MAX_SEQ_LENGTH=6500
    
elif [ "$MODEL_TYPE" = "llama" ]; then
    echo "配置 Llama-3.1-8B-Instruct..."
    MODEL_NAME="/nas/models/Meta-Llama-3-8B-Instruct"
    TRAIN_DATA="/nas/ganluo/training_data/0813_filter之后的COT_SFT数据/merged_training_data_llama.jsonl"
    EVAL_DATA="/nas/ganluo/training_data/0813_filter之后的COT_SFT数据/eval_data_llama.jsonl"  # 需要准备评估数据
    OUTPUT_DIR="/nas/ganluo/sft_output/Llama-3.1-8B-workflow-sft-eval"
    
    # Llama 训练参数
    PER_DEVICE_BATCH_SIZE=4
    GRAD_ACCUM_STEPS=1
    LEARNING_RATE=2e-5
    MAX_SEQ_LENGTH=6500
else
    echo "错误: MODEL_TYPE 必须是 'qwen' 或 'llama'"
    exit 1
fi

# 评估结果目录
EVAL_RESULTS_DIR="${OUTPUT_DIR}/eval_results"
mkdir -p $OUTPUT_DIR
mkdir -p $EVAL_RESULTS_DIR

# 日志文件
TRAIN_LOG="${OUTPUT_DIR}/train.log"
EVAL_LOG="${OUTPUT_DIR}/eval.log"

# ============================================
# 检查数据文件
# ============================================

if [ ! -f "$TRAIN_DATA" ]; then
    echo "错误: 训练数据未找到: $TRAIN_DATA"
    exit 1
fi

# 如果评估数据不存在，使用训练数据的一部分
if [ ! -f "$EVAL_DATA" ]; then
    echo "警告: 评估数据未找到，将使用训练数据进行评估"
    EVAL_DATA=$TRAIN_DATA
fi

# ============================================
# 启动训练进程
# ============================================

echo "=========================================="
echo "🚀 启动训练+评估系统"
echo "=========================================="
echo "模型: $MODEL_TYPE"
echo "训练数据: $TRAIN_DATA"
echo "评估数据: $EVAL_DATA"
echo "输出目录: $OUTPUT_DIR"
echo "评估间隔: ${EVAL_INTERVAL_MINUTES}分钟"
echo "仅保存模型: $SAVE_ONLY_MODEL"
echo "=========================================="

# 构建训练命令参数
TRAIN_ARGS=(
    --model_name_or_path $MODEL_NAME
    --model_type $MODEL_TYPE
    --dataset_path $TRAIN_DATA
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
    --save_total_limit 5  # 保存更多检查点用于评估
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
    TRAIN_ARGS+=(--use_loss_mask True)
fi

# 添加仅保存模型参数
if [ "$SAVE_ONLY_MODEL" = "true" ]; then
    TRAIN_ARGS+=(--save_only_model True)
fi

# 启动训练进程（后台运行）
echo "📚 启动训练进程..."
nohup python -m accelerate.commands.launch \
    --config_file ${BASE_DIR}/accelerate_config.yaml \
    ${BASE_DIR}/src/train.py \
    "${TRAIN_ARGS[@]}" \
    > $TRAIN_LOG 2>&1 &

TRAIN_PID=$!
echo "训练进程PID: $TRAIN_PID"
echo "训练日志: $TRAIN_LOG"

# 等待一些时间让训练开始
sleep 30

# ============================================
# 评估循环
# ============================================

echo ""
echo "📊 开始评估循环..."
echo "评估结果将保存到: $EVAL_RESULTS_DIR"
echo "评估日志: $EVAL_LOG"

# 记录已评估的检查点
EVALUATED_CHECKPOINTS=""

# 评估函数
evaluate_checkpoint() {
    local checkpoint_path=$1
    local checkpoint_name=$(basename $checkpoint_path)
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 评估检查点: $checkpoint_name" | tee -a $EVAL_LOG
    
    # 设置评估GPU
    export CUDA_VISIBLE_DEVICES=$EVAL_GPU
    
    # 构建评估命令
    EVAL_CMD="python ${BASE_DIR}/src/evaluation.py \
        --model_path $checkpoint_path \
        --eval_data $EVAL_DATA \
        --model_type $MODEL_TYPE \
        --batch_size $EVAL_BATCH_SIZE \
        --output_dir $EVAL_RESULTS_DIR"
    
    # 添加样本数限制
    if [ ! -z "$EVAL_NUM_SAMPLES" ]; then
        EVAL_CMD="$EVAL_CMD --num_samples $EVAL_NUM_SAMPLES"
    fi
    
    # 添加损失掩码参数
    if [ "$EVAL_USE_LOSS_MASK" = "true" ]; then
        EVAL_CMD="$EVAL_CMD --use_loss_mask"
    fi
    
    # 执行评估
    $EVAL_CMD >> $EVAL_LOG 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 评估完成: $checkpoint_name" | tee -a $EVAL_LOG
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 评估失败: $checkpoint_name" | tee -a $EVAL_LOG
    fi
    
    # 恢复GPU设置
    export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
}

# 主评估循环
while true; do
    # 检查训练进程是否还在运行
    if ! kill -0 $TRAIN_PID 2>/dev/null; then
        echo "训练进程已结束"
        break
    fi
    
    # 查找新的检查点
    for checkpoint in $(ls -d ${OUTPUT_DIR}/checkpoint-* 2>/dev/null | sort -V); do
        checkpoint_name=$(basename $checkpoint)
        
        # 检查是否已评估过
        if [[ ! " $EVALUATED_CHECKPOINTS " =~ " $checkpoint_name " ]]; then
            # 检查检查点是否完整（等待模型文件写入完成）
            if [ -f "$checkpoint/pytorch_model.bin" ] || [ -f "$checkpoint/model.safetensors" ]; then
                echo ""
                echo "🆕 发现新检查点: $checkpoint_name"
                
                # 评估检查点
                evaluate_checkpoint $checkpoint
                
                # 记录已评估
                EVALUATED_CHECKPOINTS="$EVALUATED_CHECKPOINTS $checkpoint_name"
            fi
        fi
    done
    
    # 等待下一次评估
    echo "💤 等待${EVAL_INTERVAL_MINUTES}分钟后进行下一次评估检查..."
    sleep $((EVAL_INTERVAL_MINUTES * 60))
done

# ============================================
# 最终评估
# ============================================

echo ""
echo "🏁 训练完成，进行最终模型评估..."

# 评估最终模型
if [ -f "$OUTPUT_DIR/pytorch_model.bin" ] || [ -f "$OUTPUT_DIR/model.safetensors" ]; then
    evaluate_checkpoint $OUTPUT_DIR
fi

# ============================================
# 生成评估报告
# ============================================

echo ""
echo "📈 生成评估报告..."

# Python脚本生成报告
python -c "
import json
import os
from pathlib import Path

eval_dir = '$EVAL_RESULTS_DIR'
report_path = os.path.join(eval_dir, 'evaluation_report.json')

results = []
for file in Path(eval_dir).glob('eval_*.json'):
    with open(file) as f:
        data = json.load(f)
        results.append({
            'checkpoint': file.stem.replace('eval_', ''),
            'perplexity': data.get('perplexity', 0),
            'avg_loss': data.get('avg_loss', 0),
            'num_samples': data.get('num_samples', 0)
        })

# 按检查点排序
results.sort(key=lambda x: x['checkpoint'])

# 保存报告
report = {
    'model_type': '$MODEL_TYPE',
    'output_dir': '$OUTPUT_DIR',
    'num_checkpoints': len(results),
    'results': results
}

with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f'报告已保存到: {report_path}')

# 打印摘要
print('\n评估摘要:')
print('-' * 50)
for r in results:
    print(f\"{r['checkpoint']}: PPL={r['perplexity']:.2f}, Loss={r['avg_loss']:.4f}\")
"

echo ""
echo "=========================================="
echo "✅ 训练+评估完成！"
echo "=========================================="
echo "训练日志: $TRAIN_LOG"
echo "评估日志: $EVAL_LOG"
echo "评估结果: $EVAL_RESULTS_DIR"
echo "=========================================="