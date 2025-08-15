#!/bin/bash

# SGLang 直接测试脚本
# 用于诊断SGLang启动问题

echo "======================================"
echo "SGLang 直接启动测试"
echo "======================================"

# 配置参数
MODEL_PATH="/nas/ganluo/sft_output/Qwen2.5-7B-workflow-sft_new/checkpoint-200"
PORT=30000

echo "模型路径: $MODEL_PATH"
echo "端口: $PORT"
echo ""

# 检查模型路径
if [ ! -d "$MODEL_PATH" ]; then
    echo "❌ 错误: 模型路径不存在: $MODEL_PATH"
    exit 1
fi

echo "✓ 模型路径存在"
echo ""

# 检查GPU
echo "GPU状态:"
nvidia-smi --query-gpu=index,name,memory.free,memory.total --format=csv
echo ""

# 检查端口
echo "检查端口 $PORT..."
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠ 警告: 端口 $PORT 已被占用"
    echo "占用进程:"
    lsof -i :$PORT
    echo ""
    read -p "是否终止占用进程? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -9 $(lsof -t -i:$PORT)
        echo "✓ 已终止占用进程"
    fi
else
    echo "✓ 端口 $PORT 可用"
fi
echo ""

# 检查SGLang安装
echo "检查SGLang安装..."
if python -c "import sglang" 2>/dev/null; then
    echo "✓ SGLang已安装"
    echo "版本信息:"
    pip show sglang | grep -E "Name:|Version:"
else
    echo "❌ SGLang未安装"
    echo "请运行: pip install sglang"
    exit 1
fi
echo ""

# 构建启动命令
CMD="python -m sglang.launch_server \
    --model-path $MODEL_PATH \
    --port $PORT \
    --tp 1 \
    --mem-fraction-static 0.85"

echo "将执行的命令:"
echo "$CMD"
echo ""
echo "======================================"
echo "开始启动SGLang服务器..."
echo "======================================"
echo ""
echo "提示: 按 Ctrl+C 停止服务器"
echo ""

# 执行命令
$CMD