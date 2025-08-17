#!/bin/bash

# =============================================================================
# VERL训练数据生成脚本 - 完全硬编码配置版本
# =============================================================================
#
# 使用说明:
#   1. 直接修改下面的硬编码配置
#   2. 运行: bash generate_data.sh 
#   3. 脚本会自动验证数据集并调整test_cases数目
#
# 功能:
#   - 完全硬编码配置，无需命令行参数
#   - 自动验证benchmark_mapping.jsonl中的数据集
#   - 保护性检查: 自动读取数据文件行数，确保test_cases不超限
#   - 同时生成parquet和jsonl两种格式
#
# =============================================================================

# =============================================================================
# 硬编码配置区域 - 直接修改这里的参数
# =============================================================================

# 选择的数据集 (空格分隔，必须在benchmark_mapping.jsonl中存在)
HARDCODED_BENCHMARKS="mbpp"

# 每条数据随机选择的test_cases数目
HARDCODED_TEST_CASES_PER_ENTRY=4

# 其他参数
HARDCODED_NUM_TRAIN_ENTRIES=1 #""        # 留空使用全部训练数据
HARDCODED_NUM_TEST_ENTRIES=1         # 生成的测试条目数
HARDCODED_DATASET_TYPE="both"         # train, test, both
HARDCODED_SAVE_INDIVIDUAL=false        # 是否保存单独的基准测试文件

# =============================================================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "VERL训练数据生成启动 (硬编码配置版本)"
echo "=========================================="

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NEW_EVAL_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"  # New_evaluation_and_RL目录
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"  # Flow_RL目录

echo "📁 脚本目录: $SCRIPT_DIR"
echo "📁 项目根目录: $PROJECT_ROOT"

# 设置环境变量
echo "🔧 设置环境变量..."

# 激活conda环境
echo "🐍 激活conda环境 workflow..."
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate workflow

echo "✅ 当前conda环境: $CONDA_DEFAULT_ENV"

# 设置Python无缓冲输出
export PYTHONUNBUFFERED=1

# 设置输出目录
OUTPUT_DIR="$NEW_EVAL_ROOT/parquet_and_jsonl_data/single"

# 检查并创建输出目录
echo "📂 检查输出目录: $OUTPUT_DIR"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "📂 创建输出目录..."
    mkdir -p "$OUTPUT_DIR"
fi

echo "📂 输出目录已准备: $OUTPUT_DIR"

# 检查必需文件
echo "🔍 检查必需文件..."

CONFIG_FILE="$NEW_EVAL_ROOT/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi
echo "✅ 配置文件: $CONFIG_FILE"

SCRIPT_FILE="$SCRIPT_DIR/generate_verl_training_data.py"
if [ ! -f "$SCRIPT_FILE" ]; then
    echo "❌ 错误: 生成脚本不存在: $SCRIPT_FILE"
    exit 1
fi
echo "✅ 生成脚本: $SCRIPT_FILE"

# 使用硬编码参数
BENCHMARKS="$HARDCODED_BENCHMARKS"
NUM_TRAIN_ENTRIES="$HARDCODED_NUM_TRAIN_ENTRIES"
NUM_TEST_ENTRIES="$HARDCODED_NUM_TEST_ENTRIES"
DATASET_TYPE="$HARDCODED_DATASET_TYPE"
TEST_CASES_PER_ENTRY="$HARDCODED_TEST_CASES_PER_ENTRY"
SAVE_INDIVIDUAL="$HARDCODED_SAVE_INDIVIDUAL"

echo ""
echo "🎯 硬编码配置参数:"
echo "   基准测试: $BENCHMARKS"
echo "   数据集类型: $DATASET_TYPE"
echo "   测试案例数: $TEST_CASES_PER_ENTRY"
if [ -n "$NUM_TRAIN_ENTRIES" ]; then
    echo "   训练条目数: $NUM_TRAIN_ENTRIES"
else
    echo "   训练条目数: 全部"
fi
echo "   测试条目数: $NUM_TEST_ENTRIES"
echo "   保存单独文件: $SAVE_INDIVIDUAL"
echo "   输出目录: $OUTPUT_DIR"
echo ""

# =============================================================================
# 数据集验证和保护性检查
# =============================================================================

echo "🔍 数据集验证和test_cases保护性检查..."

# 读取benchmark_mapping.jsonl并验证数据集
MAPPING_FILE="$PROJECT_ROOT/ScoreFlow/benchmark_mapping.jsonl"
if [ ! -f "$MAPPING_FILE" ]; then
    echo "❌ 错误: benchmark_mapping.jsonl文件不存在: $MAPPING_FILE"
    exit 1
fi

