#!/bin/bash

# Unified Model Evaluation Script
# 统一的模型评估脚本 - 支持本地模型和API模型

echo "=========================================="
echo "统一模型评估脚本"
echo "Unified Model Evaluation Script"
echo "=========================================="

# Set environment
export PYTHONPATH="${PYTHONPATH}:$(dirname $(dirname $(realpath $0)))"

# Activate conda environment
echo "激活 conda 环境..."
source /opt/anaconda3/etc/profile.d/conda.sh && conda activate workflow

# Check Python packages
echo "检查依赖包..."
python -c "import torch; import transformers; import aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少必要的Python包"
    echo "请安装: pip install torch transformers aiohttp peft bitsandbytes"
fi

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
CONFIG_FILE="models_config.yaml"
MAX_SAMPLES=""
OUTPUT_DIR=""
BATCH_SIZE=""
FILTER=""
LIMIT=""
YES_FLAG=""

# Function to show help
show_help() {
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -c, --config FILE      模型配置文件 (默认: models_config.yaml)"
    echo "  -n, --max-samples N    最大评估样本数"
    echo "  -o, --output-dir DIR   输出目录"
    echo "  -b, --batch-size N     批处理大小"
    echo "  -f, --filter TYPE      过滤模型类型 (api/local/等)"
    echo "  -l, --limit N          限制评估模型数量"
    echo "  -y, --yes              跳过确认提示"
    echo "  -h, --help             显示帮助信息"
    echo ""
    echo "示例:"
    echo "  # 评估所有配置的模型"
    echo "  $0"
    echo ""
    echo "  # 快速测试 (10个样本，前3个模型)"
    echo "  $0 -n 10 -l 3 -y"
    echo ""
    echo "  # 仅评估API模型"
    echo "  $0 -f api"
    echo ""
    echo "  # 仅评估本地模型"
    echo "  $0 -f local"
    echo ""
    echo "  # 使用自定义配置"
    echo "  $0 -c my_models.yaml -o results/"
    echo ""
}

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
        -f|--filter)
            FILTER="--filter $2"
            shift 2
            ;;
        -l|--limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        -y|--yes)
            YES_FLAG="--yes"
            shift
            ;;
        -h|--help)
            show_help
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
    echo ""
    echo "可用的配置文件:"
    ls -1 *.yaml 2>/dev/null | sed 's/^/  - /'
    echo ""
    echo "请创建配置文件或使用 -c 指定现有文件"
    exit 1
fi

echo ""
echo "配置信息:"
echo "  配置文件: $CONFIG_FILE"
if [ -n "$MAX_SAMPLES" ]; then
    echo "  最大样本数: $(echo $MAX_SAMPLES | cut -d' ' -f2)"
fi
if [ -n "$FILTER" ]; then
    echo "  模型过滤: $(echo $FILTER | cut -d' ' -f2)"
fi
if [ -n "$LIMIT" ]; then
    echo "  模型限制: $(echo $LIMIT | cut -d' ' -f2)"
fi
if [ -n "$OUTPUT_DIR" ]; then
    echo "  输出目录: $(echo $OUTPUT_DIR | cut -d' ' -f2)"
fi
echo ""

# Count models in config
echo "分析配置文件..."
python -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
    models = config.get('models', [])
    api_models = [m for m in models if m.get('type') == 'api']
    local_models = [m for m in models if m.get('type') != 'api']
    print(f'  配置的模型总数: {len(models)}')
    print(f'    - API模型: {len(api_models)}')
    print(f'    - 本地模型: {len(local_models)}')
"

echo ""

# Run evaluation
python run_unified_evaluation.py \
    --config "$CONFIG_FILE" \
    $MAX_SAMPLES \
    $OUTPUT_DIR \
    $BATCH_SIZE \
    $FILTER \
    $LIMIT \
    $YES_FLAG \
    --log-level INFO

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ 评估成功完成!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "✗ 评估过程出错 (退出码: $EXIT_CODE)"
    echo "=========================================="
    exit $EXIT_CODE
fi