#!/bin/bash

# ========================================
# Qwen3-Thinking LoRA 训练脚本（带实时监控）
# ========================================

# 设置环境变量
export CUDA_VISIBLE_DEVICES=0

# 生成时间戳
export TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "训练时间戳: $TIMESTAMP"

# 脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ========================================
# 1. 检查并应用补丁
# ========================================
echo "检查 LLaMA-Factory 补丁状态..."

# 尝试找到 llamafactory 安装位置
LLAMA_FACTORY_PATH=$(python -c "import llamafactory; import os; print(os.path.dirname(llamafactory.__file__))" 2>/dev/null | tail -n 1)

if [ -z "$LLAMA_FACTORY_PATH" ]; then
    echo "错误: 未找到 LLaMA-Factory 安装"
    echo "请先安装: pip install llamafactory"
    exit 1
fi

echo "LLaMA-Factory 路径: $LLAMA_FACTORY_PATH"

# 检查补丁是否已应用（通过检查关键的回调类）
if ! grep -q "SampleGenerationCallback" "$LLAMA_FACTORY_PATH/train/callbacks.py" 2>/dev/null; then
    echo "正在应用样本生成补丁..."
    
    # 备份原文件
    echo "备份原始文件..."
    cp "$LLAMA_FACTORY_PATH/hparams/finetuning_args.py" "$LLAMA_FACTORY_PATH/hparams/finetuning_args.py.bak" 2>/dev/null
    cp "$LLAMA_FACTORY_PATH/train/callbacks.py" "$LLAMA_FACTORY_PATH/train/callbacks.py.bak" 2>/dev/null
    cp "$LLAMA_FACTORY_PATH/train/sft/workflow.py" "$LLAMA_FACTORY_PATH/train/sft/workflow.py.bak" 2>/dev/null
    
    # 应用补丁
    cp "$SCRIPT_DIR/src/llamafactory/hparams/finetuning_args.py" "$LLAMA_FACTORY_PATH/hparams/" || {
        echo "错误: 无法复制 finetuning_args.py"
        exit 1
    }
    cp "$SCRIPT_DIR/src/llamafactory/train/callbacks.py" "$LLAMA_FACTORY_PATH/train/" || {
        echo "错误: 无法复制 callbacks.py"
        exit 1
    }
    cp "$SCRIPT_DIR/src/llamafactory/train/sft/workflow.py" "$LLAMA_FACTORY_PATH/train/sft/" || {
        echo "错误: 无法复制 workflow.py"
        exit 1
    }
    
    echo "✅ 补丁应用成功！"
else
    echo "✅ 补丁已存在，无需重复应用"
fi

# ========================================
# 2. 选择配置文件
# ========================================
# 默认配置文件（已注释掉 template 和 enable_thinking，使用模型自带配置）
CONFIG_FILE="$SCRIPT_DIR/examples/train_lora/qwen3_0910_only_qwen3_data_009.yaml"

# 允许通过参数覆盖配置文件
if [ ! -z "$1" ] && [ -f "$1" ]; then
    CONFIG_FILE="$1"
    echo "使用自定义配置文件: $CONFIG_FILE"
else
    echo "使用默认配置文件: $CONFIG_FILE"
    echo "说明: template 和 enable_thinking 已注释，将使用 Qwen3 模型自带的 tokenizer_config.json"
fi

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# ========================================
# 3. 创建输出目录
# ========================================

lora_rank=$(grep -m1 '^lora_rank:' "$CONFIG_FILE" | awk '{print $2}')
learning_rate=$(grep -m1 '^learning_rate:' "$CONFIG_FILE" | awk '{print $2}')
num_train_epochs=$(grep -m1 '^num_train_epochs:' "$CONFIG_FILE" | awk '{print $2}')
output_dir=$(grep -m1 '^output_dir:' "$CONFIG_FILE" | awk '{print $2}') # 这个是/nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/sft_output/Qwen3-8B_lora/train_with_generation
per_device_train_batch_size=$(grep -m1 '^per_device_train_batch_size:' "$CONFIG_FILE" | awk '{print $2}')
gradient_accumulation_steps=$(grep -m1 '^gradient_accumulation_steps:' "$CONFIG_FILE" | awk '{print $2}')
RUN_NAME="rank=${lora_rank}_lr=${learning_rate}_epochs=${num_train_epochs}_bs=${per_device_train_batch_size}_gc=${gradient_accumulation_steps}_not_inference"
# OUTPUT_DIR="${output_dir}_${RUN_NAME}_${TIMESTAMP}"
OUTPUT_DIR="${output_dir}/${RUN_NAME}_${TIMESTAMP}"

echo "输出目录: $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

export WANDB_PROJECT="qwen3_lora_new_0910"
export WANDB_NAME="$RUN_NAME"

FINAL_YAML="$OUTPUT_DIR/config.yaml"
# 2. 一次性把 yaml 里的 output_dir 整行换掉
sed \
  -e "s|^output_dir:.*|output_dir: ${OUTPUT_DIR}|g" \
  "$CONFIG_FILE" > "$FINAL_YAML"

# ========================================
# 4. 检测实际使用的 Template
# ========================================
echo ""
echo "🔍 检测实际使用的 Chat Template..."
echo ""

# 运行检测脚本
if [ -f "$SCRIPT_DIR/detect_template.py" ]; then
    python "$SCRIPT_DIR/detect_template.py" "$CONFIG_FILE"
    echo ""
    echo "提示: 以上为 Template 检测结果，请确认是否符合预期"
    read -p "按 Enter 继续训练，或按 Ctrl+C 取消... "
else
    echo "⚠️ 检测脚本不存在，跳过 template 检测"
fi

# ========================================
# 5. 启动训练
# ========================================
echo ""
echo "========================================" 
echo "开始训练 Qwen3-8B-Thinking LoRA"
echo "配置文件: $CONFIG_FILE"
echo "输出目录: $OUTPUT_DIR"
echo "样本生成: 启用（查看训练日志观察生成样本）"
echo "========================================" 
echo ""

# 使用 llamafactory-cli 启动训练
llamafactory-cli train "$FINAL_YAML" 2>&1 | tee "$OUTPUT_DIR/training.log"


# ========================================
# 5. 训练完成后处理
# ========================================
echo ""
echo "========================================" 
echo "训练完成！"
echo "模型保存在: $OUTPUT_DIR"
echo "生成样本保存在: $OUTPUT_DIR/generation_samples*.jsonl"
echo "训练日志: $OUTPUT_DIR/training.log"
echo "========================================" 

# 显示生成样本统计（如果存在）
if ls "$OUTPUT_DIR"/generation_samples*.jsonl 1> /dev/null 2>&1; then
    echo ""
    echo "生成样本统计："
    for file in "$OUTPUT_DIR"/generation_samples*.jsonl; do
        line_count=$(wc -l < "$file")
        echo "  - $(basename "$file"): $line_count 条记录"
    done
fi
