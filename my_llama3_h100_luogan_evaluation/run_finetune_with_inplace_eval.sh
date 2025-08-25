#!/bin/bash

# 带有原地评估的微调脚本
# 使用当前模型权重进行评估，无需保存检查点

# 忽略SIGHUP信号
trap '' HUP
set -e

# --- 内存优化环境变量 ---
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=0

# ============================================
# 获取项目根路径
# ============================================
# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 从root.yaml读取项目根路径
ROOT=$(python3 "$SCRIPT_DIR/get_root.py" 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "警告：无法读取root.yaml，使用默认服务器路径"
    ROOT="/nas/ganluo/Flow_RL"
fi
echo "项目根路径: $ROOT"

# ============================================
# 模型配置
# ============================================
MODEL_TYPE="qwen"  # "qwen" 或 "llama"
USE_LOSS_MASK=true  # 启用损失掩码以改善训练效果

# ============================================
# 配置文件路径（基于根路径）
# ============================================
# Reward Server配置文件
CONFIG_FILE="$ROOT/New_evaluation_and_RL/config.yaml"
# 评估配置文件
EVAL_CONFIG_FILE="$ROOT/my_llama3_h100_luogan_evaluation/configs/evaluation_config.yaml"
# DeepSpeed配置
DEEPSPEED_CONFIG="$ROOT/my_llama3_h100_luogan_evaluation/configs/deepspeed_config_z3.json"

# ============================================
# 通用配置
# ============================================
export WANDB_PROJECT="${MODEL_TYPE}-8b-workflow-inplace-eval"

# H100服务器配置
NUM_GPUS=8
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# --- 特定模型配置 ---
if [ "$MODEL_TYPE" = "qwen" ]; then
    echo "正在使用原地评估训练Qwen3-8B..."
    MODEL_NAME="/nas/models/Qwen3-8B"
    DATASET_PATH="/nas/ganluo/Flow_RL/training_data/training_data_raw_0825/filtered.jsonl"
    OUTPUT_DIR="/nas/ganluo/sft_output/Qwen3-8B-inplace-eval"
    
    # Qwen训练参数 (7卡训练调整)
    PER_DEVICE_BATCH_SIZE=2  # 从4调整为2，配合梯度累积
    GRAD_ACCUM_STEPS=2       # 从1调整为2，保持训练稳定性
    LEARNING_RATE=2e-5
    MAX_SEQ_LENGTH=6500
    
elif [ "$MODEL_TYPE" = "llama" ]; then
    echo "正在使用原地评估训练Llama-3.1-8B-Instruct..."
    MODEL_NAME="/nas/models/Meta-Llama-3-8B-Instruct"
    DATASET_PATH="/nas/ganluo/Flow_RL/training_data/training_data_raw_0825/filtered.jsonl"
    OUTPUT_DIR="/nas/ganluo/sft_output/Llama-3.1-8B-inplace-eval"
    
    # Llama训练参数 (7卡训练调整)
    PER_DEVICE_BATCH_SIZE=2  # 从4调整为2，配合梯度累积
    GRAD_ACCUM_STEPS=2       # 从1调整为2，保持训练稳定性
    LEARNING_RATE=2e-5
    MAX_SEQ_LENGTH=6500
else
    echo "错误：MODEL_TYPE必须是'qwen'或'llama'"
    exit 1
fi

# ============================================
# 从evaluation_config.yaml读取原地评估配置
# ============================================
ENABLE_INPLACE_EVAL=true  # 启用原地评估

# 计算训练总步数（用于更智能的配置分析）
NUM_TRAIN_EPOCHS=10  # 训练轮数

# 使用辅助脚本读取配置并分析训练信息
if [ -f "$SCRIPT_DIR/read_eval_config.py" ]; then
    # 传递训练参数给辅助脚本进行智能分析
    eval $(python3 "$SCRIPT_DIR/read_eval_config.py" \
        "$EVAL_CONFIG_FILE" \
        --dataset "$DATASET_PATH" \
        --batch-size "$PER_DEVICE_BATCH_SIZE" \
        --grad-accum "$GRAD_ACCUM_STEPS" \
        --num-gpus "$NUM_GPUS" \
        --epochs "$NUM_TRAIN_EPOCHS" \
        2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "评估配置（从 $EVAL_CONFIG_FILE 读取）："
        echo "  评估间隔: 每 $EVAL_INTERVAL 步"
        echo "  评估批次大小: $EVAL_BATCH_SIZE"
        echo "  最大评估样本数: ${MAX_EVAL_SAMPLES:-全部}"
        echo "  测试数据: $EVAL_TEST_DATA"
        
        # 显示智能分析结果（如果有）
        if [ ! -z "$TOTAL_TRAIN_SAMPLES" ]; then
            echo ""
            echo "训练数据分析："
            echo "  训练样本总数: $TOTAL_TRAIN_SAMPLES"
            echo "  全局批次大小: $GLOBAL_BATCH_SIZE"
            echo "  每轮步数: $STEPS_PER_EPOCH"
            echo "  总训练步数: $TOTAL_STEPS"
            echo "  预计评估次数: $EXPECTED_EVAL_COUNT"
        fi
    else
        echo "警告：无法读取评估配置，使用默认值"
        EVAL_INTERVAL=50
        EVAL_BATCH_SIZE=4
        MAX_EVAL_SAMPLES=20
        EVAL_TEST_DATA="$ROOT/New_evaluation_and_RL/parquet_and_jsonl_data/single/test.jsonl"
    fi
else
    # 回退到默认值
    echo "警告：配置读取脚本未找到，使用默认配置"
    EVAL_INTERVAL=50
    EVAL_BATCH_SIZE=4
    MAX_EVAL_SAMPLES=20
    EVAL_TEST_DATA="/nas/ganluo/Flow_RL/New_evaluation_and_RL/parquet_and_jsonl_data/single/test.jsonl"
fi

# --- 评估输出目录 ---
EVAL_OUTPUT_DIR="${OUTPUT_DIR}/evaluation_reports"

# 创建输出目录
mkdir -p $OUTPUT_DIR
mkdir -p $EVAL_OUTPUT_DIR

# 检查数据集是否存在
if [ ! -f "$DATASET_PATH" ]; then
    echo "错误：在$DATASET_PATH未找到训练数据集"
    exit 1
fi

# 检查评估数据集是否存在
if [ "$ENABLE_INPLACE_EVAL" = "true" ] && [ ! -f "$EVAL_TEST_DATA" ]; then
    echo "错误：在$EVAL_TEST_DATA未找到评估数据集"
    exit 1
fi

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "警告：在$CONFIG_FILE未找到配置文件"
    echo "Reward服务器端口将默认为8897"
fi

# --- 从config.yaml获取Reward Server端口 ---
if [ -f "$CONFIG_FILE" ]; then
    REWARD_PORT=$(python3 -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
port = config['services']['scoreflow_reward']['port']
print(port)
" 2>/dev/null || echo "8897")
else
    REWARD_PORT=8897
fi

REWARD_URL="http://localhost:${REWARD_PORT}"

echo "=========================================="
echo "配置摘要："
echo "=========================================="
echo "模型：$MODEL_TYPE"
echo "训练数据：$DATASET_PATH"
echo "输出目录：$OUTPUT_DIR"
echo "全局批次大小：$((NUM_GPUS * PER_DEVICE_BATCH_SIZE * GRAD_ACCUM_STEPS))"
echo "损失掩码：$USE_LOSS_MASK"
echo ""
echo "原地评估设置："
echo "  已启用：$ENABLE_INPLACE_EVAL"
if [ "$ENABLE_INPLACE_EVAL" = "true" ]; then
    echo "  配置文件：$EVAL_CONFIG_FILE"
    echo "  测试数据：$EVAL_TEST_DATA"
    echo "  Reward服务器：$REWARD_URL (端口 $REWARD_PORT)"
    echo "  评估间隔：每$EVAL_INTERVAL步"
    echo "  批次大小：$EVAL_BATCH_SIZE"
    echo "  最大样本数：${MAX_EVAL_SAMPLES:-全部}"
    echo "  报告目录：$EVAL_OUTPUT_DIR"
fi
echo ""
echo "检查点设置："
echo "  保存策略：按步数"
echo "  保存步数：1000（降低频率）"
echo "  保存限制：2（只保留最后2个检查点）"
echo "=========================================="

# --- 检查Reward Server状态（如果启用了评估）---
if [ "$ENABLE_INPLACE_EVAL" = "true" ]; then
    echo ""
    echo "正在检查Reward服务器状态..."
    if curl -s -o /dev/null -w "%{http_code}" $REWARD_URL/health | grep -q "200"; then
        echo "✓ Reward服务器正在$REWARD_URL运行"
    else
        echo "⚠ 警告：Reward服务器未在$REWARD_URL运行"
        echo "请手动启动："
        echo "  cd New_evaluation_and_RL/reward_server"
        echo "  python scoreflow_reward_server.py --port $REWARD_PORT"
        echo ""
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# --- 构建命令参数 ---
CMD_ARGS=(
    --model_name_or_path $MODEL_NAME
    --model_type $MODEL_TYPE
    --dataset_path $DATASET_PATH
    --output_dir $OUTPUT_DIR
    --num_train_epochs $NUM_TRAIN_EPOCHS
    --per_device_train_batch_size $PER_DEVICE_BATCH_SIZE
    --per_device_eval_batch_size 2
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS
    --learning_rate $LEARNING_RATE
    --lr_scheduler_type "cosine"
    --warmup_ratio 0.03
    --logging_steps 1
    --save_strategy "steps"
    --save_steps 1000      # 降低检查点保存频率
    --save_total_limit 2   # 只保留最后2个检查点
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

# 添加原地评估参数
if [ "$ENABLE_INPLACE_EVAL" = "true" ]; then
    CMD_ARGS+=(
        --enable_inplace_eval True
        --eval_interval $EVAL_INTERVAL
        --eval_test_data_path $EVAL_TEST_DATA
        --eval_batch_size $EVAL_BATCH_SIZE
        --eval_output_dir $EVAL_OUTPUT_DIR
    )
    
    if [ ! -z "$MAX_EVAL_SAMPLES" ]; then
        CMD_ARGS+=(--max_eval_samples $MAX_EVAL_SAMPLES)
    fi
fi

# --- 使用Accelerate启动训练 ---
echo ""
echo "开始使用原地评估进行训练..."
echo "将每$EVAL_INTERVAL步使用当前模型权重进行评估"
echo ""

python -m accelerate.commands.launch \
    --config_file "$ROOT/my_llama3_h100_luogan_evaluation/accelerate_config.yaml" \
    "$ROOT/my_llama3_h100_luogan_evaluation/src/train.py" \
    "${CMD_ARGS[@]}"

echo ""
echo "训练完成！"
if [ "$ENABLE_INPLACE_EVAL" = "true" ]; then
    echo "评估报告已保存至：$EVAL_OUTPUT_DIR"
fi