#!/bin/bash

# API代理启动脚本 - 支持速率限制和进度显示

# 清除代理设置，避免干扰
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY来排除localhost（即使Clash开启系统代理也有效）
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo "✓ 已设置NO_PROXY='$NO_PROXY'"
echo "  localhost请求将绕过所有代理"

# 设置Python无缓冲输出，确保实时看到print内容
export PYTHONUNBUFFERED=1

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查配置文件
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

echo "=========================================="
echo "启动 MetaGPT API 代理服务"
echo "=========================================="

# 从配置文件读取配置
PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo "5009")
DEBUG=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(str(c['services']['metagpt_api_proxy'].get('debug', False)).lower())" 2>/dev/null || echo "false")
RATE=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['metagpt_api_proxy'].get('rate_per_second', 1.0))" 2>/dev/null || echo "1.0")

# 检查端口是否被占用
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "端口 $PORT 已被占用，正在终止现有进程..."
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null
    sleep 1
fi

# 创建日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/api_proxy_$(date +%Y%m%d_%H%M%S).log"

echo "配置文件: $CONFIG_FILE"
echo "日志文件: $LOG_FILE"
echo ""
echo "服务配置:"
echo "  - 端口: $PORT"
echo "  - 速率限制: $RATE req/s"
if [ "$DEBUG" = "true" ]; then
    echo "  - 模式: 调试模式 (显示详细信息)"
else
    echo "  - 模式: 正常模式 (仅显示进度条和错误)"
fi
echo ""
echo "正在启动代理服务器..."
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

# 启动代理服务（使用-u选项禁用缓冲，确保实时输出）
cd "${PROJECT_ROOT}/metagpt_api_key_proxy"
python3 -u api_key_proxy_enhanced.py 2>&1 | tee "$LOG_FILE"