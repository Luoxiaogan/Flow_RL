#!/bin/bash
# 训练 Llama
sed -i 's/MODEL_TYPE=".*"/MODEL_TYPE="llama"/' run_finetune.sh
bash run_finetune.sh