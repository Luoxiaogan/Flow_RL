#!/bin/bash

# 简化版本的RL训练启动脚本
# 直接构建和执行命令，最少的包装

# 颜色定义
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}     VERL RL训练 - 简化版${NC}"
echo -e "${CYAN}============================================${NC}"

# 配置路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="${SCRIPT_DIR}/../config.yaml"

# 生成参数
echo "生成训练参数..."
TRAINING_PARAMS=$(python3 "$SCRIPT_DIR/generate_training_params.py" "$CONFIG_FILE" 2>&1)

if [ $? -ne 0 ]; then
    echo "参数生成失败"
    exit 1
fi

# 获取VERL脚本路径
VERL_MAIN_SCRIPT=$(python3 -c "
from pathlib import Path
project_root = Path('$SCRIPT_DIR').parent.parent
verl_main = project_root / 'verl' / 'verl' / 'trainer' / 'main_ppo.py'
print(verl_main)
" 2>/dev/null)

# 直接构建命令字符串
CMD="python $VERL_MAIN_SCRIPT --config-path=config --config-name=ppo_trainer.yaml"

# 处理参数
while IFS= read -r param; do
    if [[ -z "$param" ]]; then
        continue
    fi
    
    # 处理$$LIST$$标记
    if [[ $param == *"$$LIST$$"* ]]; then
        # 去掉标记
        clean_param="${param//\$\$LIST\$\$/}"
        CMD="$CMD '$clean_param'"
    else
        CMD="$CMD $param"
    fi
done <<< "$TRAINING_PARAMS"

# 显示命令
echo -e "${GREEN}执行命令：${NC}"
echo "$CMD"
echo ""

# 设置环境变量
export USE_SGLANG=1
export NCCL_DEBUG=INFO
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# 执行命令
echo "开始执行..."
echo "=========================================="

# 使用exec替换当前shell，确保所有输出都显示
exec bash -c "$CMD"