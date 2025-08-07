#!/bin/bash
# 训练 Qwen
sed -i 's/MODEL_TYPE=".*"/MODEL_TYPE="qwen"/' run_finetune.sh
bash run_finetune.sh