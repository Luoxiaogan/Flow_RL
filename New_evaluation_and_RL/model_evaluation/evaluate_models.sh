#!/bin/bash

# Batch Model Evaluation Script

echo "=========================================="
echo "批量模型评估脚本"
echo "=========================================="

# Set environment
export PYTHONPATH="${PYTHONPATH}:$(dirname $(dirname $(realpath $0)))"

# Activate conda environment
echo "激活 conda 环境..."
source /opt/anaconda3/etc/profile.d/conda.sh && conda activate workflow

# Check if reward server is running
echo "检查 Reward Server..."
curl -s http://localhost:8899/health > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Reward Server 未运行"
    echo "请先启动 Reward Server:"
    echo "  bash ../servers_and_proxy/start_scoreflow_reward.sh"
    echo ""
    read -p "是否继续? (可能会失败) [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ Reward Server 正常运行"
fi

# Parse arguments
CONFIG_FILE="evaluation_config.yaml"
MAX_SAMPLES=""
OUTPUT_DIR=""
BATCH_SIZE=""
YES_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -n|--max-samples)
            MAX_SAMPLES="--max-samples $2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="--output-dir $2"
            shift 2
            ;;
        -b|--batch-size)
            BATCH_SIZE="--batch-size $2"
            shift 2
            ;;
        -y|--yes)
            YES_FLAG="--yes"
            shift
            ;;
        -h|--help)
            echo "使用方法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  -c, --config FILE      配置文件 (默认: evaluation_config.yaml)"
            echo "  -n, --max-samples N    最大评估样本数"
            echo "  -o, --output-dir DIR   输出目录"
            echo "  -b, --batch-size N     批处理大小"
            echo "  -y, --yes              跳过确认提示"
            echo "  -h, --help             显示帮助信息"
            echo ""
            echo "示例:"
            echo "  # 使用默认配置评估所有模型"
            echo "  $0"
            echo ""
            echo "  # 快速测试 (10个样本)"
            echo "  $0 -n 10 -y"
            echo ""
            echo "  # 使用自定义配置"
            echo "  $0 -c my_config.yaml -o my_results/"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 -h 查看帮助"
            exit 1
            ;;
    esac
done

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

echo ""
echo "配置文件: $CONFIG_FILE"
if [ -n "$MAX_SAMPLES" ]; then
    echo "最大样本数: $(echo $MAX_SAMPLES | cut -d' ' -f2)"
fi
if [ -n "$OUTPUT_DIR" ]; then
    echo "输出目录: $(echo $OUTPUT_DIR | cut -d' ' -f2)"
fi
echo ""

# Run evaluation
python run_evaluation.py \
    --config "$CONFIG_FILE" \
    $MAX_SAMPLES \
    $OUTPUT_DIR \
    $BATCH_SIZE \
    $YES_FLAG \
    --log-level INFO

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 评估完成!"
else
    echo ""
    echo "✗ 评估失败!"
    exit 1
fi