#!/bin/bash

# 快速启动脚本 - 使用默认配置
echo "🚀 快速启动 Qwen3-Thinking LoRA 训练（带实时监控）"

# 激活 conda 环境
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate workflow

# 运行训练
bash lora_simp_e.sh