#!/bin/bash

# 测试 Template 检测功能

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🧪 测试 Template 检测功能"
echo "=" * 70
echo ""

# 默认配置文件
CONFIG_FILE="$SCRIPT_DIR/examples/train_lora/qwen3_thinking_lora_with_generation.yaml"

if [ ! -z "$1" ]; then
    CONFIG_FILE="$1"
fi

echo "配置文件: $CONFIG_FILE"
echo ""

# 运行检测
python "$SCRIPT_DIR/detect_template.py" "$CONFIG_FILE"