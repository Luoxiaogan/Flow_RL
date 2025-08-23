#!/bin/bash

# 测试命令生成和显示功能
# 这个脚本只测试参数生成和命令构建，不实际执行训练

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}     测试命令生成功能${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# 获取脚本路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="${SCRIPT_DIR}/../config.yaml"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 使用配置文件: $CONFIG_FILE${NC}"
echo ""

# 生成训练参数
echo -e "${BLUE}📝 生成训练参数...${NC}"
TRAINING_PARAMS=$(python3 "$SCRIPT_DIR/generate_training_params.py" "$CONFIG_FILE" 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 参数生成失败${NC}"
    echo "$TRAINING_PARAMS"
    exit 1
fi

# 显示生成的参数
echo -e "${GREEN}✅ 成功生成参数${NC}"
echo -e "${CYAN}参数列表：${NC}"
echo "----------------------------------------"
echo "$TRAINING_PARAMS" | nl -ba
echo "----------------------------------------"
PARAM_COUNT=$(echo "$TRAINING_PARAMS" | wc -l)
echo -e "${GREEN}总计: $PARAM_COUNT 个参数${NC}"
echo ""

# 测试命令构建
echo -e "${BLUE}📦 构建命令...${NC}"

# 模拟VERL主脚本路径
VERL_MAIN_SCRIPT="/nas/ganluo/Flow_RL/verl/verl/trainer/main_ppo.py"

# 将参数读入数组
IFS=$'\n' read -rd '' -a PARAMS <<< "$TRAINING_PARAMS"

# 显示构建的命令
echo -e "${CYAN}构建的完整命令：${NC}"
echo "----------------------------------------"
echo "python $VERL_MAIN_SCRIPT \\"
echo "  --config-path=config \\"
echo "  --config-name=ppo_trainer.yaml \\"

for raw in "${PARAMS[@]}"; do
    if [[ -z "$raw" ]]; then
        continue
    fi
    
    if [[ $raw == \$\$LIST\$\$* && $raw == *\$\$LIST\$\$ ]]; then
        param="${raw#\$\$LIST\$\$}"
        param="${param%\$\$LIST\$\$}"
        echo "  '$param' \\"
    else
        echo "  $raw \\"
    fi
done

echo "----------------------------------------"
echo ""

# 构建单行命令
echo -e "${BLUE}单行命令格式：${NC}"
echo "----------------------------------------"
FULL_CMD="python $VERL_MAIN_SCRIPT --config-path=config --config-name=ppo_trainer.yaml"

for raw in "${PARAMS[@]}"; do
    if [[ -z "$raw" ]]; then
        continue
    fi
    
    if [[ $raw == \$\$LIST\$\$* && $raw == *\$\$LIST\$\$ ]]; then
        param="${raw#\$\$LIST\$\$}"
        param="${param%\$\$LIST\$\$}"
        FULL_CMD="$FULL_CMD '$param'"
    else
        FULL_CMD="$FULL_CMD $raw"
    fi
done

echo "$FULL_CMD"
echo "----------------------------------------"
echo ""

echo -e "${GREEN}✅ 测试完成${NC}"
echo -e "${YELLOW}提示: 这只是测试脚本，不会实际执行训练命令${NC}"