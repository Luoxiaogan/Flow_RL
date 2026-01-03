#!/bin/bash
# https://www.modelscope.cn/models/  
# 找到对应模型 入参为两层路径的模型名称 文件自动下载到../models/目录中
# 检查是否提供了参数
if [ "$#" -ne 1 ]; then
    echo "Usage: \$0 <model_name>"
    exit 1
fi

# 接收参数
MODEL_NAME="$1"

# 生成 local_dir 路径
LEAF_DIR=$(basename "$MODEL_NAME")
LOCAL_DIR="$LEAF_DIR"

# 输出路径
echo "Model Name: $MODEL_NAME"
echo "Local Directory: $LOCAL_DIR"

modelscope download --model "$MODEL_NAME" --local_dir "$LOCAL_DIR"