# 验证每个基准测试并检查数据集大小
for benchmark in $BENCHMARKS; do
    echo "📊 检查基准测试: $benchmark"
    
    # 从mapping文件中提取数据路径
    train_path=$(grep "\"benchmark\": \"$benchmark\"" "$MAPPING_FILE" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    print(data.get('data_train_dir', ''))
except:
    pass
")
    
    test_path=$(grep "\"benchmark\": \"$benchmark\"" "$MAPPING_FILE" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    print(data.get('data_test_dir', ''))
except:
    pass
")
    
    if [ -z "$train_path" ] && [ -z "$test_path" ]; then
        echo "❌ 错误: 在mapping文件中找不到基准测试 '$benchmark'"
        exit 1
    fi
    
    # 检查训练数据文件
    if [ -n "$train_path" ] && [ -f "$train_path" ]; then
        train_lines=$(wc -l < "$train_path" 2>/dev/null || echo "0")
        echo "   📈 训练数据: $train_lines 行 ($train_path)"
        
        if [ "$train_lines" -lt "$TEST_CASES_PER_ENTRY" ]; then
            echo "⚠️  警告: $benchmark 训练数据只有 $train_lines 行，少于所需的 test_cases=$TEST_CASES_PER_ENTRY"
            # 调整test_cases数目
            if [ "$train_lines" -gt 1 ]; then
                ADJUSTED_TEST_CASES=$((train_lines - 1))
                echo "   🔧 自动调整 test_cases 为 $ADJUSTED_TEST_CASES"
                TEST_CASES_PER_ENTRY=$ADJUSTED_TEST_CASES
            else
                echo "❌ 错误: $benchmark 训练数据不足，无法生成test_cases"
                exit 1
            fi
        fi
    fi
    
    # 检查测试数据文件
    if [ -n "$test_path" ] && [ -f "$test_path" ]; then
        test_lines=$(wc -l < "$test_path" 2>/dev/null || echo "0")
        echo "   📊 测试数据: $test_lines 行 ($test_path)"
        
        if [ "$test_lines" -lt "$TEST_CASES_PER_ENTRY" ]; then
            echo "⚠️  警告: $benchmark 测试数据只有 $test_lines 行，少于所需的 test_cases=$TEST_CASES_PER_ENTRY"
            # 调整test_cases数目
            if [ "$test_lines" -gt 1 ]; then
                ADJUSTED_TEST_CASES=$((test_lines - 1))
                echo "   🔧 自动调整 test_cases 为 $ADJUSTED_TEST_CASES"
                TEST_CASES_PER_ENTRY=$ADJUSTED_TEST_CASES
            else
                echo "❌ 错误: $benchmark 测试数据不足，无法生成test_cases"
                exit 1
            fi
        fi
    fi
    
    echo "   ✅ $benchmark 验证通过"
done

echo "✅ 所有数据集验证通过"
echo "🔧 最终 test_cases_per_entry: $TEST_CASES_PER_ENTRY"
echo ""

# =============================================================================
# 构建并执行Python命令
# =============================================================================

# 构建Python命令
PYTHON_CMD="python $SCRIPT_FILE"
PYTHON_CMD="$PYTHON_CMD --benchmarks $BENCHMARKS"
PYTHON_CMD="$PYTHON_CMD --dataset-type $DATASET_TYPE"
PYTHON_CMD="$PYTHON_CMD --output-dir $OUTPUT_DIR"
PYTHON_CMD="$PYTHON_CMD --test-cases-per-entry $TEST_CASES_PER_ENTRY"

if [ -n "$NUM_TRAIN_ENTRIES" ]; then
    PYTHON_CMD="$PYTHON_CMD --num-train-entries $NUM_TRAIN_ENTRIES"
fi

PYTHON_CMD="$PYTHON_CMD --num-test-entries $NUM_TEST_ENTRIES"

if [ "$SAVE_INDIVIDUAL" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --save-individual"
fi

echo "🚀 开始生成数据..."
echo "📝 执行命令: $PYTHON_CMD"
echo ""

# 切换到脚本目录执行
cd "$SCRIPT_DIR"

# 执行Python脚本
if eval "$PYTHON_CMD"; then
    echo ""
    echo "=========================================="
    echo "✅ 数据生成完成！"
    echo "=========================================="
    echo "📂 输出目录: $OUTPUT_DIR"
    echo "📊 查看生成的文件:"
    if [ -d "$OUTPUT_DIR" ]; then
        ls -la "$OUTPUT_DIR"
    fi
    echo ""
    echo "🎯 硬编码配置总结:"
    echo "   选择的基准测试: $HARDCODED_BENCHMARKS"
    echo "   生成的测试条目: $HARDCODED_NUM_TEST_ENTRIES"
    echo "   实际test_cases: $TEST_CASES_PER_ENTRY"
    echo "   保存格式: parquet + jsonl"
    echo "   保存单独文件: $HARDCODED_SAVE_INDIVIDUAL"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ 数据生成失败！"
    echo "=========================================="
    echo "请检查错误信息并重试"
    echo "可能需要修改脚本开头的硬编码配置参数"
    exit 1
fi