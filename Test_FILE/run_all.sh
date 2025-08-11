#!/bin/bash

# 设置错误处理
set -e  # 遇到错误时立即退出
set -u  # 使用未定义变量时报错

echo "开始执行所有测试..."

echo "执行 MILR 测试..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_limr.sh

echo "执行 DROP 测试..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_drop.sh

echo "执行 GSM8K 测试..."
bash /nas/ganluo/Flow_RL/Test_FILE/run_workflow_system_gsm8k.sh

echo "所有测试执行完成！"