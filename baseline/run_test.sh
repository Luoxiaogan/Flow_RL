#!/bin/bash
# Script to run CoT vs Self-Consistency evaluation

echo "========================================"
echo "  CoT vs Self-Consistency Evaluation"
echo "========================================"
echo ""

# Check if reward server is accessible
echo "检查 Reward Server 状态..."
if curl -s http://localhost:8899/health > /dev/null 2>&1; then
    echo "✓ Reward Server 运行正常"
else
    echo "❌ 无法连接到 Reward Server"
    echo "请先启动 Reward Server:"
    echo "  cd ../New_evaluation_and_RL/reward_server"
    echo "  python scoreflow_reward_server.py"
    exit 1
fi

echo ""
echo "开始评估..."
echo "----------------------------------------"

# Run the evaluation
python test_workflows.py

echo ""
echo "评估完成! 结果已保存在 ./results/ 目录"