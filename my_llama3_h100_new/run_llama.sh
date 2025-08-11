#!/bin/bash
# 训练 Llama

# 可选: 启用损失掩码 (取消注释下一行)
# export USE_LOSS_MASK_OVERRIDE=true

# 设置模型类型为 Llama
sed -i 's/MODEL_TYPE=".*"/MODEL_TYPE="llama"/' run_finetune.sh

# 如果设置了 USE_LOSS_MASK_OVERRIDE，更新配置
if [ ! -z "$USE_LOSS_MASK_OVERRIDE" ]; then
    sed -i "s/USE_LOSS_MASK=.*/USE_LOSS_MASK=$USE_LOSS_MASK_OVERRIDE/" run_finetune.sh
fi

bash run_finetune.sh