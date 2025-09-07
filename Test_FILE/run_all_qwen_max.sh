#!/bin/bash

# 设置错误处理
set -e  # 遇到错误时立即退出
set -u  # 使用未定义变量时报错

echo "开始执行所有测试..."

echo "执行 MBPP 数据合成..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_mbpp_max.sh

echo "执行 HUMANEVAL 测试..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_humaneval_max.sh

echo "执行 HOTPOTQA 测试..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_hotpotqa_max.sh

echo "执行 DROP 测试..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_drop.sh

echo "执行 GSM8K 测试..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_gsm8k.sh

echo "所有测试执行完成！"