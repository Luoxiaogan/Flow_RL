#!/bin/bash

# 测试 JSONL 转 Python 文件的脚本

echo "🧪 测试 JSONL 到 Python 文件转换"
echo "=================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 查找 JSONL 文件
JSONL_FILE=$(ls *generation_samples*.jsonl 2>/dev/null | head -1)

if [ -z "$JSONL_FILE" ]; then
    echo "❌ 未找到 generation_samples 文件"
    echo "请确保当前目录有生成样本文件"
    exit 1
fi

echo "📁 找到文件: $JSONL_FILE"

# 创建输出目录
OUTPUT_DIR="rank_8"
mkdir -p "$OUTPUT_DIR"

echo "📂 输出目录: $OUTPUT_DIR/"

# 先预览文件结构
echo ""
echo "🔍 预览文件结构..."
python jsonl_to_python_files.py "$JSONL_FILE" "$OUTPUT_DIR" -p

echo ""
read -p "是否继续转换为 Python 文件? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 开始转换..."
    python jsonl_to_python_files.py "$JSONL_FILE" "$OUTPUT_DIR"
    
    echo ""
    echo "📊 转换结果:"
    echo "  - 生成的文件数: $(ls $OUTPUT_DIR/*.py 2>/dev/null | wc -l)"
    echo "  - 目录大小: $(du -sh $OUTPUT_DIR 2>/dev/null | cut -f1)"
    
    echo ""
    echo "🔎 查看生成的文件:"
    ls -la "$OUTPUT_DIR/" | head -10
    
    if [ $(ls $OUTPUT_DIR/*.py 2>/dev/null | wc -l) -gt 0 ]; then
        FIRST_FILE=$(ls $OUTPUT_DIR/*.py | head -1)
        echo ""
        echo "📝 第一个文件内容预览 ($FIRST_FILE):"
        echo "----------------------------------------"
        head -20 "$FIRST_FILE"
        echo "----------------------------------------"
        echo "(只显示前20行)"
    fi
else
    echo "取消转换"
fi